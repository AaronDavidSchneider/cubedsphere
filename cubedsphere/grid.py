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
                            {0: {'X': ((4, c.Y, False), (1, c.X, False)),
                                 'Y': ((5, c.Y, False), (2, c.X, False))},
                             1: {'X': ((0, c.X, False), (3, c.Y, False)),
                                 'Y': ((5, c.X, False), (2, c.Y, False))},
                             2: {'X': ((0, c.Y, False), (3, c.X, False)),
                                 'Y': ((1, c.Y, False), (4, c.X, False))},
                             3: {'X': ((2, c.X, False), (5, c.Y, False)),
                                 'Y': ((1, c.X, False), (4, c.Y, False))},
                             4: {'X': ((2, c.Y, False), (5, c.X, False)),
                                 'Y': ((3, c.Y, False), (0, c.X, False))},
                             5: {'X': ((4, c.X, False), (1, c.Y, False)),
                                 'Y': ((3, c.X, False), (0, c.Y, False))}}}

    if np.all(grid_nc[c.X].shape == grid_nc[c.Xp1].shape) and grid_nc[c.Xp1].attrs.get("c_grid_axis_shift")==-0.5:
        # We might have left values here
        coords = {'X': {'center': c.X, 'left': c.Xp1}, 'Y': {'center': c.Y, 'left': c.Yp1}, 'T': {'center': c.T},
                  'Z': {'center': c.Z, 'left': c.Zl}}
    elif np.all(grid_nc[c.X].shape == grid_nc[c.Xp1].shape) and grid_nc[c.Xp1].attrs.get("c_grid_axis_shift")==+0.5:
        # We might have left values here
        coords = {'X': {'center': c.X, 'right': c.Xp1}, 'Y': {'center': c.Y, 'right': c.Yp1}, 'T': {'center': c.T},
                  'Z': {'center': c.Z, 'left': c.Zl}}
    else:
        coords = {'X': {'center': c.X, 'outer': c.Xp1}, 'Y': {'center': c.Y, 'outer': c.Yp1}, 'T': {'center': c.T},
                  'Z': {'center': c.Z, 'left': c.Zl}}

    grid_nc[c.drW] = grid_nc[c.HFacW] * grid_nc[c.drF]  # vertical cell size at u point
    grid_nc[c.drS] = grid_nc[c.HFacS] * grid_nc[c.drF]  # vertical cell size at v point
    grid_nc[c.drC] = grid_nc[c.HFacC] * grid_nc[c.drF]  # vertical cell size at tracer point
    metrics = {
        ('X',): [c.dxC, c.dxG],  # X distances
        ('Y',): [c.dyC, c.dyG],  # Y distances
        ('Z',): [c.drW, c.drS, c.drC],  # Z distances
        ('X', 'Y'): [c.rA, c.rAz, c.rAs, c.rAw]  # Areas
    }

    grid = xgcm.Grid(grid_nc, face_connections=face_connections, coords=coords, periodic=['X', 'Y'], metrics=metrics, **kwargs)
    return grid