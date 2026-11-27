"""NFR garage corner-fit, staircase, walk-mode and NF-BW01 verification.

This guards the *specific* regressions observed in actual Android screenshots.
Coordinates in Blender X/Y/Z; Unity maps them to X/Y/-Z.
Requires only Python standard library; runner executes before Blender/Unity.
"""
from pathlib import Path
import math
base=Path(__file__).resolve().parent
gen=(base/"generate_assets.py").read_text()
detail=(base/"upgrade_geometry.py").read_text()
editor=(base.parent.parent/"Assets/Editor/NeonFoundryUnityBuild.cs").read_text()
viewer=(base.parent.parent/"Assets/Scripts/FoundryGarageViewer.cs").read_text()

# Inner wall planes: lateral wall center 17.45 and thickness .35,
# back wall center 18.40 and thickness .35.
right_inner=17.45-.35/2
back_inner=18.40-.35/2
deck_cx,deck_cy=12.5125,13.725
deck_w,deck_len=9.525,9.0
deck_left=deck_cx-deck_w/2
deck_right=deck_cx+deck_w/2
deck_front=deck_cy-deck_len/2
deck_rear=deck_cy+deck_len/2
assert math.isclose(deck_right,right_inner,abs_tol=.002)
assert math.isclose(deck_rear,back_inner,abs_tol=.002)
assert deck_left<7.80 and math.isclose(deck_front,9.225,abs_tol=.002)
assert 'box("DECK | elevated overlook",(12.5125,13.725,DECK_Z),(9.525,9.0,.25)' in gen
assert 'new Vector3(12.5125f,4.35f,-13.725f)' in editor
assert 'new Vector3(9.525f,.25f,9.0f)' in editor
assert 'new Vector3(12.50f, 4.50f, -14.0f)' in editor

# Actual tread top meets true balcony top with a walkable small rise.
n=24;step_run=.46;rise=.184;first_y=-1.20;step_z0=.12
deck_top=4.35+.25/2
step_last_top=step_z0+(n-1)*rise+.16/2
last_y=first_y+(n-1)*step_run
assert 0<deck_top-step_last_top<.10
assert abs(last_y-deck_front)<.25
assert "STAIR_COUNT=24" in gen and 'STAIR_X=9.35' in gen
assert 'for(int i=0;i<24;i++)' in editor
assert 'new Vector3(9.35f,.12f+i*.184f,-(-1.20f+i*.46f))' in editor
assert 'for x in (7.82,10.64,12.02,13.8,15.5,17.19):' in detail
# Guard rails leave room at actual landing and ascend with the treads.
assert 'start=(sx,-1.40,.88)' in detail
assert 'end=(sx,9.67,5.34)' in detail

# Confirm movement no longer relies on raycast finding deck vs tread.
assert 'Mathf.FloorToInt((1.20f-walker.z+.23f)/.46f)' in viewer
assert 'if (inDeck && walker.y >= 5.10f)' in viewer
assert 'new Vector3(9.35f,1.64f,2.65f)' in viewer
assert 'walkYaw = 180f;' in viewer
assert '"STAIR ENTRY"' in viewer

# Stand at first tread and walk toward negative Unity Z; ascent must be
# monotonically increasing and top tread accessible without a >10cm jump.
heights=[]
for i in range(n):
    center_unity_z=-(first_y+i*step_run)
    idx=max(0,min(n-1,math.floor((1.20-center_unity_z+.23)/.46)))
    heights.append(.20+idx*.184)
assert len(heights)==24 and all(a<=b for a,b in zip(heights,heights[1:]))
assert max(abs(heights[i]-(.20+i*rise)) for i in range(n))<.001

# Under-deck service bay, no staircase footprint overlap.
station_x=13.25
station_w=3.8
stair_outer=9.35+1.06
assert (station_x-station_w/2)-stair_outer>.7
assert (station_x+station_w/2)<deck_right
assert 'bayX=13.25f, bayZ=-12.50f, underside=4.225f' in editor
assert 'yaw = index==3?164f' in viewer
assert 'locationIndex==3?3.55f:6.48f' in viewer

print("NF_GARAGE_CORNER_STAIR_STATION_QA_OK", {
    "deck_right_x":deck_right,"wall_inner_x":right_inner,
    "deck_rear_y":deck_rear,"wall_inner_y":back_inner,
    "last_stair_top":round(step_last_top,3),
    "deck_top":round(deck_top,3),
    "stair_to_station_gap":round(station_x-station_w/2-stair_outer,3),
    "stair_slope":"24 steps verified"})
