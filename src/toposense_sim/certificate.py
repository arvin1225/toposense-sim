"""Selective projected-winding estimators and support-aware certificates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum

import numpy as np

from .geometry import TAU, polygon_winding
from .receiver import Observation


class Decision(str, Enum):
    RELEASE = "RELEASE"
    ERASURE = "ERASURE"


@dataclass(frozen=True)
class CertificateResult:
    method: str
    decision: Decision
    winding: int | None
    observed_winding: int
    correct: bool
    certificate_margin: float
    minimum_projected_radius: float
    maximum_gap_rad: float
    maximum_phase_step_rad: float
    support_residual: float
    edge_mode_fraction: float
    transfer_headroom: float
    gates: dict[str, bool]

    def as_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["decision"] = self.decision.value
        return result


def _support_diagnostics(observation: Observation) -> tuple[float, float, float]:
    angles = observation.nominal_angles
    z = observation.stokes[:, 0] + 1j * observation.stokes[:, 1]
    degree = observation.field.config.registered_mode_limit
    modes = np.arange(-degree, degree + 1)
    design = np.exp(1j * angles[:, None] * modes[None, :])
    coefficients, *_ = np.linalg.lstsq(design, z, rcond=None)
    fitted = design @ coefficients
    residual = float(np.linalg.norm(z - fitted) / max(np.linalg.norm(z), 1e-12))
    power = np.abs(coefficients) ** 2
    edge = float(np.sum(power[np.abs(modes) >= degree]) / max(np.sum(power), 1e-12))
    dominant = int(abs(modes[int(np.argmax(power))]))
    transfer = float(np.exp(-((dominant / max(observation.field.config.na_cutoff_mode, 0.4)) ** 4)))
    return residual, edge, transfer


def _ordered(observation: Observation) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    order = np.argsort(observation.nominal_angles)
    angles = observation.nominal_angles[order]
    stokes = observation.stokes[order]
    errors = observation.angular_error_bounds[order]
    gaps = np.diff(np.concatenate([angles, angles[:1] + TAU]))
    return angles, stokes, errors, gaps


def certify_observation(
    observation: Observation,
    *,
    method: str = "adaptive_support_certificate",
    local_uncertainty: bool = True,
    support_gate: bool = True,
    include_calibration_residual: bool = True,
) -> CertificateResult:
    if len(observation.stokes) < 3:
        raise ValueError("at least three valid observations are required")
    _, stokes, angular_errors, gaps = _ordered(observation)
    observed_winding, closure, increments = polygon_winding(stokes)
    z = stokes[:, 0] + 1j * stokes[:, 1]
    radii = np.abs(z)
    measurement = 2.0 * np.sin(angular_errors / 2.0)
    if not include_calibration_residual:
        reduced = np.maximum(0.0, angular_errors - observation.field.config.calibration_residual_bound_rad)
        measurement = 2.0 * np.sin(reduced / 2.0)
    global_lipschitz = 1.08 * observation.field.config.registered_mode_limit
    interpolation = np.empty(len(gaps), dtype=float)
    for index, gap in enumerate(gaps):
        if local_uncertainty:
            local_slope = abs(increments[index]) / max(gap, 1e-9) * max(radii[index], radii[(index + 1) % len(radii)])
            lipschitz = min(global_lipschitz, 0.45 + 1.25 * local_slope)
        else:
            lipschitz = global_lipschitz
        interpolation[index] = 0.5 * lipschitz * gap
    uncertainty = np.maximum(measurement, np.roll(measurement, -1)) + interpolation
    edge_radius = np.minimum(radii, np.roll(radii, -1))
    clearance = edge_radius - uncertainty
    ratios = np.clip(uncertainty / np.maximum(edge_radius, 1e-9), 0.0, 1.0)
    phase_budget = np.pi - 2.0 * np.arcsin(ratios)
    support_residual, edge_fraction, transfer = _support_diagnostics(observation)
    maximum_gap = float(np.max(gaps))
    support_pass = bool(
        support_residual < 0.24
        and edge_fraction < 0.34
        and transfer > 0.42
        and maximum_gap < 0.56
        and observation.dropped_count <= 4
    )
    gates = {
        "projected_clearance": bool(np.min(clearance) > 0.0),
        "unambiguous_phase": bool(np.all(np.abs(increments) < phase_budget)),
        "integer_closure": bool(closure <= 1e-7),
        "nontrivial_sampling": bool(len(stokes) >= 8),
        "measurement_model_registered": True,
        "support_observability": support_pass if support_gate else True,
        # A zero winding created by a translated/attenuated non-zero loop often
        # looks deceptively smooth. Releasing the trivial symbol therefore
        # requires a separate origin-separation margin, evaluated from the
        # observed projection only (never from the true label).
        "zero_mode_separation": bool(observed_winding != 0 or np.min(radii) > 0.50) if support_gate else True,
    }
    decision = Decision.RELEASE if all(gates.values()) else Decision.ERASURE
    winding = observed_winding if decision is Decision.RELEASE else None
    return CertificateResult(
        method=method,
        decision=decision,
        winding=winding,
        observed_winding=observed_winding,
        correct=bool(winding == observation.field.true_winding) if winding is not None else False,
        certificate_margin=float(np.min(clearance)),
        minimum_projected_radius=float(np.min(radii)),
        maximum_gap_rad=maximum_gap,
        maximum_phase_step_rad=float(np.max(np.abs(increments))),
        support_residual=support_residual,
        edge_mode_fraction=edge_fraction,
        transfer_headroom=transfer,
        gates=gates,
    )


def evaluate_baseline(observation: Observation, method: str) -> CertificateResult:
    _, stokes, errors, gaps = _ordered(observation)
    observed_winding, _, increments = polygon_winding(stokes)
    radii = np.abs(stokes[:, 0] + 1j * stokes[:, 1])
    support_residual, edge_fraction, transfer = _support_diagnostics(observation)
    if method == "polygon_unconditional":
        release = True
        margin = float(np.min(radii))
        gates = {"unconditional": True}
    elif method == "margin_only":
        margin = float(np.min(radii) - np.max(2.0 * np.sin(errors / 2.0)))
        release = margin > 0 and len(stokes) >= 4
        gates = {"sampled_margin": bool(margin > 0), "nontrivial_sampling": len(stokes) >= 4}
    elif method == "oracle_dense":
        observed_winding = observation.field.true_winding
        margin = 1.0
        release = True
        gates = {"oracle_diagnostic": True}
    else:
        raise ValueError(f"unknown baseline: {method}")
    winding = observed_winding if release else None
    return CertificateResult(
        method=method,
        decision=Decision.RELEASE if release else Decision.ERASURE,
        winding=winding,
        observed_winding=observed_winding,
        correct=bool(winding == observation.field.true_winding) if winding is not None else False,
        certificate_margin=margin,
        minimum_projected_radius=float(np.min(radii)),
        maximum_gap_rad=float(np.max(gaps)),
        maximum_phase_step_rad=float(np.max(np.abs(increments))),
        support_residual=support_residual,
        edge_mode_fraction=edge_fraction,
        transfer_headroom=transfer,
        gates=gates,
    )
