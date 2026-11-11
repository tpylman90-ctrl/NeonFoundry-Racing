#!/usr/bin/env python3
"""Reference-to-geometry diagnostics for aligned vehicle views.

This tool compares actual reference and Blender-rendered silhouettes. DINOv2
and relative depth inference are OPTIONAL visual diagnostics, not measuring
instruments. Never use an AI score to certify approval or advance craft gates.
"""
import argparse
import json
import math
from pathlib import Path


def load_rgba_and_mask(image_path, mask_path=None):
    from PIL import Image
    import numpy as np
    im = Image.open(image_path).convert("RGBA")
    if mask_path:
        mask_im = Image.open(mask_path).convert("L")
        if mask_im.size != im.size:
            raise ValueError("Mask and image dimensions differ: " + str(image_path))
        mask = np.asarray(mask_im, dtype=np.uint8) >= 128
    else:
        alpha = np.asarray(im.getchannel("A"), dtype=np.uint8)
        if alpha.min() == 255:
            raise ValueError(
                "An explicit black/white mask or transparent PNG is required for " + str(image_path)
                + "; RGB studio images are not reliable automatic silhouettes."
            )
        mask = alpha >= 128
    if not mask.any():
        raise ValueError("Empty foreground mask: " + str(image_path))
    return im, mask


def bounds(mask):
    import numpy as np
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        raise ValueError("Empty foreground")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def compare_masks(reference, render):
    import numpy as np
    if reference.shape != render.shape:
        raise ValueError("Reference and render masks must share the same image dimensions")
    rb, mb = bounds(reference), bounds(render)
    intersection = np.logical_and(reference, render).sum()
    union = np.logical_or(reference, render).sum()
    wref, href = rb[2] - rb[0], rb[3] - rb[1]
    wmod, hmod = mb[2] - mb[0], mb[3] - mb[1]
    rows = {}
    # Compare cross-section widths at fixed image Y positions; missing spans
    # are reported as null rather than mistakenly scored as zero.
    for fraction in (.1, .25, .5, .75, .9):
        y = min(reference.shape[0] - 1, max(0, int(rb[1] + fraction * href)))
        a = np.flatnonzero(reference[y])
        b = np.flatnonzero(render[y])
        rows[str(fraction)] = {
            "y_px": int(y),
            "reference_width_px": int(a[-1] - a[0] + 1) if a.size else None,
            "render_width_px": int(b[-1] - b[0] + 1) if b.size else None,
        }
    return {
        "silhouette_iou": round(float(intersection / union), 6) if union else 0.0,
        "reference_bbox_px": rb,
        "render_bbox_px": mb,
        "bbox_width_error_pct": round(100.0 * (wmod / wref - 1), 3),
        "bbox_height_error_pct": round(100.0 * (hmod / href - 1), 3),
        "centroid_bbox_offset_px": [
            round((mb[0] + mb[2] - rb[0] - rb[2]) / 2, 2),
            round((mb[1] + mb[3] - rb[1] - rb[3]) / 2, 2),
        ],
        "cross_section_widths": rows,
    }


def compare_landmarks(path):
    """Only a known orthographic calibration permits projected meter estimates.

    JSON: {"camera":"orthographic", "reference":{"a":[10,20],...},
    "render":{"a":[11,20],...},
    "calibration":{"point_a":"a","point_b":"b","distance_m":7.2}}
    """
    data = json.loads(Path(path).read_text())
    ref = data.get("reference", {})
    model = data.get("render", {})
    shared = sorted(set(ref) & set(model))
    output = {"landmarks": {}, "calibration_m_per_px": None}
    scale = None
    cal = data.get("calibration")
    if cal:
        if data.get("camera") != "orthographic":
            raise ValueError("Meter calibration requires orthographic view, not perspective")
        a, b = cal["point_a"], cal["point_b"]
        if a not in ref or b not in ref:
            raise ValueError("Calibration points absent from reference landmarks")
        projected = math.dist(ref[a], ref[b])
        if projected < 1:
            raise ValueError("Calibration span must be at least one pixel")
        if cal["distance_m"] <= 0:
            raise ValueError("Known distance must be positive")
        scale = cal["distance_m"] / projected
        output["calibration_m_per_px"] = round(scale, 8)
    for name in shared:
        d = [float(model[name][i] - ref[name][i]) for i in (0, 1)]
        output["landmarks"][name] = {
            "delta_px": d,
            "distance_px": round(math.hypot(*d), 3),
            "projected_delta_m": [round(x * scale, 4) for x in d] if scale else None,
        }
    return output


