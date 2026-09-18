import unittest

import numpy as np

from toposense_sim.config import CONFIRMATORY_FAMILIES, sample_config
from toposense_sim.field import synthesize_field


class FieldTests(unittest.TestCase):
    def test_dense_ideal_winding_matches_registered_symbol(self) -> None:
        for seed in range(10):
            field = synthesize_field(seed, "nominal", dense_samples=512)
            self.assertEqual(field.true_winding, sample_config(seed, "nominal").winding)
            self.assertTrue(np.allclose(np.linalg.norm(field.ideal_stokes, axis=1), 1.0))

    def test_field_replay_is_exact(self) -> None:
        first = synthesize_field(17, "compound_shift", dense_samples=512)
        second = synthesize_field(17, "compound_shift", dense_samples=512)
        self.assertTrue(np.array_equal(first.received_stokes, second.received_stokes))

    def test_composed_families_change_multiple_receiver_axes(self) -> None:
        nominal = sample_config(11, "nominal")
        for family in CONFIRMATORY_FAMILIES:
            shifted = sample_config(11, family)
            differences = sum(
                getattr(nominal, name) != getattr(shifted, name)
                for name in ("photons_per_analyzer", "na_cutoff_mode", "crosstalk", "calibration_bias", "dropout_width_rad", "hidden_mode_amplitude")
            )
            self.assertGreaterEqual(differences, 2, family)
