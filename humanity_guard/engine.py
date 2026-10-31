"""Guardian engine: sense -> verify -> refuse -> human gate -> act.

One event, in order:
  1. SENSE twice (two independent looks at the same scene kind).
  2. VERIFY: commit p1 from the first look's coherence, revise to p2
     from the second look, score both with Brier (exactly two forecasts).
  3. REFUSE: the frozen gate judges the mean coherence. On refusal the
     event ends: no classification, no request, no action.
  4. HUMAN GATE: on acceptance the engine opens an "alert" request.
     Nothing is actuated until a human approves it through HumanGate.
  5. ACT (only via HumanGate.execute): "alert" is performed on approval.
     A "decoy" request is opened only when the caller explicitly asks
     for one, and it needs two distinct approvers.

No step in this engine can actuate anything on its own. There is no
lethal action in the action set at all: the only actions are "alert"
and "decoy" (a projected holographic pattern, simulated here as a
recorded pattern id, not a physical projector).
"""

from __future__ import annotations

import numpy as np

from .humangate import HumanGate
from .refusal import RefusalGate, calibrate_threshold
from .sensing import coherence, generate_scene, sharpness
from .verify import clamp_p, score_event


def calibrate_gate(rng: np.random.Generator, n_per_kind: int = 60):
    """Calibrate the refusal threshold on synthetic training scenes."""
    real_scores = []
    other_scores = []
    for _ in range(n_per_kind):
        for kind in ("real",):
            amp, ph = generate_scene(rng, kind)
            real_scores.append(coherence(amp, ph))
        for kind in ("decoy", "glare", "noise"):
            amp, ph = generate_scene(rng, kind)
            other_scores.append(coherence(amp, ph))
    tau, youden_j = calibrate_threshold(real_scores, other_scores)
    return tau, youden_j


class GuardianEngine:
    """Defensive sensing engine with a human gate. Synthetic only."""

    def __init__(self, seed: int = 42, tau: float | None = None):
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        if tau is None:
            tau, youden_j = calibrate_gate(self.rng)
            self.calibration_youden_j = youden_j
        else:
            self.calibration_youden_j = None
        self.gate = RefusalGate(tau)
        self.human_gate = HumanGate()
        self.events: list[dict] = []

    def process(self, kind: str) -> dict:
        """Process one scene. Returns the full event record."""
        amp1, ph1 = generate_scene(self.rng, kind)
        amp2, ph2 = generate_scene(self.rng, kind)
        coh1 = coherence(amp1, ph1)
        coh2 = coherence(amp2, ph2)
        mean_coh = (coh1 + coh2) / 2.0
        p1 = clamp_p(coh1)
        p2 = clamp_p(coh2)
        truth = kind == "real"
        score = score_event(p1, p2, truth, n_looks=2)
        decision = self.gate.decide(mean_coh, is_real=truth)
        event = {
            "kind": kind,
            "coherence_look1": coh1,
            "coherence_look2": coh2,
            "mean_coherence": mean_coh,
            "sharpness_look1": sharpness(amp1),
            "commit_p1": p1,
            "commit_p2": p2,
            "score": score["score"],
            "decision": decision,
            "request_id": None,
        }
        if decision == "accepted":
            event["request_id"] = self.human_gate.request(
                "alert", detail=f"accepted scene kind={kind} coherence={mean_coh:.3f}"
            )
        self.events.append(event)
        return event

    def request_decoy(self, event: dict) -> str:
        """Open a decoy request for an accepted event. Needs 2 approvers."""
        if event["decision"] != "accepted":
            raise ValueError("decoy requires an accepted event")
        return self.human_gate.request(
            "decoy", detail=f"decoy for coherence={event['mean_coherence']:.3f}"
        )

    def summary(self) -> dict:
        """Aggregate statistics over processed events."""
        n = len(self.events)
        accepted = [e for e in self.events if e["decision"] == "accepted"]
        refused = [e for e in self.events if e["decision"] == "refused"]
        return {
            "events": n,
            "accepted": len(accepted),
            "refused": len(refused),
            "accuracy_on_accepted": self.gate.accuracy_on_accepted,
            "mean_score": float(np.mean([e["score"] for e in self.events])) if n else 0.0,
            "tau": self.gate.tau,
            "calibration_youden_j": self.calibration_youden_j,
            "ledger_valid": self.human_gate.verify_chain(),
            "ledger_entries": len(self.human_gate.ledger),
        }
