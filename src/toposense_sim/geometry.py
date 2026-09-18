"""Auditable circular geometry and Stokes primitives."""

from __future__ import annotations

import numpy as np


TAU = float(2.0 * np.pi)


def normalize_stokes(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("Stokes array must have shape (n, 3)")
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    if np.any(norms <= 1e-12) or not np.all(np.isfinite(array)):
        raise ValueError("Stokes observations must be finite and nonzero")
    return array / norms


def principal_increment(z0: complex, z1: complex) -> float:
    if abs(z0) <= 1e-12 or abs(z1) <= 1e-12:
        raise ValueError("phase undefined at projected origin")
    product = z1 * np.conjugate(z0)
    return float(np.arctan2(product.imag, product.real))


def polygon_winding(stokes: np.ndarray) -> tuple[int, float, np.ndarray]:
    points = normalize_stokes(stokes)
    projected = points[:, 0] + 1j * points[:, 1]
    increments = np.array([principal_increment(projected[i], projected[(i + 1) % len(projected)]) for i in range(len(projected))])
    turns = float(np.sum(increments) / TAU)
    winding = int(round(turns))
    return winding, abs(turns - winding), increments


def circular_gaps(angles: np.ndarray) -> np.ndarray:
    ordered = np.sort(np.mod(np.asarray(angles, dtype=float), TAU))
    return np.diff(np.concatenate([ordered, ordered[:1] + TAU]))


def angular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aa = normalize_stokes(np.atleast_2d(a))
    bb = normalize_stokes(np.atleast_2d(b))
    dots = np.sum(aa * bb, axis=1)
    return np.arccos(np.clip(dots, -1.0, 1.0))
