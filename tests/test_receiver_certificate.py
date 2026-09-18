import unittest

import numpy as np

from toposense_sim.certificate import Decision, certify_observation, evaluate_baseline
from toposense_sim.receiver import acquire_adaptive, acquire_uniform


class ReceiverCertificateTests(unittest.TestCase):
    def test_uniform_and_adaptive_replay_are_exact_and_budgeted(self) -> None:
        for acquire in (acquire_uniform, acquire_adaptive):
            first = acquire(13, "nominal")
            second = acquire(13, "nominal")
            self.assertEqual(first.attempted_count, 32)
            self.assertTrue(np.array_equal(first.stokes, second.stokes))
            self.assertTrue(np.array_equal(first.nominal_angles, second.nominal_angles))

    def test_clean_source_loop_can_be_certified(self) -> None:
        observation = acquire_uniform(3, "nominal")
        result = certify_observation(observation, method="global_certificate", local_uncertainty=False, support_gate=False)
        self.assertEqual(result.decision, Decision.RELEASE)
        self.assertTrue(result.correct)

    def test_support_gate_erases_deliberately_shifted_example(self) -> None:
        observation = acquire_adaptive(0, "sector_dropout")
        gated = certify_observation(observation, support_gate=True)
        ungated = certify_observation(observation, method="adaptive_no_support", support_gate=False)
        self.assertEqual(gated.decision, Decision.ERASURE)
        self.assertIn(ungated.decision, (Decision.RELEASE, Decision.ERASURE))

    def test_oracle_is_diagnostic_and_always_correct(self) -> None:
        observation = acquire_uniform(9, "compound_shift")
        oracle = evaluate_baseline(observation, "oracle_dense")
        self.assertTrue(oracle.correct)
        self.assertEqual(oracle.winding, observation.field.true_winding)
