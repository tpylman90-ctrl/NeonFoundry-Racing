"""Synthetic tests for the no-cost geometry review engine.

These run even without Blender or AI weights; the CI job installs Pillow/numpy.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

try:
    import numpy as np
    from PIL import Image
    from geometry_vision import (
        bounds, compare_landmarks, compare_masks, load_rgba_and_mask, main,
    )
    DEPS_READY = True
except ImportError:
    DEPS_READY = False


@unittest.skipUnless(DEPS_READY, "Optional Pillow/numpy are not installed")
class GeometryVisionTests(unittest.TestCase):
    def test_exact_silhouette_is_perfect(self):
        a = np.zeros((100, 120), dtype=bool)
        a[10:60, 20:100] = True
        result = compare_masks(a, a.copy())
        self.assertEqual(result["silhouette_iou"], 1.0)
        self.assertEqual(result["bbox_width_error_pct"], 0.0)
        self.assertEqual(result["bbox_height_error_pct"], 0.0)
        self.assertEqual(bounds(a), [20, 10, 100, 60])

    def test_wider_render_is_detected(self):
        a = np.zeros((100, 120), dtype=bool)
        b = np.zeros_like(a)
        a[10:60, 20:100] = True
        b[10:60, 15:105] = True
        result = compare_masks(a, b)
        self.assertGreater(result["bbox_width_error_pct"], 0)
        self.assertLess(result["silhouette_iou"], 1.0)
        self.assertEqual(result["bbox_height_error_pct"], 0)

    def test_shrinking_a_vehicle_reduces_reference_coverage(self):
        # A smaller rendered shape can have perfect precision while missing
        # important canopy/wing regions. The score must expose that loss.
        reference = np.zeros((100, 120), dtype=bool)
        model = np.zeros_like(reference)
        reference[10:90, 10:110] = True
        model[20:80, 30:90] = True
        result = compare_masks(reference, model)
        self.assertEqual(result["silhouette_precision"], 1.0)
        self.assertLess(result["silhouette_recall"], 0.5)
        self.assertGreater(result["missing_reference_pixels"], 0)
        self.assertEqual(result["excess_render_pixels"], 0)
        self.assertLess(result["silhouette_f2_recall_weighted"], 0.6)

    def test_different_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            compare_masks(np.ones((10, 10), dtype=bool), np.ones((20, 20), dtype=bool))

    def test_explicit_mask_required_for_rgb_studio(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "studio.png"
            Image.new("RGB", (32, 32), "gray").save(p)
            with self.assertRaisesRegex(ValueError, "explicit black/white mask"):
                load_rgba_and_mask(p)

    def test_known_calibration_and_landmarks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "landmarks.json"
            path.write_text(json.dumps({
                "camera": "orthographic",
                "reference": {"nose": [10, 50], "tail": [110, 50], "wing": [60, 20]},
                "render": {"nose": [10, 50], "tail": [110, 50], "wing": [65, 20]},
                "calibration": {"point_a": "nose", "point_b": "tail", "distance_m": 7.2},
            }))
            result = compare_landmarks(path)
            self.assertAlmostEqual(result["calibration_m_per_px"], 0.072)
            self.assertEqual(result["landmarks"]["wing"]["projected_delta_m"], [0.36, 0.0])

    def test_perspective_calibration_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "landmarks.json"
            path.write_text(json.dumps({
                "camera": "perspective",
                "reference": {"a": [10, 10], "b": [20, 10]},
                "render": {"a": [10, 10], "b": [20, 10]},
                "calibration": {"point_a": "a", "point_b": "b", "distance_m": 1},
            }))
            with self.assertRaisesRegex(ValueError, "orthographic"):
                compare_landmarks(path)

    def test_cli_creates_measured_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, xshift in (("reference", 0), ("render", 3)):
                pixels = np.zeros((64, 64, 4), dtype=np.uint8)
                pixels[15:55, 8 + xshift:50 + xshift] = [150, 150, 150, 255]
                Image.fromarray(pixels, "RGBA").save(root / (name + ".png"))
            main([
                "--reference", str(root / "reference.png"),
                "--render", str(root / "render.png"),
                "--out", str(root / "review"),
            ])
            self.assertTrue((root / "review/silhouette_overlay.png").is_file())
            report = json.loads((root / "review/geometry_review.json").read_text())
            self.assertLess(report["metrics"]["silhouette_iou"], 1)
            self.assertIn("requires explicit owner", report["gate_approval"])


if __name__ == "__main__":
    unittest.main()
