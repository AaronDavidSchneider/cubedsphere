import xarray as xr
import xgcm
import numpy as np

import cubedsphere.const as c

import os

def init_grid(grid_dir=None, ds=None, **kwargs):
    """

    :param grid_dir: direction where the grid can be found (optional)
    :param ds: dataset that contains the grid (optional)
    :return:
    """
    if grid_dir is not None:
        grid_files = os.path.join(grid_dir,"grid.t{:03d}.nc")
        grid_list = [xr.open_dataset(grid_files.format(i)) for i in range(1, 7)]
        grid_nc = xr.concat(grid_list, dim=range(6))
    elif ds is not None:
        grid_nc = ds
    else:
        raise TypeError("you need to specify ds or grid_dir")

    face_connections = {c.FACEDIM:
                            {0: {c.i: ((4, c.j, False), (1, c.i, False)),
                                 c.j: ((5, c.j, False), (2, c.i, False))},
                             1: {c.i: ((0, c.i, False), (3, c.j, False)),
                                 c.j: ((5, c.i, False), (2, c.j, False))},
                             2: {c.i: ((0, c.j, False), (3, c.i, False)),
                                 c.j: ((1, c.j, False), (4, c.i, False))},
                             3: {c.i: ((2, c.i, False), (5, c.j, False)),
                                 c.j: ((1, c.i, False), (4, c.j, False))},
                             4: {c.i: ((2, c.j, False), (5, c.i, False)),
                                 c.j: ((3, c.j, False), (0, c.i, False))},
                             5: {c.i: ((4, c.i, False), (1, c.j, False)),
                                 c.j: ((3, c.i, False), (0, c.j, False))}}}

    if np.all(grid_nc[c.i].shape == grid_nc[c.i_g].shape) and grid_nc[c.i_g].attrs.get("c_grid_axis_shift")==-0.5:
        # We might have left values here
        coords = {c.i: {'center': c.i, 'left': c.i_g}, c.j: {'center': c.j, 'left': c.j_g}, c.time: {'center': c.time},
                  c.k: {'center': c.k, 'left': c.k_l}}
    elif np.all(grid_nc[c.i].shape == grid_nc[c.i_g].shape) and grid_nc[c.i_g].attrs.get("c_grid_axis_shift")==+0.5:
        # We might have left values here
        coords = {c.i: {'center': c.i, 'right': c.i_g}, c.j: {'center': c.j, 'right': c.j_g}, c.time: {'center': c.time},
                  c.k: {'center': c.k, 'left': c.k_l}}
    else:
        coords = {c.i: {'center': c.i, 'outer': c.i_g}, c.j: {'center': c.j, 'outer': c.j_g}, c.time: {'center': c.time},
                  c.k: {'center': c.k, 'left': c.k_l}}

    grid_nc[c.drW] = grid_nc[c.HFacW] * grid_nc[c.drF]  # vertical cell size at u point
    grid_nc[c.drS] = grid_nc[c.HFacS] * grid_nc[c.drF]  # vertical cell size at v point
    grid_nc[c.drC] = grid_nc[c.HFacC] * grid_nc[c.drF]  # vertical cell size at tracer point
    metrics = {
        (c.i,): [c.dxC, c.dxG],  # X distances
        (c.j,): [c.dyC, c.dyG],  # Y distances
        (c.k,): [c.drW, c.drS, c.drC],  # Z distances
        (c.i, c.j): [c.rA, c.rAz, c.rAs, c.rAw]  # Areas
    }

    grid = xgcm.Grid(grid_nc, face_connections=face_connections, coords=coords, periodic=[c.i, c.j], metrics=metrics, **kwargs)
    return grid