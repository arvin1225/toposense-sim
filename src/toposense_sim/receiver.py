"""Finite photon-budget Stokes acquisition and adaptive angular sampling."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .field import OpticalField, synthesize_field
from .geometry import TAU, angular_distance, normalize_stokes, principal_increment


@dataclass(frozen=True)
class Observation:
    field: OpticalField
    nominal_angles: np.ndarray
    actual_angles: np.ndarray
    stokes: np.ndarray
    received_truth: np.ndarray
    angular_error_bounds: np.ndarray
    analyzer_totals: np.ndarray
    attempted_count: int
    dropped_count: int
    adaptive: bool
    uncertainty_covered_fraction: float


def _circular_delta(angle: float, center: float) -> float:
    return float(abs((angle - center + np.pi) % TAU - np.pi))


def _interpolate_periodic(angles: np.ndarray, grid: np.ndarray, values: np.ndarray) -> np.ndarray:
    extended_x = np.concatenate([grid[-1:] - TAU, grid, grid[:1] + TAU])
    result = np.column_stack(
        [np.interp(np.mod(angles, TAU), extended_x, np.concatenate([values[-1:, axis], values[:, axis], values[:1, axis]])) for axis in range(values.shape[1])]
    )
    return normalize_stokes(result)


class MeasurementEngine:
    def __init__(self, field: OpticalField) -> None:
        self.field = field
        self.attempted: dict[float, tuple[float, np.ndarray, np.ndarray, float] | None] = {}

    def _key(self, angle: float) -> float:
        return round(float(np.mod(angle, TAU)), 12)

    def measure(self, nominal_angle: float) -> tuple[float, np.ndarray, np.ndarray, float] | None:
        key = self._key(nominal_angle)
        if key in self.attempted:
            return self.attempted[key]
        config = self.field.config
        if config.dropout_width_rad > 0 and _circular_delta(key, config.dropout_center_rad) <= config.dropout_width_rad / 2.0:
            self.attempted[key] = None
            return None
        code = int(round(key / TAU * 10_000_019))
        rng = np.random.default_rng(self.field.seed * 1_000_003 + code + 7919)
        jitter = float(rng.normal(0.0, config.angular_jitter_rad))
        actual = float(np.mod(key + jitter, TAU))
        truth = _interpolate_periodic(np.array([actual]), self.field.angles, self.field.received_stokes)[0]
        cross = config.crosstalk
        transform = np.array(
            [[1.0, cross, -0.35 * cross], [-0.55 * cross, 1.0, cross], [0.45 * cross, -0.4 * cross, 1.0]], dtype=float
        )
        bias = config.calibration_bias * np.array([1.0, -0.65, 0.35])
        distorted = transform @ truth + bias
        distorted /= max(np.linalg.norm(distorted), 1e-12)
        estimates = np.zeros(3, dtype=float)
        totals = np.zeros(3, dtype=float)
        for axis in range(3):
            plus_mean = config.photons_per_analyzer * max(0.0, (1.0 + distorted[axis]) / 2.0)
            minus_mean = config.photons_per_analyzer * max(0.0, (1.0 - distorted[axis]) / 2.0)
            plus = max(0.0, float(rng.poisson(plus_mean) + rng.normal(0.0, config.read_noise_electrons)))
            minus = max(0.0, float(rng.poisson(minus_mean) + rng.normal(0.0, config.read_noise_electrons)))
            total = max(plus + minus, 1.0)
            estimates[axis] = (plus - minus) / total
            totals[axis] = total
        measured = normalize_stokes(estimates[None, :])[0]
        photon_term = 4.2 / np.sqrt(max(float(np.min(totals)), 1.0))
        read_term = 4.0 * config.read_noise_electrons / max(float(np.min(totals)), 1.0)
        bound = float(
            min(
                1.25,
                photon_term + read_term + config.calibration_residual_bound_rad + config.jitter_bound_rad * (abs(config.winding) + config.phase_harmonic * config.phase_modulation),
            )
        )
        result = (actual, measured, truth, bound)
        self.attempted[key] = result
        return result

    def observe(self, *, adaptive: bool) -> Observation:
        valid = [(angle, result) for angle, result in self.attempted.items() if result is not None]
        valid.sort(key=lambda item: item[0])
        nominal = np.array([item[0] for item in valid], dtype=float)
        actual = np.array([item[1][0] for item in valid], dtype=float)
        measured = np.array([item[1][1] for item in valid], dtype=float)
        truth = np.array([item[1][2] for item in valid], dtype=float)
        bounds = np.array([item[1][3] for item in valid], dtype=float)
        totals = np.full((len(valid), 3), self.field.config.photons_per_analyzer, dtype=float)
        covered = angular_distance(measured, truth) <= bounds
        return Observation(
            field=self.field,
            nominal_angles=nominal,
            actual_angles=actual,
            stokes=measured,
            received_truth=truth,
            angular_error_bounds=bounds,
            analyzer_totals=totals,
            attempted_count=len(self.attempted),
            dropped_count=sum(result is None for result in self.attempted.values()),
            adaptive=adaptive,
            uncertainty_covered_fraction=float(np.mean(covered)) if len(covered) else 0.0,
        )


def acquire_uniform(seed: int, family: str, budget: int = 32, *, field: OpticalField | None = None) -> Observation:
    if budget < 4:
        raise ValueError("budget must be at least four")
    optical = field or synthesize_field(seed, family)
    engine = MeasurementEngine(optical)
    offset = float((seed % 17) / 17.0 * TAU / budget)
    for angle in np.linspace(0.0, TAU, budget, endpoint=False) + offset:
        engine.measure(float(angle))
    return engine.observe(adaptive=False)


def _refinement_candidates(start: float, gap: float) -> tuple[float, ...]:
    return tuple(float(np.mod(start + fraction * gap, TAU)) for fraction in (0.5, 0.382, 0.618, 0.25, 0.75))


def _interval_scores(observation: Observation) -> list[tuple[float, float, float]]:
    angles = observation.nominal_angles
    z = observation.stokes[:, 0] + 1j * observation.stokes[:, 1]
    scores: list[tuple[float, float, float]] = []
    for index in range(len(angles)):
        next_index = (index + 1) % len(angles)
        gap = float((angles[next_index] - angles[index]) % TAU)
        phase = abs(principal_increment(z[index], z[next_index]))
        radius = max(1e-5, min(abs(z[index]), abs(z[next_index])))
        uncertainty = observation.angular_error_bounds[index] + observation.angular_error_bounds[next_index]
        score = gap / (TAU / 12.0) + phase / np.pi + 0.8 * uncertainty / radius
        scores.append((float(score), float(angles[index]), gap))
    return sorted(scores, reverse=True)


def _edge_certificate_margin(
    left: np.ndarray,
    right: np.ndarray,
    left_bound: float,
    right_bound: float,
    gap: float,
    mode_limit: int,
) -> float:
    """Observed-data proxy for the local certificate's limiting margin."""

    z0 = complex(left[0], left[1])
    z1 = complex(right[0], right[1])
    radii = np.array([abs(z0), abs(z1)], dtype=float)
    edge_radius = max(1e-9, float(np.min(radii)))
    phase = abs(principal_increment(z0, z1))
    local_slope = phase / max(gap, 1e-9) * float(np.max(radii))
    lipschitz = min(1.08 * mode_limit, 0.45 + 1.25 * local_slope)
    measurement = max(2.0 * np.sin(left_bound / 2.0), 2.0 * np.sin(right_bound / 2.0))
    uncertainty = float(measurement + 0.5 * lipschitz * gap)
    clearance = edge_radius - uncertainty
    ratio = float(np.clip(uncertainty / edge_radius, 0.0, 1.0))
    phase_budget = float(np.pi - 2.0 * np.arcsin(ratio))
    phase_margin = edge_radius * (phase_budget - phase) / np.pi
    return float(min(clearance, phase_margin))


