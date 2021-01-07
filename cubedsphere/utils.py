import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import f90nml
import xmitgcm
import cubedsphere.const as c

def flatten_ds(ds):
    if c.i in ds.dims:
        return xr.concat([ds.isel(**{c.FACEDIM: i}) for i in range(6)], dim=c.i)
    else:
        return xr.concat([ds.isel(**{c.FACEDIM: i}) for i in range(6)], dim=c.i_g)

def read_parameters(outdir):
    """
    Use f90nml to infer exorad modelparameter from data file.
    Useful for postprocessing

    WIP

    :param outdir:
    :return deltaT: timestep
    """
    with open(f'{outdir}/data') as nml_file:
        parser = f90nml.Parser()
        parser.comment_tokens += '#'
        data = parser.read(nml_file)

    deltaT = data["parm03"]["deltaT"]

    return deltaT

def open_mnc_dataset(outdir, iternumber, fname_list = ["state", "secmomDiag", "dynDiag", "surfDiag"]):
    """
    Wrapper that opens simulation outputs from mnc outputs.

    :param outdir: Output directory
    :param iternumber: iteration number of output file
    :param fname_list: List of NetCDF file prefixes to read (no need to specify grid files here)

    :return:
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

    return ds

def open_ascii_dataset(outdir, iternumber, **kwargs):
    """
    Wrapper that opens simulation outputs from standard mitgcm outputs.

     :param outdir: Output directory
    :param iternumber: See xmitgcm iters, can be a iterationnumber or 'all'
    :param kwargs: everything else that is passed to xmitgcm

    :return:
    """
    ds = xmitgcm.open_mdsdataset(data_dir=outdir, iters=iternumber, grid_vars_to_coords=True, geometry="cs", **kwargs).load()

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
                    'k': c.k,
                    'k_u': c.k_u,
                    'k_l': c.k_l,
                    'k_p1': c.k_p1,
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

def overplot_wind(ds_reg, U, V, stepsize=1):
    """
    Quick and dirty function for overplotting wind of a regridded dataset

    :param ds_reg: regridded dataset
    :param stepsize: specify the stepsize for which wind arrows should be plotted

    :return:
    """
    ax = plt.gca()
    y, x = ds_reg["lat"].values, ds_reg["lon"].values
    xmesh, ymesh = np.meshgrid(x, y)
    ax.quiver(xmesh[::stepsize, ::stepsize], ymesh[::stepsize, ::stepsize], U[::stepsize, ::stepsize],
              V[::stepsize, ::stepsize])

