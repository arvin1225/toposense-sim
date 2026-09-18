import json
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class PublishedArtifactTests(unittest.TestCase):
    def test_dashboard_is_bound_to_confirmatory_summary(self) -> None:
        dashboard = json.loads((ROOT / "web" / "public" / "data" / "receiver.json").read_text(encoding="utf-8"))
        summary = json.loads((ROOT / "artifacts" / "confirmatory" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(dashboard["summary"]["hypotheses"], summary["hypotheses"])
        self.assertEqual(dashboard["summary"]["registered_success"], summary["registered_success"])
        self.assertEqual(len(dashboard["representatives"]), 5)

    def test_dashboard_loops_are_finite_normalized_and_method_complete(self) -> None:
        dashboard = json.loads((ROOT / "web" / "public" / "data" / "receiver.json").read_text(encoding="utf-8"))
        expected = set(dashboard["methodLabels"])
        for item in dashboard["representatives"]:
            ideal = np.asarray(item["ideal"], dtype=float)
            received = np.asarray(item["received"], dtype=float)
            self.assertTrue(np.all(np.isfinite(ideal)))
            self.assertTrue(np.allclose(np.linalg.norm(ideal, axis=1), 1.0, atol=2e-5))
            self.assertTrue(np.allclose(np.linalg.norm(received, axis=1), 1.0, atol=2e-5))
            self.assertTrue(expected.issubset(set(item["methods"])))
            self.assertLessEqual(len(item["adaptive"]["angles"]), 32)

    def test_publication_figures_have_vector_and_raster_exports(self) -> None:
        for stem in ("fig_certified_goodput", "fig_receiver_evidence"):
            png = ROOT / "figures" / f"{stem}.png"
            pdf = ROOT / "figures" / f"{stem}.pdf"
            self.assertEqual(png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
