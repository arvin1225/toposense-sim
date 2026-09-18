"""Jones/Stokes boundary synthesis and finite-NA transfer."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import ReceiverConfig, sample_config
from .geometry import TAU, normalize_stokes, polygon_winding


@dataclass(frozen=True)
class OpticalField:
    seed: int
    config: ReceiverConfig
    angles: np.ndarray
    ideal_jones: np.ndarray
    received_jones: np.ndarray
    ideal_stokes: np.ndarray
    received_stokes: np.ndarray
    true_winding: int
    received_dense_winding: int
    ideal_high_mode_fraction: float
    received_high_mode_fraction: float


def jones_to_stokes(jones: np.ndarray) -> np.ndarray:
    er, el = jones[:, 0], jones[:, 1]
    intensity = np.maximum(np.abs(er) ** 2 + np.abs(el) ** 2, 1e-12)
    s1 = 2.0 * np.real(er * np.conjugate(el)) / intensity
    s2 = 2.0 * np.imag(er * np.conjugate(el)) / intensity
    s3 = (np.abs(er) ** 2 - np.abs(el) ** 2) / intensity
    return normalize_stokes(np.column_stack([s1, s2, s3]))


def _periodic_transfer(values: np.ndarray, cutoff: float) -> np.ndarray:
    frequencies = np.fft.fftfreq(len(values)) * len(values)
    transfer = np.exp(-((np.abs(frequencies) / max(cutoff, 0.4)) ** 4))
    return np.fft.ifft(np.fft.fft(values) * transfer)


def _high_mode_fraction(values: np.ndarray, limit: int) -> float:
    spectrum = np.abs(np.fft.fft(values)) ** 2
    frequencies = np.abs(np.fft.fftfreq(len(values)) * len(values))
    return float(np.sum(spectrum[frequencies > limit]) / max(np.sum(spectrum), 1e-12))


def synthesize_field(seed: int, family: str, dense_samples: int = 2048) -> OpticalField:
    config = sample_config(seed, family)
    theta = np.linspace(0.0, TAU, dense_samples, endpoint=False)
    rng = np.random.default_rng(seed * 65537 + 17)
    phase_offset = float(rng.uniform(-np.pi, np.pi))
    phase = (
        config.winding * theta
        + phase_offset
        + config.phase_modulation * np.sin(config.phase_harmonic * theta + 0.31)
        + config.hidden_mode_amplitude * np.sin(config.hidden_mode_order * theta - 0.47)
    )
    latitude = config.latitude_rad + config.latitude_modulation * np.sin(2.0 * theta - 0.28)
    er = np.cos(0.5 * (np.pi / 2.0 - latitude)).astype(complex)
    el = np.sin(0.5 * (np.pi / 2.0 - latitude)).astype(complex) * np.exp(-1j * phase)
    ideal_jones = np.column_stack([er, el])
    received_jones = np.column_stack([_periodic_transfer(er, config.na_cutoff_mode), _periodic_transfer(el, config.na_cutoff_mode)])
    ideal_stokes = jones_to_stokes(ideal_jones)
    received_stokes = jones_to_stokes(received_jones)
    if config.projected_bias:
        received_stokes = normalize_stokes(
            received_stokes + np.array([config.projected_bias, -0.35 * config.projected_bias, 0.0])[None, :]
        )
    true_winding = polygon_winding(ideal_stokes)[0]
    received_winding = polygon_winding(received_stokes)[0]
    projected_ideal = ideal_stokes[:, 0] + 1j * ideal_stokes[:, 1]
    projected_received = received_stokes[:, 0] + 1j * received_stokes[:, 1]
    return OpticalField(
        seed=seed,
        config=config,
        angles=theta,
        ideal_jones=ideal_jones,
        received_jones=received_jones,
        ideal_stokes=ideal_stokes,
        received_stokes=received_stokes,
        true_winding=true_winding,
        received_dense_winding=received_winding,
        ideal_high_mode_fraction=_high_mode_fraction(projected_ideal, config.registered_mode_limit),
        received_high_mode_fraction=_high_mode_fraction(projected_received, config.registered_mode_limit),
    )
