# DESIGN.md — Humanity Guard v0.1.0

## Falsified designs (tried in reasoning, rejected)

1. **Sharpness-only detection.** A decoy with a few bright modes has
   higher amplitude variance than a real scene. Any detector trusting
   sharpness accepts decoys. Falsified by construction: decoys are
   generated exactly this way, and the coherence gate refuses them.
2. **Single-look decisions.** One noisy look misjudges borderline
   scenes. The two-look commit/replicate/revise loop exists because a
   single look cannot carry a probability honestly.
3. **Auto-actuation on acceptance.** Letting an accepted detection act
   without approval would make the human gate decorative. Rejected:
   acceptance only OPENS a request; HumanGate.execute() is the only
   path to action, and it denies without quorum.
4. **Scoring every look.** An earlier reimplementation of a related
   injection scored every variant tried, inflating scores 3-6x. This
   package scores exactly two forecasts per event; the rule is pinned
   by test so the bug cannot silently return.

## Kept design

- Coherence over sharpness (WaveHolo lesson: sharp can lie, real can't).
- Calibration before judgment, frozen after (refusing-membrane lesson).
- Two forecasts, explicit costs (Crystallize lesson).
- Approval quorum + hash-chained ledger (AgentGate lesson).
- No lethal action in the action set, by construction, not by policy
  comment alone: QUORUM contains exactly {"alert", "decoy"}.

## Open questions (not answered here)

- What coherence threshold survives real sensor noise? Unknown until
  real data exists. The synthetic threshold must not be quoted as a
  real-world number.
- How many approvers, and who, for a real deployment? A software
  prototype cannot answer that; people and their rules must.
- Does the two-look loop cost too much time for fast scenes? Unmeasured
  here; the demo is not a latency benchmark.
