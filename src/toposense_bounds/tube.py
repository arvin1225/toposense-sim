"""Certify a received complex loop from bounded samples and a derivative bound.

The derivative bound must come from a declared physical model or an independent
bound. Estimating it from adjacent sample slopes does not satisfy the contract.
See docs/BOUND_CERTIFICATE.md for the homotopy argument and assumptions.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class WindingBound:
    decision: str
    winding: int | None
    polygon_winding: int | None
    minimum_margin: float
    maximum_gap: float
    limiting_interval: int
    reason: str


def certify_winding(angles, samples, error_radii, *, derivative_bound: float) -> WindingBound:
    """Return a conditional certificate for a continuous 2*pi-periodic loop.

    Samples and errors are in the complex plane, without renormalization.
    Errors bound each endpoint simultaneously; |f'(theta)| <= derivative_bound
    must hold everywhere, including between samples. No labels are accepted.
    """
    theta = np.asarray(angles, dtype=float)
    z = np.asarray(samples, dtype=complex)
    errors = np.asarray(error_radii, dtype=float)
    if theta.ndim != 1 or len(theta) < 3 or z.shape != theta.shape or errors.shape != theta.shape:
        raise ValueError("aligned one-dimensional arrays with at least three samples are required")
    if not (np.all(np.isfinite(theta)) and np.all(np.isfinite(z)) and np.all(np.isfinite(errors))):
        raise ValueError("samples, angles and bounds must be finite")
    if np.any(errors < 0) or not np.isfinite(derivative_bound) or derivative_bound < 0:
        raise ValueError("error radii and derivative bound must be nonnegative")
    order = np.argsort(theta % (2 * np.pi))
    theta, z, errors = (theta % (2 * np.pi))[order], z[order], errors[order]
    gaps = np.diff(np.r_[theta, theta[0] + 2 * np.pi])
    if np.min(gaps) <= 1e-12:
        raise ValueError("angles must be distinct modulo 2*pi")
    dz = np.roll(z, -1) - z
    squared = np.abs(dz) ** 2
    projection = np.zeros_like(squared)
    np.divide(-np.real(np.conj(dz) * z), squared, out=projection, where=squared > 0)
    distance = np.abs(z + np.clip(projection, 0, 1) * dz)
    tube = np.maximum(errors, np.roll(errors, -1)) + derivative_bound * gaps / 2
    margins = distance - tube
    limiting = int(np.argmin(margins))
    # A contradiction between endpoints and the assumed bound cannot certify.
    consistent = np.all(np.abs(dz) <= derivative_bound * gaps + errors + np.roll(errors, -1) + 1e-12)
    polygon = None if np.min(distance) <= 1e-12 else int(round(float(np.sum(np.angle(np.roll(z, -1) * np.conj(z))) / (2 * np.pi))))
    release = bool(consistent and polygon is not None and np.min(margins) > 1e-12)
    return WindingBound(
        "RELEASE" if release else "ERASURE", polygon if release else None,
        polygon, float(np.min(margins)), float(np.max(gaps)), limiting,
        "BOUNDED_HOMOTOPY" if release else ("INCONSISTENT_BOUNDS" if not consistent else "ORIGIN_NOT_EXCLUDED"),
    )
