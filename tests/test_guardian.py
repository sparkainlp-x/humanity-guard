"""Tests for humanity-guard v0.1.0. Run: python -m unittest discover -s tests -v

SYNTHETIC. All scenes are generated; no real sensor is involved.
"""

import unittest

import numpy as np

from humanity_guard.engine import GuardianEngine
from humanity_guard.humangate import HumanGate
from humanity_guard.refusal import RefusalGate
from humanity_guard.sensing import coherence, generate_scene, sharpness
from humanity_guard.verify import brier, calibration_points, score_event


class TestSensing(unittest.TestCase):
    def test_real_scenes_are_coherent_and_decoys_are_not(self):
        rng = np.random.default_rng(7)
        real = [coherence(*generate_scene(rng, "real")) for _ in range(30)]
        decoy = [coherence(*generate_scene(rng, "decoy")) for _ in range(30)]
        self.assertGreater(min(real), 0.7)
        self.assertLess(max(decoy), 0.5)

    def test_sharpness_lie_decoy_is_sharp_but_incoherent(self):
        rng = np.random.default_rng(7)
        amp, ph = generate_scene(rng, "decoy")
        self.assertGreater(sharpness(amp), 1.0)
        self.assertLess(coherence(amp, ph), 0.5)


class TestVerify(unittest.TestCase):
    def test_brier_and_points_match_crystallize(self):
        self.assertAlmostEqual(brier(0.75, True), 0.0625)
        self.assertAlmostEqual(calibration_points(0.75, True), 75.0)
        self.assertAlmostEqual(calibration_points(0.5, True), 0.0)
        self.assertLess(calibration_points(0.99, False), 0)

    def test_event_scores_exactly_two_forecasts(self):
        # Three looks taken, but only two forecasts scored: the cost is
        # per look, the forecasts are exactly two. Scoring every look
        # would give a different (inflated) number; pin the two-forecast rule.
        scored = score_event(0.75, 0.75, True, n_looks=3)
        self.assertAlmostEqual(scored["score"], 75.0 - 0.8 * 3)


class TestRefusal(unittest.TestCase):
    def test_gate_refuses_decoys_and_accepts_real(self):
        eng = GuardianEngine(seed=42)
        for kind in ("real", "decoy", "glare", "noise"):
            event = eng.process(kind)
            if kind == "real":
                self.assertEqual(event["decision"], "accepted")
            else:
                self.assertEqual(event["decision"], "refused")

    def test_accuracy_on_accepted_is_high(self):
        eng = GuardianEngine(seed=123)
        for _ in range(10):
            for kind in ("real", "decoy", "glare", "noise"):
                eng.process(kind)
        acc = eng.summary()["accuracy_on_accepted"]
        self.assertIsNotNone(acc)
        self.assertGreaterEqual(acc, 0.9)


class TestHumanGate(unittest.TestCase):
    def test_unapproved_action_is_denied_and_does_nothing(self):
        gate = HumanGate()
        req = gate.request("alert")
        result = gate.execute(req)
        self.assertEqual(result["status"], "denied")
        self.assertTrue(gate.verify_chain())

    def test_alert_needs_one_approver_decoy_needs_two(self):
        gate = HumanGate()
        req = gate.request("alert")
        gate.approve(req, "operator")
        self.assertEqual(gate.execute(req)["status"], "executed")
        req2 = gate.request("decoy")
        gate.approve(req2, "operator")
        self.assertEqual(gate.execute(req2)["status"], "denied")
        gate.approve(req2, "supervisor")
        self.assertEqual(gate.execute(req2)["status"], "executed")

    def test_ledger_tamper_is_detected(self):
        gate = HumanGate()
        req = gate.request("alert")
        gate.approve(req, "operator")
        gate.execute(req)
        self.assertTrue(gate.verify_chain())
        gate.ledger[0]["entry"]["action"] = "decoy"
        self.assertFalse(gate.verify_chain())


class TestEngine(unittest.TestCase):
    def test_accepted_event_opens_request_and_executes_on_approval(self):
        eng = GuardianEngine(seed=42)
        event = eng.process("real")
        self.assertEqual(event["decision"], "accepted")
        self.assertIsNotNone(event["request_id"])
        eng.human_gate.approve(event["request_id"], "operator")
        result = eng.human_gate.execute(event["request_id"])
        self.assertEqual(result["status"], "executed")

    def test_refused_event_opens_no_request(self):
        eng = GuardianEngine(seed=42)
        event = eng.process("decoy")
        self.assertEqual(event["decision"], "refused")
        self.assertIsNone(event["request_id"])

    def test_determinism_same_seed_same_events(self):
        a = GuardianEngine(seed=42)
        b = GuardianEngine(seed=42)
        for kind in ("real", "decoy", "glare", "noise"):
            ea, eb = a.process(kind), b.process(kind)
            self.assertEqual(ea["decision"], eb["decision"])
            self.assertAlmostEqual(ea["mean_coherence"], eb["mean_coherence"])
            self.assertAlmostEqual(ea["score"], eb["score"])

    def test_no_lethal_action_exists(self):
        from humanity_guard.humangate import QUORUM

        self.assertEqual(set(QUORUM.keys()), {"alert", "decoy"})


if __name__ == "__main__":
    unittest.main()
