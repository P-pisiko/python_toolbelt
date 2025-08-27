"""
COD4 Blender camera importer
─────────────────────────────-
"""
import bpy
import csv
import math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

# ────────────────────────────────
# SETTINGS (change CSV_PATH & Fps etc.)
# ────────────────────────────────
CSV_PATH      = Path(r"C:\Users\<YOUR-USERNAME>\positions.csv")  # <-- change me pls :/
RECORD_FPS    = 125
INCH_TO_METRE = 0.0254
CAMERA_NAME   = "Camera"
FLIP_Y        = False
# threads for parsing/convert; keep to cpu count-ish
WORKERS = 8
# ────────────────────────────────

scene = bpy.context.scene
scene.render.fps = RECORD_FPS
scene.render.fps_base = 1.0

if CAMERA_NAME in bpy.data.objects:
    cam = bpy.data.objects[CAMERA_NAME]
else:
    cam_data = bpy.data.cameras.new(CAMERA_NAME)
    cam = bpy.data.objects.new(CAMERA_NAME, cam_data)
    bpy.context.scene.collection.objects.link(cam)

cam.rotation_mode = 'XYZ'

def cod4_pitch_to_blender(pitch_deg: float) -> float:
    signed = -pitch_deg if pitch_deg <= 85 else 360.0 - pitch_deg
    return math.radians(signed)

def cod4_yaw_to_blender(yaw_deg: float) -> float:
    return math.radians(yaw_deg)

rows = []
with CSV_PATH.open(newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# conversion function
def convert_row(row) -> Tuple[int, Tuple[float,float,float], Tuple[float,float,float]]:
    frame_idx = int(row["frame"])
    x = float(row["x"]) * INCH_TO_METRE
    y_raw = float(row["y"])
    y = (-y_raw if FLIP_Y else y_raw) * INCH_TO_METRE
    z = float(row["z"]) * INCH_TO_METRE

    pitch = cod4_pitch_to_blender(float(row["pitch"]))
    pitch = pitch + math.radians(90.0)
    yaw   = cod4_yaw_to_blender(float(row["yaw"]))
    yaw = yaw - math.radians(90.0)
    roll  = 0.0

    # rotation_euler is (X, Y, Z)
    rot = (pitch, 0.0, yaw)
    loc = (x, y, z)
    return frame_idx, loc, rot

# run conversions in threadpool
converted: List[Tuple[int, Tuple[float,float,float], Tuple[float,float,float]]] = []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for result in ex.map(convert_row, rows):
        converted.append(result)

converted.sort(key=lambda r: r[0])

if not converted:
    print("No rows found in CSV.")
else:
    max_frame = max(r[0] for r in converted)

    # Create action & f-curves (must be done on main thread)
    cam.animation_data_create()
    action = bpy.data.actions.new(name=f"{CAMERA_NAME}_import_action")
    cam.animation_data.action = action

    # prepare 6 fcurves: location[0..2], rotation_euler[0..2]
    fcurves = []
    for i in range(3):
        fcurves.append(action.fcurves.new(data_path="location", index=i))
    for i in range(3):
        fcurves.append(action.fcurves.new(data_path="rotation_euler", index=i))

    # Insert keyframe points directly into fcurves (much faster than keyframe_insert)
    # Note: keyframe_points.insert(frame, value, options={'FAST'}) is available in Blender >= 2.80
    for frame_idx, loc, rot in converted:
        # location
        fcurves[0].keyframe_points.insert(frame_idx, loc[0], options={'FAST'})
        fcurves[1].keyframe_points.insert(frame_idx, loc[1], options={'FAST'})
        fcurves[2].keyframe_points.insert(frame_idx, loc[2], options={'FAST'})
        # rotation
        fcurves[3].keyframe_points.insert(frame_idx, rot[0], options={'FAST'})
        fcurves[4].keyframe_points.insert(frame_idx, rot[1], options={'FAST'})
        fcurves[5].keyframe_points.insert(frame_idx, rot[2], options={'FAST'})

    for fc in fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

    scene.frame_start = 0
    scene.frame_end = max_frame

    print(f"Imported {len(converted)} frames into action '{action.name}' (frame range 0..{max_frame}).")