def overlay(reference, render, output):
    import numpy as np
    from PIL import Image
    h, w = reference.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    overlap = reference & render
    rgb[reference & ~render] = (247, 74, 84)  # missing model area
    rgb[render & ~reference] = (49, 205, 232)  # excess model area
    rgb[overlap] = (218, 218, 218)            # agreement
    Image.fromarray(rgb, "RGB").save(output)


def dinov2_similarity(image_a, image_b):
    import torch
    from transformers import AutoImageProcessor, AutoModel
    name = "facebook/dinov2-small"
    processor = AutoImageProcessor.from_pretrained(name)
    model = AutoModel.from_pretrained(name).eval()
    inputs = processor(images=[image_a.convert("RGB"), image_b.convert("RGB")], return_tensors="pt")
    with torch.inference_mode():
        tokens = model(**inputs).last_hidden_state
        cls = torch.nn.functional.normalize(tokens[:, 0, :], dim=-1)
        patches = torch.nn.functional.normalize(tokens[:, 1:, :], dim=-1)
        global_cosine = torch.sum(cls[0] * cls[1]).item()
        patch_cosine = (patches[0] * patches[1]).sum(dim=-1).mean().item()
    return {
        "model": name,
        "global_cosine": round(global_cosine, 5),
        "same_position_patch_cosine": round(patch_cosine, 5),
        "warning": "Visual feature similarity, NOT geometric accuracy or dimensions; camera alignment required.",
    }


def infer_relative_depth(image, output):
    import numpy as np
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    name = "depth-anything/Depth-Anything-V2-Small-hf"
    processor = AutoImageProcessor.from_pretrained(name)
    model = AutoModelForDepthEstimation.from_pretrained(name).eval()
    inputs = processor(images=image.convert("RGB"), return_tensors="pt")
    with torch.inference_mode():
        pred = model(**inputs)
        depth = processor.post_process_depth_estimation(
            pred, target_sizes=[(image.height, image.width)]
        )[0]["predicted_depth"].cpu().numpy()
    lo, hi = float(np.min(depth)), float(np.max(depth))
    image8 = np.uint8(np.clip((depth - lo) / max(hi - lo, 1e-8) * 255, 0, 255))
    Image.fromarray(image8, "L").save(output)
    return {"model": name, "depth_map": Path(output).name,
            "warning": "Relative monocular depth, not metric depth."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--render", type=Path, required=True)
    parser.add_argument("--reference-mask", type=Path)
    parser.add_argument("--render-mask", type=Path)
    parser.add_argument("--landmarks", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dino", action="store_true", help="Opt-in CPU DINOv2 comparison (downloads model)")
    parser.add_argument("--depth", action="store_true", help="Opt-in CPU relative depth (downloads model)")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    reference_im, reference_mask = load_rgba_and_mask(args.reference, args.reference_mask)
    render_im, render_mask = load_rgba_and_mask(args.render, args.render_mask)
    report = {
        "scope": "aligned 2D reference/render; no automatic 3D reconstruction",
        "reference": args.reference.name,
        "render": args.render.name,
        "metrics": compare_masks(reference_mask, render_mask),
        "gate_approval": "UNTOUCHED — requires explicit owner visual review",
    }
    overlay(reference_mask, render_mask, args.out / "silhouette_overlay.png")
    if args.landmarks:
        report["landmark_comparison"] = compare_landmarks(args.landmarks)
    if args.dino:
        report["dino"] = dinov2_similarity(reference_im, render_im)
    if args.depth:
        report["reference_relative_depth"] = infer_relative_depth(
            reference_im, args.out / "reference_relative_depth.png")
        report["render_relative_depth"] = infer_relative_depth(
            render_im, args.out / "render_relative_depth.png")
    (args.out / "geometry_review.json").write_text(json.dumps(report, indent=2) + "\n")
    print("NFR_GEOMETRY_REVIEW_OK", json.dumps(report["metrics"], sort_keys=True))


if __name__ == "__main__":
    main()
