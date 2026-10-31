"""Synthetic sensing: coherence vs sharpness.

A scene is N complex modes. A REAL object produces phases concentrated
around one true phase (coherent). A DECOY, a GLARE, or pure NOISE
produces scattered phases -- but a decoy can be made to LOOK sharp by
concentrating amplitude into a few bright modes. That is the sharpness
lie: amplitude variance is high, phase coherence is low.

The detector therefore trusts coherence, never sharpness alone:

    coherence = |sum_j A_j exp(i theta_j)| / sum_j A_j   (0..1)
    sharpness = variance of amplitude, normalized

SYNTHETIC. These scenes model sensor phenomenology; they are not
recordings from any real sensor, and no claim about any real device
follows from them.
"""

from __future__ import annotations

import math

import numpy as np

N_MODES = 64


def generate_scene(rng: np.random.Generator, kind: str, n_modes: int = N_MODES):
    """Return (amplitude, phase) for one synthetic scene.

    kind: "real", "decoy", "glare", or "noise".
    """
    if kind == "real":
        true_phase = float(rng.uniform(-math.pi, math.pi))
        phase = true_phase + rng.normal(0.0, 0.15, size=n_modes)
        amplitude = np.ones(n_modes) + rng.normal(0.0, 0.05, size=n_modes)
        amplitude = np.clip(amplitude, 0.5, 1.5)
    elif kind == "decoy":
        # Sharpness lie: a few very bright modes, phases scattered.
        phase = rng.uniform(-math.pi, math.pi, size=n_modes)
        amplitude = np.full(n_modes, 0.2)
        bright = rng.choice(n_modes, size=max(1, n_modes // 10), replace=False)
        amplitude[bright] = 3.0
    elif kind == "glare":
        phase = rng.uniform(-math.pi, math.pi, size=n_modes)
        amplitude = np.full(n_modes, 0.2)
        amplitude[rng.integers(0, n_modes)] = 5.0
    elif kind == "noise":
        phase = rng.uniform(-math.pi, math.pi, size=n_modes)
        amplitude = np.ones(n_modes)
    else:
        raise ValueError(f"unknown scene kind: {kind!r}")
    return amplitude, phase


def coherence(amplitude, phase) -> float:
    """Amplitude-weighted phase coherence, 0..1. See module docstring."""
    amplitude = np.asarray(amplitude, dtype=float)
    phase = np.asarray(phase, dtype=float)
    total = float(np.sum(amplitude))
    if total <= 0:
        return 0.0
    field = amplitude * np.exp(1j * phase)
    return float(abs(np.sum(field)) / total)


def sharpness(amplitude) -> float:
    """Normalized amplitude variance: high for decoys, low for real scenes."""
    amplitude = np.asarray(amplitude, dtype=float)
    mean = float(np.mean(amplitude))
    if mean <= 0:
        return 0.0
    return float(np.var(amplitude) / (mean * mean))