def _predicted_stokes(left: np.ndarray, right: np.ndarray, fraction: float) -> np.ndarray:
    chord = (1.0 - fraction) * left + fraction * right
    norm = float(np.linalg.norm(chord))
    if norm <= 1e-9:
        chord = left if fraction <= 0.5 else right
        norm = float(np.linalg.norm(chord))
    return chord / max(norm, 1e-12)


def _voi_candidates(observation: Observation) -> list[tuple[float, float]]:
    """Rank candidate locations by predicted global certificate-margin gain.

    This routine deliberately receives only the observation. It cannot inspect
    the dense field, true winding, family label, or hidden receiver parameters.
    """

    angles = observation.nominal_angles
    stokes = observation.stokes
    bounds = observation.angular_error_bounds
    mode_limit = observation.field.config.registered_mode_limit
    edge_records: list[tuple[float, float, float, int, int]] = []
    for index in range(len(angles)):
        next_index = (index + 1) % len(angles)
        gap = float((angles[next_index] - angles[index]) % TAU)
        margin = _edge_certificate_margin(
            stokes[index], stokes[next_index], float(bounds[index]), float(bounds[next_index]), gap, mode_limit
        )
        edge_records.append((margin, float(angles[index]), gap, index, next_index))
    old_global = min(record[0] for record in edge_records)
    base_gap = TAU / 12.0
    ranked: list[tuple[float, float]] = []
    for edge_index, (old_margin, start, gap, left_index, right_index) in enumerate(edge_records):
        other_margin = min((record[0] for i, record in enumerate(edge_records) if i != edge_index), default=np.inf)
        for fraction in (0.5, 0.382, 0.618, 0.25, 0.75):
            candidate = float(np.mod(start + fraction * gap, TAU))
            predicted = _predicted_stokes(stokes[left_index], stokes[right_index], fraction)
            predicted_bound = float(max(bounds[left_index], bounds[right_index]))
            left_margin = _edge_certificate_margin(
                stokes[left_index], predicted, float(bounds[left_index]), predicted_bound, fraction * gap, mode_limit
            )
            right_margin = _edge_certificate_margin(
                predicted,
                stokes[right_index],
                predicted_bound,
                float(bounds[right_index]),
                (1.0 - fraction) * gap,
                mode_limit,
            )
            new_global = min(other_margin, left_margin, right_margin)
            global_gain = max(0.0, float(new_global - old_global))
            local_gain = max(0.0, float(min(left_margin, right_margin) - old_margin))
            # Frozen before H2 confirmation: global bottleneck reduction is the
            # principal term; a small local/exploration term prevents ties and
            # retains angular support when several deficits are comparable.
            score = global_gain + 0.22 * local_gain + 0.018 * gap / base_gap
            ranked.append((float(score), candidate))
    return sorted(ranked, key=lambda item: (-item[0], item[1]))


