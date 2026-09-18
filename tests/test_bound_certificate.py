import unittest

import numpy as np

from toposense_bounds import certify_winding


class BoundCertificateTests(unittest.TestCase):
    def test_orientation_and_nonuniform_sampling(self):
        angles = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        angles[1] += 0.03
        for winding in (-2, -1, 0, 1, 2):
            z = np.exp(1j * winding * angles)
            result = certify_winding(angles[::-1], z[::-1], np.zeros(32), derivative_bound=abs(winding))
            self.assertEqual(result.winding, winding)

    def test_aliasing_is_rejected_with_valid_derivative_bound(self):
        angles = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        z = np.exp(17j * angles)
        result = certify_winding(angles, z, np.zeros(16), derivative_bound=17)
        self.assertEqual(result.polygon_winding, 1)
        self.assertEqual(result.decision, "ERASURE")

    def test_large_gap_and_origin_crossing_are_rejected(self):
        angles = np.array([0, 0.1, 0.2, np.pi])
        self.assertEqual(certify_winding(angles, np.exp(1j * angles), np.zeros(4), derivative_bound=1).decision, "ERASURE")

    def test_invalid_input_and_contradictory_bounds(self):
        for angles in ([0, 0, 1], [0, np.nan, 1]):
            with self.assertRaises(ValueError):
                certify_winding(angles, [1, 1, 1], [0, 0, 0], derivative_bound=1)
        result = certify_winding([0, 1, 2], [1, 2, 3], [0, 0, 0], derivative_bound=0)
        self.assertEqual(result.reason, "INCONSISTENT_BOUNDS")

    def test_bounded_noise_property(self):
        rng = np.random.default_rng(829)
        for winding in range(-3, 4):
            for _ in range(25):
                angles = np.linspace(0, 2 * np.pi, 48, endpoint=False)
                errors = np.full(48, 0.02)
                z = np.exp(1j * winding * angles) + rng.uniform(0, 0.02, 48) * np.exp(1j * rng.uniform(0, 2 * np.pi, 48))
                result = certify_winding(angles, z, errors, derivative_bound=abs(winding))
                self.assertEqual(result.winding, winding)

    def test_sample_slopes_cannot_validate_the_bound(self):
        angles = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        z = np.exp(17j * angles)
        # Deliberately false assumptions can produce a false certificate.
        # This demonstrates why the independent-bound precondition matters.
        self.assertEqual(certify_winding(angles, z, np.zeros(16), derivative_bound=1).winding, 1)


if __name__ == "__main__":
    unittest.main()
