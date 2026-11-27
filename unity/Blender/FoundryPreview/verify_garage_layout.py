"""Strict layout contract for the NFR raised-deck and NF-BW01 review bay.

Standard Python only. Coordinates are in Blender X/Y/Z and are converted to
Unity X/Y-up/-Z by the existing OBJ exporter; this verifies world-space
clearances independently of materials and Unity compilation.
"""
from pathlib import Path
import math
base=Path(__file__).resolve().parent
generator=(base/"generate_assets.py").read_text()
upgrades=(base/"upgrade_geometry.py").read_text()
editor=(base.parent.parent/"Assets/Editor/NeonFoundryUnityBuild.cs").read_text()
assert "DECK_Z=4.35" in generator
assert "STAIR_X=9.35" in generator
assert "STAIR_COUNT=24" in generator
assert "STAIR_STEP_RUN=.46" in generator
assert "STAIR_RISE=.184" in generator
assert 'new Vector3(11.8f,4.35f,-12.5f)' in editor
assert 'for(int i=0;i<24;i++)' in editor
assert 'new Vector3(9.35f,.12f+i*.184f,-(-1.20f+i*.46f))' in editor
assert 'bayX=13.25f, bayZ=-12.50f, underside=4.225f' in editor
assert '(( -14.3,6.5)' not in upgrades # harmless: do not assume an old tuple
assert '(6.15,12.2)' in upgrades
assert 'for x in (-14,16.25)' in generator
deck_top=4.35+.25/2
deck_underside=4.35-.25/2
last_stair_top=.12+23*.184+.16/2
assert 0<deck_top-last_stair_top<.10,(deck_top,last_stair_top)
# Top step should extend into the beginning of the raised deck by a little.
first_y=-1.20; last_y=first_y+23*.46
deck_front_y=12.50-6.55/2
assert abs(last_y-deck_front_y)<.25,(last_y,deck_front_y)
# Station width from prior source bbox estimate 3.8m, fits between stair
# outer guard and perimeter near x=17.275 while remaining under the deck.
stair_right=9.35+1.06
station_left=13.25-3.8/2
station_right=13.25+3.8/2
assert station_left-stair_right>.70,(station_left,stair_right)
assert station_right<15.5
assert deck_underside>4.2
print("NF_RAISED_DECK_LAYOUT_QA_OK",{
 "deck_top_m":round(deck_top,3),
 "deck_underside_m":round(deck_underside,3),
 "last_stair_top_m":round(last_stair_top,3),
 "upper_landing_gap_m":round(deck_top-last_stair_top,3),
 "station_to_stair_guard_clearance_m":round(station_left-stair_right,3),
 "station_bay_x_m":13.25,
 "station_bay_unity_z_m":-12.5})
