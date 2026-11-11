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

    def test_menu_startup_and_navigation_sources(self):
        root = (ROOT / "game/project.godot").read_text()
        self.assertIn('run/main_scene="res://scenes/title_menu.tscn"', root)
        menus = (ROOT / "game/scripts/title_menu.gd").read_text()
        for symbol in ["func show_title()", "func show_main_menu()", "func open_settings()", "func _open_section("]:
            self.assertIn(symbol, menus)
        self.assertIn('cfg.save(SETTINGS_FILE)', menus)
        self.assertIn("mobile", root)
        self.assertIn("vulkan", root)

    def test_blender_menu_production_contract(self):
        script = (ROOT / "tools/build_menu_hero.py").read_text()
        ui = (ROOT / "game/scripts/title_menu.gd").read_text()
        self.assertIn("bpy.ops.render.render(write_still=True)", script)
        self.assertIn("bpy.ops.wm.save_as_mainfile", script)
        self.assertIn("Repulsor housing", script)
        self.assertIn("VISIBLE aerial raceway", script)
        self.assertIn("BlenderCinematicBackdrop", ui)
        self.assertIn("func _set_menu_preview(", ui)
        self.assertIn("func _on_motion_changed(", ui)

    def test_android_identity(self):
        s = (ROOT / "game/export_presets.cfg").read_text()
        self.assertIn("com.tpylman.neonfoundryracing.debug", s)
        self.assertNotIn("com.sceneforge", s)

    def test_contract(self):
        subprocess.run([sys.executable, "tools/check_repository.py"],
                       cwd=ROOT, capture_output=True, check=True)


if __name__ == "__main__":
    unittest.main()