def acquire_adaptive(
    seed: int,
    family: str,
    *,
    initial: int = 12,
    budget: int = 32,
    field: OpticalField | None = None,
) -> Observation:
    if not 4 <= initial <= budget:
        raise ValueError("require 4 <= initial <= budget")
    optical = field or synthesize_field(seed, family)
    engine = MeasurementEngine(optical)
    offset = float((seed % 13) / 13.0 * TAU / initial)
    for angle in np.linspace(0.0, TAU, initial, endpoint=False) + offset:
        engine.measure(float(angle))
    while len(engine.attempted) < budget:
        snapshot = engine.observe(adaptive=True)
        if len(snapshot.nominal_angles) < 2:
            candidate = float(len(engine.attempted) / budget * TAU)
            engine.measure(candidate)
            continue
        added = False
        for _, start, gap in _interval_scores(snapshot):
            for candidate in _refinement_candidates(start, gap):
                if engine._key(candidate) not in engine.attempted:
                    engine.measure(candidate)
                    added = True
                    break
            if added:
                break
        if not added:
            for candidate in np.linspace(0.0, TAU, budget * 4, endpoint=False):
                if engine._key(float(candidate)) not in engine.attempted:
                    engine.measure(float(candidate))
                    added = True
                    break
        if not added:
            break
    return engine.observe(adaptive=True)


def acquire_value_adaptive(
    seed: int,
    family: str,
    *,
    initial: int = 12,
    budget: int = 32,
    field: OpticalField | None = None,
) -> Observation:
    """Acquire by predicted certificate-margin value per attempted location."""

    if not 4 <= initial <= budget:
        raise ValueError("require 4 <= initial <= budget")
    optical = field or synthesize_field(seed, family)
    engine = MeasurementEngine(optical)
    offset = float((seed % 13) / 13.0 * TAU / initial)
    for angle in np.linspace(0.0, TAU, initial, endpoint=False) + offset:
        engine.measure(float(angle))
    while len(engine.attempted) < budget:
        snapshot = engine.observe(adaptive=True)
        refinement_index = len(engine.attempted) - initial
        ranked_angles: list[float] = []
        if len(snapshot.nominal_angles) >= 2 and refinement_index % 2 == 0:
            # Amendment 01: recover global angular support on alternating
            # attempts before returning to the local certificate bottleneck.
            for _, start, gap in _interval_scores(snapshot):
                ranked_angles.extend(_refinement_candidates(start, gap))
        elif len(snapshot.nominal_angles) >= 2:
            ranked_angles = [angle for _, angle in _voi_candidates(snapshot)]
        candidate = next((angle for angle in ranked_angles if engine._key(angle) not in engine.attempted), None)
        if candidate is None:
            candidate = next(
                (
                    float(angle)
                    for angle in np.linspace(0.0, TAU, budget * 8, endpoint=False)
                    if engine._key(float(angle)) not in engine.attempted
                ),
                None,
            )
        if candidate is None:
            break
        engine.measure(candidate)
    return engine.observe(adaptive=True)
