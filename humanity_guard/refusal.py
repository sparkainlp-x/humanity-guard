"""Refusal gate: calibrated on training data, then frozen.

The gate's threshold tau is chosen once, on labeled synthetic training
scenes, to maximize Youden's J (sensitivity + specificity - 1), and
then frozen. It is never re-tuned on the scenes it judges: a gate that
moves its own threshold after seeing the answer is not a gate.

Decision rule: accept (classify as real) iff coherence >= tau, else
REFUSE -- no classification is emitted at all. A refused scene is not
a negative; it is an explicit "I don't know", and it can never trigger
an action.

Accuracy-on-accepted is measured only over accepted scenes: among
scenes the gate accepted, the fraction that really were real.
"""

from __future__ import annotations

import numpy as np


def calibrate_threshold(real_scores, other_scores):
    """Pick tau maximizing Youden's J, at the middle of the best gap.

    Thresholds are evaluated at midpoints between consecutive observed
    scores, not at the scores themselves: picking an observed score as
    tau puts the threshold at the edge of the separating gap (in the
    demo that gave tau = 0.985, the smallest real score, with zero
    margin below it). The midpoint of the best gap has equal margin on
    both sides. Ties go to the widest gap.
    """
    real = np.asarray(real_scores, dtype=float)
    other = np.asarray(other_scores, dtype=float)
    points = np.unique(np.concatenate([real, other]))
    if len(points) < 2:
        return 0.5, 0.0
    # Candidate thresholds: midpoints between consecutive observed scores.
    # The margin of a candidate is its distance to the nearest score.
    best_tau, best_j, best_margin = 0.5, -1.0, -1.0
    for a, b in zip(points[:-1], points[1:]):
        tau = (a + b) / 2.0
        sensitivity = float(np.mean(real >= tau)) if len(real) else 0.0
        specificity = float(np.mean(other < tau)) if len(other) else 0.0
        j = sensitivity + specificity - 1.0
        margin = min(tau - a, b - tau)
        if j > best_j + 1e-12 or (abs(j - best_j) <= 1e-12 and margin > best_margin):
            best_j, best_tau, best_margin = j, float(tau), margin
    return best_tau, best_j


class RefusalGate:
    """Frozen coherence threshold gate."""

    def __init__(self, tau: float):
        if not 0.0 <= tau <= 1.0:
            raise ValueError("tau must be in [0, 1]")
        self.tau = tau
        self.accepted = 0
        self.refused = 0
        self.true_positives = 0
        self.false_positives = 0

    def decide(self, coherence: float, is_real: bool | None = None) -> str:
        """Return "accepted" or "refused". is_real is for audit only."""
        if coherence >= self.tau:
            self.accepted += 1
            if is_real is True:
                self.true_positives += 1
            elif is_real is False:
                self.false_positives += 1
            return "accepted"
        self.refused += 1
        return "refused"

    @property
    def accuracy_on_accepted(self) -> float | None:
        """Fraction of accepted scenes that were real; None if none accepted."""
        total = self.true_positives + self.false_positives
        if total == 0:
            return None
        return self.true_positives / total
