"""Registered source and held-out optical/sensor families."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


SOURCE_FAMILIES = ("nominal", "shot_only", "blur_only", "crosstalk_only", "jitter_only")
CONFIRMATORY_FAMILIES = ("blur_crosstalk", "low_photon_bias", "high_mode_na", "sector_dropout", "compound_shift")
ALL_FAMILIES = SOURCE_FAMILIES + CONFIRMATORY_FAMILIES
SYMBOLS = (-2, -1, 0, 1, 2)


@dataclass(frozen=True)
class ReceiverConfig:
    family: str
    winding: int
    photons_per_analyzer: float = 5000.0
    read_noise_electrons: float = 2.0
    na_cutoff_mode: float = 8.0
    crosstalk: float = 0.01
    calibration_bias: float = 0.004
    calibration_residual_bound_rad: float = 0.018
    angular_jitter_rad: float = 0.002
    jitter_bound_rad: float = 0.006
    dropout_center_rad: float = -10.0
    dropout_width_rad: float = 0.0
    latitude_rad: float = 0.38
    latitude_modulation: float = 0.12
    phase_modulation: float = 0.10
    phase_harmonic: int = 3
    hidden_mode_amplitude: float = 0.03
    hidden_mode_order: int = 6
    projected_bias: float = 0.0
    registered_mode_limit: int = 4

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def _u(rng: np.random.Generator, low: float, high: float) -> float:
    return float(rng.uniform(low, high))


def sample_config(seed: int, family: str) -> ReceiverConfig:
    if family not in ALL_FAMILIES:
        raise ValueError(f"unknown family: {family}")
    rng = np.random.default_rng(seed * 104729 + sum(map(ord, family)))
    winding = SYMBOLS[seed % len(SYMBOLS)]
    values: dict[str, float | int | str] = {
        "family": family,
        "winding": winding,
        "photons_per_analyzer": _u(rng, 4300.0, 7200.0),
        "read_noise_electrons": _u(rng, 1.0, 3.0),
        "na_cutoff_mode": _u(rng, 7.0, 9.5),
        "crosstalk": _u(rng, 0.004, 0.018),
        "calibration_bias": _u(rng, 0.001, 0.006),
        "calibration_residual_bound_rad": _u(rng, 0.014, 0.024),
        "angular_jitter_rad": _u(rng, 0.0005, 0.003),
        "jitter_bound_rad": 0.007,
        "latitude_rad": _u(rng, 0.18, 0.55),
        "latitude_modulation": _u(rng, 0.04, 0.14),
        "phase_modulation": _u(rng, 0.04, 0.14),
        "phase_harmonic": int(rng.integers(2, 4)),
        "hidden_mode_amplitude": _u(rng, 0.0, 0.045),
        "hidden_mode_order": int(rng.integers(5, 8)),
        "projected_bias": 0.0,
    }
    if family == "shot_only":
        values["photons_per_analyzer"] = _u(rng, 650.0, 1500.0)
        values["read_noise_electrons"] = _u(rng, 3.0, 7.0)
    elif family == "blur_only":
        values["na_cutoff_mode"] = _u(rng, 3.5, 5.0)
    elif family == "crosstalk_only":
        values["crosstalk"] = _u(rng, 0.055, 0.10)
        values["calibration_bias"] = _u(rng, 0.015, 0.035)
        values["calibration_residual_bound_rad"] = 0.07
    elif family == "jitter_only":
        values["angular_jitter_rad"] = _u(rng, 0.018, 0.045)
        values["jitter_bound_rad"] = 0.055
    elif family == "blur_crosstalk":
        values["na_cutoff_mode"] = _u(rng, 2.7, 4.2)
        values["crosstalk"] = _u(rng, 0.09, 0.16)
        values["calibration_bias"] = _u(rng, 0.025, 0.06)
        values["calibration_residual_bound_rad"] = 0.105
        values["latitude_rad"] = _u(rng, 0.62, 0.96)
        values["projected_bias"] = _u(rng, 0.32, 0.62)
    elif family == "low_photon_bias":
        values["photons_per_analyzer"] = _u(rng, 180.0, 520.0)
        values["read_noise_electrons"] = _u(rng, 6.0, 13.0)
        values["calibration_bias"] = _u(rng, 0.07, 0.14)
        values["calibration_residual_bound_rad"] = 0.16
        values["latitude_rad"] = _u(rng, 0.76, 1.04)
        values["projected_bias"] = _u(rng, 0.34, 0.66)
    elif family == "high_mode_na":
        values["na_cutoff_mode"] = _u(rng, 2.0, 3.2)
        values["hidden_mode_amplitude"] = _u(rng, 0.24, 0.46)
        values["hidden_mode_order"] = int(rng.integers(6, 10))
        values["phase_modulation"] = _u(rng, 0.24, 0.42)
        values["latitude_rad"] = _u(rng, 0.72, 1.02)
        values["projected_bias"] = _u(rng, 0.42, 0.76)
    elif family == "sector_dropout":
        values["dropout_center_rad"] = _u(rng, 0.0, np.pi * 2.0)
        values["dropout_width_rad"] = _u(rng, 0.62, 1.08)
        values["phase_modulation"] = _u(rng, 0.22, 0.40)
        values["phase_harmonic"] = int(rng.integers(3, 6))
        values["angular_jitter_rad"] = _u(rng, 0.012, 0.032)
        values["jitter_bound_rad"] = 0.045
    elif family == "compound_shift":
        values["photons_per_analyzer"] = _u(rng, 220.0, 620.0)
        values["read_noise_electrons"] = _u(rng, 5.0, 12.0)
        values["na_cutoff_mode"] = _u(rng, 2.1, 3.7)
        values["crosstalk"] = _u(rng, 0.10, 0.18)
        values["calibration_bias"] = _u(rng, 0.06, 0.13)
        values["calibration_residual_bound_rad"] = 0.18
        values["angular_jitter_rad"] = _u(rng, 0.018, 0.05)
        values["jitter_bound_rad"] = 0.06
        values["latitude_rad"] = _u(rng, 0.72, 1.05)
        values["hidden_mode_amplitude"] = _u(rng, 0.18, 0.38)
        values["hidden_mode_order"] = int(rng.integers(6, 10))
        values["projected_bias"] = _u(rng, 0.44, 0.80)
    return ReceiverConfig(**values)
