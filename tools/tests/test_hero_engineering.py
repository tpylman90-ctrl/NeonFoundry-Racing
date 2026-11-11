"""Gate 01 geometry design checks, not a substitute for the owner's visual approval."""
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC_PATH=ROOT/"art/hero_01/01_PROPORTIONS.json"
PROGRESS_PATH=ROOT/"art/hero_01/progress.json"


class TestHeroEngineeringPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads(SPEC_PATH.read_text())
        cls.progress=json.loads(PROGRESS_PATH.read_text())

    def test_reference_is_original_and_not_claimed_as_measured(self):
        s=self.spec
        self.assertEqual(s["craft_id"],"NF-H01")
        self.assertEqual(s["approval_status"],"approved_for_blockout")
        self.assertEqual(s["units"],"meters")
        self.assertEqual(s["coordinate_system"]["forward"],"-Y")

    def test_body_station_monotonic_and_closed(self):
        s=self.spec
        pts=s["primary_shell_stations"]
        self.assertGreaterEqual(len(pts),8)
        self.assertEqual(pts[0]["y"],-3.6)
        self.assertEqual(pts[-1]["y"],3.6)
        for a,b in zip(pts,pts[1:]):
            self.assertLess(a["y"],b["y"])
        for p in pts:
            self.assertGreater(p["half_width"],0)
            self.assertGreater(p["top_z"],p["bottom_z"])
            self.assertGreaterEqual(p["bottom_z"],0)
        self.assertTrue(math.isclose(max(p["half_width"] for p in pts)*2,
                                        s["proposed_envelope"]["hull_max_width_m"]))

    def test_propulsion_and_lift_symmetry(self):
        spec=self.spec
        nozzles=spec["main_nozzles"]
        self.assertAlmostEqual(nozzles["left_x"],-nozzles["right_x"])
        self.assertAlmostEqual(nozzles["exit_y"],3.6)
        self.assertGreater(nozzles["outer_diameter_m"],0.85)
        lift=spec["lift_module_packing_approx"]
        self.assertEqual(len(lift),4)
        self.assertEqual({round(p["y"],2) for p in lift},{-1.65,1.8})
        for y in (-1.65,1.8):
            xs=sorted(p["x"] for p in lift if math.isclose(p["y"],y))
            self.assertEqual(len(xs),2)
            self.assertAlmostEqual(xs[0],-xs[1])

    def test_canopy_and_review_scope(self):
        c=self.spec["cockpit"]
        self.assertLess(c["front_y"],c["apex_y"])
        self.assertLess(c["apex_y"],c["rear_y"])
        self.assertEqual(c["pilot_count"],1)
        self.assertEqual(len(self.spec["required_review_views"]),8)
        self.assertTrue(self.spec["next_gate_locked"])

    def test_no_premature_blockout_approval(self):
        p=self.progress
        self.assertIn(str(SPEC_PATH.relative_to(ROOT)),p["gates"][0]["evidence"])
        self.assertEqual(p["gates"][0]["state"],"approved")
        self.assertEqual(p["gates"][0]["user_review"]["decision"],"approved")
        self.assertEqual(p["last_approved_stage"],1)
        self.assertEqual(p["current_stage"],2)
        self.assertEqual(p["gates"][1]["state"],"in_progress")
        self.assertIsNone(p["gates"][1]["user_review"])


if __name__=="__main__":
    unittest.main()
