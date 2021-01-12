"""
XGCM Grid initialisations for cubedsphere and regridded datasets
"""

import xarray as xr
import xgcm
import numpy as np

import cubedsphere.const as c
import cubedsphere as cs

import os

def init_grid_CS(ds=None, grid_dir=None, **kwargs):
    """
    Init a xgcm grid for a cubedsphere dataset. Useful for raw datasets.

    Parameters
    ----------
    grid_dir: string
        direction where the grid can be found (optional)
    ds: xarray DataSet
        dataset that contains the grid (optional)

    Returns
    ----------
    grid: xgcm.grid
        xgcm grid
    """
    if grid_dir is not None:
        grid_files = os.path.join(grid_dir,"grid.t{:03d}.nc")
        grid_list = [xr.open_dataset(grid_files.format(i)) for i in range(1, 7)]
        grid_nc = xr.concat(grid_list, dim=range(6))
        grid_nc = cs.utils._swap_vertical_coords(grid_nc)
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
                  c.Z: {'center': c.Z, 'right': c.Z_u, 'left': c.Z_l, 'outer': c.Z_p1}}
    elif np.all(grid_nc[c.i].shape == grid_nc[c.i_g].shape) and grid_nc[c.i_g].attrs.get("c_grid_axis_shift")==+0.5:
        # We might have left values here
        coords = {c.i: {'center': c.i, 'right': c.i_g}, c.j: {'center': c.j, 'right': c.j_g}, c.time: {'center': c.time},
                  c.Z: {'center': c.Z, 'right': c.Z_u, 'left': c.Z_l, 'outer': c.Z_p1}}
    else:
        coords = {c.i: {'center': c.i, 'outer': c.i_g}, c.j: {'center': c.j, 'outer': c.j_g}, c.time: {'center': c.time},
                  c.Z: {'center': c.Z, 'right': c.Z_u, 'left': c.Z_l, 'outer': c.Z_p1}}

    grid_nc[c.drW] = grid_nc[c.HFacW] * grid_nc[c.drF]  # vertical cell size at u point
    grid_nc[c.drS] = grid_nc[c.HFacS] * grid_nc[c.drF]  # vertical cell size at v point
    grid_nc[c.drC] = grid_nc[c.HFacC] * grid_nc[c.drF]  # vertical cell size at tracer point
    metrics = {
        (c.i,): [c.dxC, c.dxG],  # X distances
        (c.j,): [c.dyC, c.dyG],  # Y distances
        (c.Z,): [c.drW, c.drS, c.drC],  # Z distances
        (c.i, c.j): [c.rA, c.rAz, c.rAs, c.rAw]  # Areas
    }

    boundary = {c.i:None, c.j:None, c.time:'extrapolate', c.Z:'extrapolate'}

    grid = xgcm.Grid(grid_nc, face_connections=face_connections, coords=coords, periodic=[c.i, c.j], metrics=metrics, boundary=boundary, **kwargs)
    return grid

def init_grid_LL(ds=None, grid_dir=None, **kwargs):
    """
    Init a xgcm grid for a latlon dataset. Useful for regridded datasets

    Parameters
    ----------
    grid_dir: string
        direction where the grid can be found (optional)
    ds: xarray DataSet
        dataset that contains the grid (optional)

    Returns
    ----------
    grid: xgcm.grid
        xgcm grid
    """
    if grid_dir is not None:
        grid_files = os.path.join(grid_dir, "grid.t{:03d}.nc")
        grid_list = [xr.open_dataset(grid_files.format(i)) for i in range(1, 7)]
        grid_nc = xr.concat(grid_list, dim=range(6))
    elif ds is not None:
        grid_nc = ds
    else:
        raise TypeError("you need to specify ds or grid_dir")

    coords = {c.lon: {'center': c.lon}, c.lat: {'center': c.lat}, c.time: {'center': c.time},
              c.Z: {'center': c.Z, 'right': c.Z_u, 'left': c.Z_l, 'outer': c.Z_p1}}

    boundary = {c.i: None, c.j: None, c.time: 'extrapolate', c.Z: 'extrapolate'}

    grid = xgcm.Grid(grid_nc, periodic=[c.i, c.j], coords=coords, boundary=boundary, **kwargs)
    return grid
