"""Crystallize-style verification: commit, replicate, revise, score.

One detection is never trusted on a single look. The engine commits a
probability after the first look, takes a second independent look
(the replication, on fresh noise), revises, and scores both commits
with the Brier rule:

    brier(p, truth) = (p - truth)^2
    points(p, truth) = 100 * (1 - 4 * brier)
    event score = 0.5 * points(p1) + 0.5 * points(p2) - 0.8 * n_looks

Exactly two forecasts per event are scored, no matter how many looks
were taken. Scoring every look would inflate the score by the number
of looks; that was a real scoring bug found in a reimplementation and
is pinned by test here.

p values are clipped to [0.01, 0.99], as in Crystallize.
"""

from __future__ import annotations

P_MIN = 0.01
P_MAX = 0.99
COST_PER_LOOK = 0.8


def clamp_p(p: float) -> float:
    return float(min(P_MAX, max(P_MIN, p)))


def brier(p: float, truth: bool) -> float:
    d = clamp_p(p) - (1.0 if truth else 0.0)
    return d * d


def calibration_points(p: float, truth: bool) -> float:
    """100 at a perfect report, 0 at 50%, negative when confidently wrong."""
    return 100.0 * (1.0 - 4.0 * brier(p, truth))


def revise_toward_humility(p: float) -> float:
    """Move a commit halfway toward 0.5 after a miss."""
    return clamp_p(0.5 * (clamp_p(p) + 0.5))


def score_event(p1: float, p2: float, truth: bool, n_looks: int = 2) -> dict:
    """Score one detection event with exactly two forecasts."""
    s1 = calibration_points(p1, truth)
    s2 = calibration_points(p2, truth)
    cost = COST_PER_LOOK * n_looks
    return {
        "points_first": s1,
        "points_revised": s2,
        "sampling_cost": cost,
        "score": 0.5 * s1 + 0.5 * s2 - cost,
    }
