import tempfile
import unittest
from pathlib import Path

from toposense_sim.benchmark import METHODS, run_benchmark
from toposense_sim.metrics import wilson_upper
from toposense_sim.validation import validate_artifact


ROOT = Path(__file__).resolve().parents[1]


class MetricsBenchmarkTests(unittest.TestCase):
    def test_wilson_upper_is_conservative(self) -> None:
        self.assertGreater(wilson_upper(0, 500), 0.0)
        self.assertLess(wilson_upper(0, 500), 0.01)
        self.assertGreater(wilson_upper(5, 500), 0.01)

    def test_quick_artifact_has_all_methods_and_validates(self) -> None:
        (ROOT / "artifacts").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts", prefix="test-") as directory:
            result = run_benchmark(directory, seed_start=0, seeds_per_family=5, bootstrap_resamples=100)
            self.assertEqual(result["manifest"]["row_count"], 5 * 5 * len(METHODS))
            report = validate_artifact(directory, quick=False)
            self.assertTrue(report["integrity"], report["checks"])


if __name__ == "__main__":
    unittest.main()
