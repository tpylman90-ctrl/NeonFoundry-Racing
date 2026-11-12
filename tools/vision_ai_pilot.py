#!/usr/bin/env python3
"""CPU pilot: confirm actual DINOv2 and Depth Anything V2 inference on real NF-H01 renders.

Input images MUST be real Blender Gate 02 artifact renders, not synthetic AI images.
The user's uploaded concept/reference photos remain outside this PUBLIC repository.
The report is diagnostic; it never alters a mesh, approximates physical dimensions
from monocular depth or advances the owner's locked approval stage.
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModel, AutoModelForDepthEstimation

BASE = Path(os.environ.get("NFR_SOURCE", "build/hero_01_gate02"))
OUT = Path(os.environ.get("NFR_REPORT", "build/vision_ai_pilot"))
OUT.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(2)
source = Image.open(BASE / "04_starboard_side.png").convert("RGB")
rear = Image.open(BASE / "08_rear_three_quarter.png").convert("RGB")
# Deliberately shifted and cropped version tests feature tolerance while
# preserving provenance of real Blender-generated imagery.
w, h = source.size
altered = source.crop((int(w * .07), int(h * .035), int(w * .93), int(h * .965))).resize((w, h), Image.Resampling.BICUBIC)

dino_id = "facebook/dinov2-small"
dino_p = AutoImageProcessor.from_pretrained(dino_id)
dino = AutoModel.from_pretrained(dino_id).eval()
with torch.inference_mode():
    token = dino(**dino_p(images=[source, altered, rear], return_tensors="pt")).last_hidden_state
    cls = F.normalize(token[:, 0, :], dim=1)
    patches = F.normalize(token[:, 1:, :], dim=2)
    similarity = (cls @ cls.T).cpu().numpy()
    patch_sim = (patches[0] * patches[1]).sum(-1).mean().item()
del dino, dino_p, token
print("NFR_DINOV2_INFERENCE_OK", flush=True)

depth_id = "depth-anything/Depth-Anything-V2-Small-hf"
depth_p = AutoImageProcessor.from_pretrained(depth_id)
depth_m = AutoModelForDepthEstimation.from_pretrained(depth_id).eval()
depth_stats = []
for index, image in enumerate((source, rear)):
    with torch.inference_mode():
        result = depth_m(**depth_p(images=image, return_tensors="pt"))
        d = depth_p.post_process_depth_estimation(
            result, target_sizes=[(image.height, image.width)]
        )[0]["predicted_depth"].cpu().numpy()
    if not np.isfinite(d).all() or np.ptp(d) < 1e-6:
        raise RuntimeError("Non-finite or constant relative depth prediction")
    q01, q99 = (float(x) for x in np.percentile(d, [1, 99]))
    normalized = np.uint8(np.clip((d - q01) / max(q99 - q01, 1e-9) * 255, 0, 255))
    name = ("side", "rear_three_quarter")[index]
    Image.fromarray(normalized, "L").save(OUT / (name + "_relative_depth.png"))
    depth_stats.append({"view": name, "p01": round(q01, 6), "p99": round(q99, 6),
                        "range": round(float(np.ptp(d)), 6)})
del depth_m, depth_p
print("NFR_DEPTH_ANYTHING_V2_INFERENCE_OK", flush=True)

report = {
    "asset": "NF-H01", "gate": 2,
    "source_images": ["04_starboard_side.png", "08_rear_three_quarter.png"],
    "dino_model": dino_id,
    "dino_self_similarity": round(float(similarity[0, 0]), 6),
    "dino_crop_similarity": round(float(similarity[0, 1]), 6),
    "dino_different_view_similarity": round(float(similarity[0, 2]), 6),
    "dino_same_patch_crop_similarity": round(float(patch_sim), 6),
    "depth_model": depth_id,
    "depth": depth_stats,
    "interpretation": "DINO values are features, not geometry; relative depth cannot recover metric dimensions or occluded geometry",
    "user_reference_image_used": False,
    "craft_geometry_modified": False,
    "gate_approval": "pending owner silhouette inspection",
}
(OUT / "AI_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
print("NFR_AI_PILOT_OK", json.dumps(report, sort_keys=True), flush=True)
