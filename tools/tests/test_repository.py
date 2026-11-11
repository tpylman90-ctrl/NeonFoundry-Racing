import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestFoundation(unittest.TestCase):
    def test_vulkan_project(self):
        s = (ROOT / "game/project.godot").read_text()
        self.assertIn('renderer/rendering_method="mobile"', s)
        self.assertIn('rendering_device/driver.android="vulkan"', s)
        self.assertIn('rendering_device/fallback_to_opengl3=false', s)

    def test_android_identity(self):
        s = (ROOT / "game/export_presets.cfg").read_text()
        self.assertIn("com.tpylman.neonfoundryracing.debug", s)
        self.assertNotIn("com.sceneforge", s)

    def test_contract(self):
        subprocess.run([sys.executable, "tools/check_repository.py"],
                       cwd=ROOT, capture_output=True, check=True)


if __name__ == "__main__":
    unittest.main()
