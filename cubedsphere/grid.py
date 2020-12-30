def init_grid(grid_files="../run/grid.t{:03d}.nc"):
    grid_list = [xr.open_dataset(grid_files.format(i)) for i in range(1, 7)]
    grid_nc = xr.concat(grid_list, dim=range(6))
    face_connections = {'concat_dim':
                            {0: {'X': ((4, 'Y', False), (1, 'X', False)),
                                 'Y': ((5, 'Y', False), (2, 'X', False))},
                             1: {'X': ((0, 'X', False), (3, 'Y', False)),
                                 'Y': ((5, 'X', False), (2, 'Y', False))},
                             2: {'X': ((0, 'Y', False), (3, 'X', False)),
                                 'Y': ((1, 'Y', False), (4, 'X', False))},
                             3: {'X': ((2, 'X', False), (5, 'Y', False)),
                                 'Y': ((1, 'X', False), (4, 'Y', False))},
                             4: {'X': ((2, 'Y', False), (5, 'X', False)),
                                 'Y': ((3, 'Y', False), (0, 'X', False))},
                             5: {'X': ((4, 'X', False), (1, 'Y', False)),
                                 'Y': ((3, 'X', False), (0, 'Y', False))}}}

    coords = {'X': {'center': 'X', 'outer': 'Xp1'}, 'Y': {'center': 'Y', 'outer': 'Yp1'}, 'T': {'center': 'T'},
              'Z': {'center': 'Z', 'left': 'Zl'}}

    grid_nc['drW'] = grid_nc.HFacW * grid_nc.drF  # vertical cell size at u point
    grid_nc['drS'] = grid_nc.HFacS * grid_nc.drF  # vertical cell size at v point
    grid_nc['drC'] = grid_nc.HFacC * grid_nc.drF  # vertical cell size at tracer point
    metrics = {
        ('X',): ['dxC', 'dxG'],  # X distances
        ('Y',): ['dyC', 'dyG'],  # Y distances
        ('Z',): ['drW', 'drS', 'drC'],  # Z distances
        ('X', 'Y'): ['rA', 'rAz', 'rAs', 'rAw']  # Areas
    }

    grid = xgcm.Grid(grid_nc, face_connections=face_connections, coords=coords, periodic=['X', 'Y'], metrics=metrics)
    return grid