"""CPU-only TripoSR marching cubes adapter for free GitHub Actions runners.

Replaces the native torchmcubes extension only inside the experiment checkout.
scikit-image: BSD-3-Clause. TripoSR: MIT. No production game code is altered.
"""
from __future__ import annotations

import numpy as np
import torch
from skimage.measure import marching_cubes as _skimage_marching_cubes


def marching_cubes(volume: torch.Tensor, level: float):
    if volume.ndim != 3:
        raise ValueError("marching_cubes expects a 3D tensor")
    values = np.ascontiguousarray(volume.detach().float().cpu().numpy())
    vertices, faces, _normals, _values = _skimage_marching_cubes(
        values, level=float(level), allow_degenerate=False
    )
    return (
        torch.from_numpy(np.ascontiguousarray(vertices, dtype=np.float32)),
        torch.from_numpy(np.ascontiguousarray(faces, dtype=np.int64)),
    )


def self_test():
    grid = np.mgrid[-1:1:24j, -1:1:24j, -1:1:24j]
    sphere = torch.from_numpy(
        (grid[0] ** 2 + grid[1] ** 2 + grid[2] ** 2 - 0.55 ** 2).astype(np.float32)
    )
    vertices, faces = marching_cubes(sphere, 0.0)
    assert len(vertices) > 100 and len(faces) > 100
    assert vertices.ndim == 2 and vertices.shape[1] == 3
    assert faces.ndim == 2 and faces.shape[1] == 3
    assert torch.isfinite(vertices).all()
    assert int(faces.min()) >= 0 and int(faces.max()) < len(vertices)
    print("FORGE_CPU_MARCHING_CUBES_TEST_OK", len(vertices), len(faces), flush=True)


if __name__ == "__main__":
    self_test()
