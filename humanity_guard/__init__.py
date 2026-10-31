"""Humanity Guard: defensive holographic sensing with a human gate.

Sense (coherence, not sharpness) -> verify (commit, replicate, revise,
Brier) -> refuse (frozen calibrated gate) -> human gate (approval
quorum, hash-chained ledger) -> act (alert or decoy only).

Synthetic, classical, stdlib + numpy. No lethal action exists in this
package. See README.md for honest limits.
"""

from .engine import GuardianEngine, calibrate_gate
from .humangate import HumanGate
from .refusal import RefusalGate, calibrate_threshold
from .sensing import coherence, generate_scene, sharpness
from .verify import brier, calibration_points, clamp_p, score_event

__version__ = "0.1.0"

__all__ = [
    "GuardianEngine",
    "calibrate_gate",
    "HumanGate",
    "RefusalGate",
    "calibrate_threshold",
    "coherence",
    "generate_scene",
    "sharpness",
    "brier",
    "calibration_points",
    "clamp_p",
    "score_event",
]
