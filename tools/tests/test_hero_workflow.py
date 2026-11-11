import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from validate_hero_workflow import EXPECTED, validate_status  # noqa: E402


class HeroCraftGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads((ROOT / "art/hero_01/progress.json").read_text())

    def test_current_order_is_locked(self):
        self.assertEqual(len(EXPECTED), 12)
        self.assertEqual(validate_status(copy.deepcopy(self.baseline)), [])

    def test_skip_is_forbidden(self):
        data = copy.deepcopy(self.baseline)
        data["current_stage"] = 4
        self.assertTrue(validate_status(data))

    def test_future_gate_cannot_be_started(self):
        data = copy.deepcopy(self.baseline)
        data["gates"][4]["state"] = "in_progress"
        self.assertTrue(validate_status(data))

    def test_approval_without_evidence_is_rejected(self):
        data = copy.deepcopy(self.baseline)
        data["last_approved_stage"] = 1
        data["current_stage"] = 2
        data["gates"][0]["state"] = "approved"
        data["gates"][1]["state"] = "in_progress"
        self.assertTrue(validate_status(data))

    def test_evidence_requires_named_user_review(self):
        data = copy.deepcopy(self.baseline)
        data["last_approved_stage"] = 1
        data["current_stage"] = 2
        data["gates"][0].update(state="approved", evidence=["art/hero_01/01/spec.md"])
        data["gates"][1]["state"] = "in_progress"
        self.assertTrue(validate_status(data))
        data["gates"][0]["user_review"] = {
            "decision": "approved",
            "reference": "conversation explicit visual review",
            "note": "The user accepted the stage-01 engineering spec",
        }
        self.assertEqual(validate_status(data), [])

    def test_gate_renaming_is_forbidden(self):
        data = copy.deepcopy(self.baseline)
        data["gates"][2]["title"] = "Paint the car"
        self.assertTrue(validate_status(data))


if __name__ == "__main__":
    unittest.main()
