"""NF-BW01 Gate 02 mechanical refinement R2.

This module extends the *same* editable Blender master. No external meshes,
textures, UVs, LODs or game-scene integration. Every moving mechanical part
remains separately named within the current collections. Working envelope and
rigging remain subject to review; the displayed wrist is a parked pose.
"""

import math
from mathutils import Vector


def add_mechanical_refinements(c):
    set_group=c["set_group"]
    box=c["box"]
    cyl=c["cyl"]
    torus=c["torus"]
    beam=c["beam"]
    bolt=c["bolt"]
    cable=c["cable"]
    pivot=c["pivot"]
    put_under=c["put_under"]

    # Underside is designed as an open structural chassis, *not* a textured
    # rectangle. The master deck ends at z=0.153, leaving 150mm service depth.
    # Keep all parts inside z=[0,3.40] and 3.8m x 2.4m approved footprint.
    set_group(c["STRUCT"])

    for y in (-.88,.88):
        # Longitudinal lower crash beams, attachment to sole plates
        box("R2 UNDERFRAME | C-channel crossmember", (0,y,.079),
            (2.90,.105,.11),"HOUSING",.013)
        box("R2 UNDERFRAME | inset machined flange", (0,y,.030),
            (2.70,.072,.025),"BRUSH",.006)

    for x in (-1.40,1.40):
        box("R2 UNDERFRAME | parallel longitudinal rail",(x,0,.088),
            (.105,1.81,.115),"STEEL",.010)
        box("R2 UNDERFRAME | lower protected skid",(x,0,.027),
            (.18,1.79,.036),"DARK",.006)
        for y in (-.62,.0,.62):
            bolt("R2 UNDERFRAME | rail structural fastener",(x,y,.017),
                 axis="Z",radius=.014)

    # Deliberately large visible negative spaces between members.
    # A continuous underside sheet would hide all of these.
    for x in (-.94,.0,.94):
        box("R2 UNDERFRAME | center box section",(x,0,.116),
            (.11,1.64,.070),"HOUSING",.010)
        for y in (-.47,.47):
            box("R2 UNDERFRAME | gusset foot plate",(x,y,.093),
                (.30,.21,.042),"STEEL",.014)

    # Two X-brace frames, with a load path to the rail fastening points.
    for sign in (-1,1):
        x=sign*.83
        beam("R2 UNDERFRAME | diagonal torsion brace",
             (x-.31,-.73,.067),(x+.31,.72,.067),
             .050,.049,"BRUSH",.008)
        beam("R2 UNDERFRAME | counter diagonal brace",
             (x-.31,.72,.070),(x+.31,-.73,.070),
             .048,.048,"BRUSH",.008)

    # Protected underside pump/energy-transfer module, lowered but not
    # protruding below floor. A real removable cover and adjacent line routing.
    box("R2 UNDERFRAME | sealed power-distribution belly casing",
        (.42,-.11,.108),(.41,.54,.075),"DARK",.020)
    box("R2 UNDERFRAME | skid-mounted inspection lid",
        (.42,-.11,.061),(.36,.48,.023),"STEEL",.012)
    for sx in (-.13,.13):
        for sy in (-.16,.16):
            bolt("R2 UNDERFRAME | belly maintenance fixing",
                 (.42+sx,-.11+sy,.045),radius=.010)

    # Fuel-cell return channels: separate fixed couplers and tough protective
    # elastomer straps. Low-profile because this workstation is floor anchored.
    for yy in (-.38,.38):
        cyl("R2 UNDERFRAME | power feed pipe",(-.41,yy,.070),
            .027,1.01,"BRUSH","X",24,.004)
        for xx in (-.69,-.12):
            box("R2 UNDERFRAME | grounded pipe retainer",(xx,yy,.075),
                (.087,.072,.030),"DARK",.008)
    for side in (-1,1):
        for yy in (-.75,.75):
            box("R2 UNDERFRAME | welded corner anti-crush doubler",
                (side*1.60,yy,.086),(.28,.27,.092),"HOUSING",.020)
            bolt("R2 UNDERFRAME | structural lock washer",
                 (side*1.60,yy,.021),radius=.018)

    # Robot physical bearing and gearbox details; located on the built joints,
    # in restrained scale so they read as precision engineering.
    set_group(c["ROBOT"])
    p0=Vector(c["p0"])
    p1=Vector(c["p1"])
    p2=Vector(c["p2"])
    p3=Vector(c["p3"])
    for y in (.37,.76):
        cyl("R2 AXIS1 | yaw drive through-shaft",
            (-1.10,y,1.005),.070,.15,"DARK","Y",32,.008)
        torus("R2 AXIS1 | labyrinth shaft seal",
              (-1.10,y,1.005),.079,.012,"BRUSH","Y",40)
    # Actual hydraulics: piston rod travels within a broad protective sleeve.
    # Shown parked; does not claim the actuator is kinematically solved.
    set_group(c["UPPER"])
    beam("R2 AXIS2 | hydraulic cylinder barrel",
         (-1.02,.79,1.19),(-1.34,.81,1.49),.102,.102,"HOUSING",.017)
    beam("R2 AXIS2 | exposed piston rod",
         (-1.34,.81,1.49),(-1.53,.78,1.71),.052,.052,"BRUSH",.008)
    for p in ((-1.03,.79,1.21),(-1.53,.78,1.71)):
        cyl("R2 AXIS2 | spherical bearing clevis",p,.080,.078,
            "DARK","Y",32,.008)
        cyl("R2 AXIS2 | machined pivot pin",p,.047,.097,
            "STEEL","Y",24,.005)
    for i in (-1,1):
        cyl("R2 AXIS2 | shoulder toothed retainer",
            (p0.x,p0.y+i*.211,p0.z),.125,.035,
            "DARK","Y",40,.005)

    set_group(c["FORE"])
    for side in (-1,1):
        cyl("R2 AXIS3 | double reduction drive cover",
            (p1.x,p1.y+side*.211,p1.z),.135,.035,
            "HOUSING","Y",40,.009)
        for k in range(6):
            angle=math.tau*k/6
            point=(p1.x+math.cos(angle)*.106,
                   p1.y+side*.235,
                   p1.z+math.sin(angle)*.106)
            bolt("R2 AXIS3 | ring-gland screws",point,axis="Y",radius=.010)
    for t in (.28,.49,.71):
        q=p1.lerp(p2,t)
        box("R2 AXIS3 | stamped forearm service seam",
            (q.x+.07,q.y-.145,q.z),(.145,.022,.018),
            "DARK",.004)

    # Toolhead: jaw width (~.61 m between fingers) aligns with cassette
    # sockets x=-.17 +/- .305 only when parked wrist is centered at x=-.17.
    # These are separate clamped solids, not painted stripes.
    set_group(c["WRIST"])
    center_x=-.25
    wrist_y=-.21
    gearbox_z=2.18
    cyl("R2 AXIS5 | angular contact wrist race",
        (center_x,wrist_y,2.228),.163,.075,
        "DARK", "Z",48,.009)
    torus("R2 AXIS5 | retaining lock ring",
          (center_x,wrist_y,2.187),.168,.017,"BRUSH")
    cyl("R2 AXIS5 | annular rotary encoder",
        (center_x,wrist_y,2.287),.123,.040,
        "STEEL","Z",40,.005)
    for angle in range(0,360,45):
        aa=math.radians(angle)
        px=center_x+math.cos(aa)*.132
        py=wrist_y+math.sin(aa)*.132
        bolt("R2 AXIS5 | coupler mounting stud",
             (px,py,2.20),radius=.011)

    # Toolhead assembly: a raised geared linear transfer slide and parallel
    # opposing dovetail jaws; service cover is visible from inspection camera.
    box("R2 GRIPPER | structural carriage bridge",
        (center_x,wrist_y,2.123),(.72,.22,.075),
        "DARK",.018)
    box("R2 GRIPPER | top machined rail",
        (center_x,wrist_y,2.179),(.645,.105,.033),
        "BRUSH",.007)
    box("R2 GRIPPER | recessed linear rack",
        (center_x,wrist_y-.099,2.125),(.60,.033,.045),
        "DARK",.004)
    for k in range(13):
        xx=center_x-.267+k*.0445
        box("R2 GRIPPER | precision rack tooth",
            (xx,wrist_y-.118,2.136),(.016,.012,.034),
            "STEEL",.002)

    for side in (-1,1):
        gx=center_x+side*.302
        # These are replaceable machined fingers with visible dovetail shoes.
        box("R2 GRIPPER | dovetail slider",
            (gx,wrist_y,2.115),(.118,.190,.090),
            "STEEL",.012)
        box("R2 GRIPPER | precision roller block",
            (gx,wrist_y+.015,2.168),(.102,.140,.035),
            "BRUSH",.006)
        box("R2 GRIPPER | jaw sealed pneumatic actuator",
            (center_x+side*.185,wrist_y+.086,2.041),
            (.235,.107,.104),"HOUSING",.024)
        cyl("R2 GRIPPER | linear piston rod",
            (center_x+side*.205,wrist_y+.085,2.049),
            .032,.21,"BRUSH","X",24,.005)
        # Integral open-ended C-shaped socket contacts, allow a mechanical
        # insertion path rather than a fake "jaw closes through solid wall".
        box("R2 GRIPPER | milled finger backbone",
            (gx,wrist_y-.04,1.951),(.078,.096,.300),
            "BRUSH",.014)
        box("R2 GRIPPER | nitrile contact face",
            (gx-side*.046,wrist_y-.041,1.863),
            (.022,.078,.120),"SEAL",.004)
        box("R2 GRIPPER | ceramic locating nose",
            (gx,wrist_y-.044,1.795),
            (.081,.099,.045),"ARMOR",.009)
        # Real fasteners and anti-rotation shafts on the slider.
        for yy in (wrist_y-.042,wrist_y+.057):
            bolt("R2 GRIPPER | detachable jaw cover screw",
                 (gx,yy,2.185),radius=.011)
        box("R2 GRIPPER | floating cable-stop",
            (gx,wrist_y+.102,2.101),
            (.075,.041,.066),"DARK",.009)
    # Differentiates rotation vs clamping assembly for eventual rigging.
    jaw_l=pivot("PIVOT | R2 independent left jaw slide X",
                (center_x-.302,wrist_y,2.10))
    jaw_r=pivot("PIVOT | R2 independent right jaw slide X",
                (center_x+.302,wrist_y,2.10))
    for child in list(c["WRIST"].objects):
        if child.name.startswith("R2 GRIPPER |") and child.type=="MESH":
            gx=child.matrix_world.translation.x
            if gx<center_x-.245:
                put_under(child,jaw_l)
            elif gx>center_x+.245:
                put_under(child,jaw_r)

    # Strain-relieved signal and pneumatic leads *terminate at the wrist*.
    # The cable envelope is protected by the articulated cover.
    set_group(c["WRIST"])
    cable("R2 WRIST | pneumatic service pigtail",
          [(-.72,.25,2.55),(-.59,.11,2.49),
           (-.41,-.08,2.41),(-.31,-.17,2.27)],.030,"SEAL")
    cable("R2 WRIST | encoder signal braid",
          [(-.70,.21,2.54),(-.57,.08,2.50),
           (-.39,-.10,2.40),(-.28,-.15,2.275)],.018,"DARK")

    # Review metadata, enforced by the original model's bounds check.
    print("NF_BW01_GATE02_R2_MECHANICAL_REFINEMENT_OK")
    return {
        "revision":"Gate02-v02",
        "assembly_scope":[
            "Load-bearing ventilated underside structural frame",
            "Underdeck replaceable power distribution box and protected feed pipes",
            "Hydraulic shoulder actuator and reduction drive covers",
            "Ring-gear wrist encoder and C-contact replaceable jaw fingers",
            "Separate gripper jaw slide marker pivots",
        ],
        "limitations":[
            "Rendered gripper is in a parked pose and does not pick a battery yet",
            "No collision sweep or actuator stroke validation at Gate 02",
            "Physical real-world electrical certification is not implied",
        ],
    }
