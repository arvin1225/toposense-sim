import unittest
import tempfile
from pathlib import Path

import numpy as np

from toposense_sim.benchmark_v2 import METHODS_H2, evaluate_trial_h2, run_h2_benchmark
from toposense_sim.receiver import acquire_value_adaptive
from toposense_sim.spectral_reference import audit_propagation, direct_periodic_transfer
from toposense_sim.validation_v2 import validate_h2_artifact


ROOT = Path(__file__).resolve().parents[1]


class H2ValueOfInformationTests(unittest.TestCase):
    def test_voi_replay_is_deterministic_and_budgeted(self) -> None:
        first = acquire_value_adaptive(503, "sector_dropout")
        second = acquire_value_adaptive(503, "sector_dropout")
        self.assertEqual(first.attempted_count, 32)
        self.assertTrue(np.array_equal(first.nominal_angles, second.nominal_angles))
        self.assertTrue(np.array_equal(first.stokes, second.stokes))

    def test_voi_schedule_differs_from_frozen_h1_policy(self) -> None:
        from toposense_sim.receiver import acquire_adaptive

        h1 = acquire_adaptive(503, "compound_shift")
        voi = acquire_value_adaptive(503, "compound_shift")
        self.assertFalse(np.array_equal(h1.nominal_angles, voi.nominal_angles))

    def test_h2_trial_has_complete_paired_methods(self) -> None:
        rows = evaluate_trial_h2(501, "compound_shift")
        self.assertEqual([row["method"] for row in rows], list(METHODS_H2))
        self.assertTrue(all(int(row["samples_used"]) <= 32 for row in rows))

    def test_direct_transfer_matches_fft_production(self) -> None:
        for seed, family in ((500, "blur_crosstalk"), (501, "high_mode_na"), (502, "compound_shift")):
            audit = audit_propagation(seed, family, samples=64)
            self.assertLess(audit.maximum_complex_error, 1e-10)
            self.assertTrue(audit.winding_match)

    def test_reference_transfer_is_linear(self) -> None:
        rng = np.random.default_rng(8)
        a = rng.normal(size=24) + 1j * rng.normal(size=24)
        b = rng.normal(size=24) + 1j * rng.normal(size=24)
        left = direct_periodic_transfer(0.3 * a - 0.7j * b, 3.2)
        right = 0.3 * direct_periodic_transfer(a, 3.2) - 0.7j * direct_periodic_transfer(b, 3.2)
        self.assertTrue(np.allclose(left, right, atol=1e-11, rtol=1e-11))

    def test_quick_h2_artifact_validates(self) -> None:
        (ROOT / "artifacts").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts", prefix="test-h2-") as directory:
            run_h2_benchmark(directory, seed_start=500, seeds_per_family=2, bootstrap_resamples=50)
            report = validate_h2_artifact(directory, quick=False)
            self.assertTrue(report["integrity"], report["checks"])


if __name__ == "__main__":
    unittest.main()
