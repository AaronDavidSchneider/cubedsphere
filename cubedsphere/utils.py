"""
Helper functions used throughout this package and utilities to open datasets using xmitgcm and mnc
"""

import xarray as xr
import xmitgcm
import cubedsphere.const as c
import sys

def _flatten_ds(ds):
    """
    Function that concatenates the face dimension along X

    Parameters
    ----------
    ds: xarray Dataset
        Dataset which should be concatenated

    Returns
    -------
    ds: xarray Dataset
        concatenated Dataset
    """
    if c.i in ds.dims:
        return xr.concat([ds.isel(**{c.FACEDIM: i}) for i in range(6)], dim=c.i)
    else:
        return xr.concat([ds.isel(**{c.FACEDIM: i}) for i in range(6)], dim=c.i_g)

def _add_swap_dim_attr(ds):
    for dim in c.vertical_dict.keys():
        ds[dim].attrs["swap_dim"] = c.vertical_dict[dim]

    return ds

def open_mnc_dataset(outdir, iternumber, fname_list = ["state", "secmomDiag", "dynDiag", "surfDiag"]):
    """
    Wrapper that opens simulation outputs from mnc outputs.

    Parameters
    ----------
    outdir: string
        Output directory
    iternumber: integer
        iteration number of output file
    fname_list: list
        List of NetCDF file prefixes to read (no need to specify grid files here)

    Returns
    ----------
    ds: xarray Dataset
        Dataset of simulation output
    """
    # read_parameters(outdir)

    dataset_list = []
    for fname in fname_list:
        dataset = [xr.open_dataset("{}/{}.{:010d}.t{:03d}.nc".format(outdir, fname, iternumber, i)) for i in range(1, 7)]
        dataset_list.append(xr.concat(dataset, dim=range(6)))

    dataset_list = [ds_i.reset_coords(["XC", "YC"]) if "XC" in ds_i.coords else ds_i for ds_i in dataset_list]
    dataset_list = [ds_i.reset_coords(["iter"]) if "iter" in ds_i.coords else ds_i for ds_i in dataset_list]

    grid = [xr.open_dataset("{}/{}.t{:03d}.nc".format(outdir, "grid", i)) for i in range(1, 7)]
    dataset_list.append(xr.concat(grid, dim=range(6)))

    ds = xr.merge(dataset_list, compat="override")

    _rename_dict = {'XC': c.lon,
                    'XG': c.lon_b,
                    'YC': c.lat,
                    'YG': c.lat_b,
                    'X': c.i,
                    'Xp1': c.i_g,
                    'Y': c.j,
                    'Yp1': c.j_g,
                    'AngleCS': c.AngleCS,
                    'AngleSN': c.AngleSN,
                    'concat_dim': c.FACEDIM,
                    'HFacC': c.HFacC,
                    'HFacW': c.HFacW,
                    'HFacS': c.HFacS,
                    'RC': c.Z,
                    'RF': c.Z_p1,
                    'RU': c.Z_u,
                    'RL': c.Z_l,
                    'Z': c.k,
                    'Zu': c.k_u,
                    'Zl': c.k_l,
                    'Zp1': c.k_p1,
                    'T': c.time,
                    'drF': c.drF,
                    'drC': c.drC,
                    'dxC': c.dxC,
                    'dxG': c.dxG,
                    'dyC': c.dyC,
                    'dyG': c.dyG,
                    'dxF': c.dxF,
                    'dyU': c.dyU,
                    'dxV': c.dxV,
                    'dyF': c.dyF,
                    'rA': c.rA,
                    'rAz': c.rAz,
                    'rAs': c.rAs,
                    'rAw': c.rAw,
                    'Temp': c.T
                    }
    ds = ds.rename(_rename_dict)

    ds = _swap_vertical_coords(ds)

    return ds

def open_ascii_dataset(outdir, iternumber, **kwargs):
    """
    Wrapper that opens simulation outputs from standard mitgcm outputs.

    Parameters
    ----------
    outdir: string
        Output directory
    iternumber: List or integer or None
        See xmitgcm iters, can be a iterationnumber or 'all'
    **kwargs
        everything else that is passed to xmitgcm

    Returns
    ----------
    ds: xarray Dataset
        Dataset of simulation output
    """
    ds = xmitgcm.open_mdsdataset(data_dir=outdir, iters=iternumber, grid_vars_to_coords=True, geometry="cs", **kwargs).load()
    ds = _swap_vertical_coords(ds)

    # You might need to extend this if you plan to change values in const.py!
    _rename_dict = {'XC': c.lon,
                    'XG': c.lon_b,
                    'YC': c.lat,
                    'YG': c.lat_b,
                    'i': c.i,
                    'i_g': c.i_g,
                    'j': c.j,
                    'j_g': c.j_g,
                    'CS': c.AngleCS,
                    'SN': c.AngleSN,
                    'face': c.FACEDIM,
                    'hFacC': c.HFacC,
                    'hFacW': c.HFacW,
                    'hFacS': c.HFacS,
                    'time': c.time,
                    'Z': c.Z,
                    'Zu': c.Z_u,
                    'Zl': c.Z_l,
                    'Zp1': c.Z_p1,
                    'drF': c.drF,
                    'drC': c.drC,
                    'dxC': c.dxC,
                    'dxG': c.dxG,
                    'dyC': c.dyC,
                    'dyG': c.dyG,
                    'rA': c.rA,
                    'rAz': c.rAz,
                    'rAs': c.rAs,
                    'rAw': c.rAw,
                    'T':c.T
                    }

    ds = ds.rename(_rename_dict)
    ds = ds.transpose(c.FACEDIM,...)

    return ds

def _swap_vertical_coords(ds, drop_old=True):
    """
    function adapted from xmitgcm to switch the logical vertical dimension to the physical pressure coordinates.

    Parameters
    ----------
    ds: xarray Dataset
        ds for which the vertical dimension should be switched
    drop_old: boolean
        drop old index. True by default

    Returns
    ----------
    ds: xarray Dataset
        Dataset with swaped vertical coordinates
    """

    keep_attrs = ['axis', 'c_grid_axis_shift']

    if 'swap_dim' not in ds[c.k].attrs:
        ds = _add_swap_dim_attr(ds)

    # first squeeze all the coordinates
    for orig_dim in ds.dims:
        if 'swap_dim' in ds[orig_dim].attrs and orig_dim in c.vertical_dict.keys():
            new_dim = ds[orig_dim].attrs['swap_dim']
            coord_var = ds[new_dim]
            for coord_dim in coord_var.dims:
                if coord_dim != orig_dim:
                    # dimension should be the same along all other axes, so just
                    # take the first row / column
                    coord_var = coord_var.isel(**{coord_dim: 0}).drop(coord_dim)
            ds[new_dim] = coord_var
            for key in keep_attrs:
                if key in ds[orig_dim].attrs:
                    ds[new_dim].attrs[key] = ds[orig_dim].attrs[key]
    # then swap dims
    for orig_dim in ds.dims:
        if 'swap_dim' in ds[orig_dim].attrs and orig_dim in c.vertical_dict.keys():
            new_dim = ds[orig_dim].attrs['swap_dim']
            ds = ds.swap_dims({orig_dim:  new_dim})
            if drop_old:
                if sys.version_info[0] < 3:
                    ds = ds.drop(orig_dim)
                else:
                    ds = ds.drop_vars(orig_dim)
    return ds