import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import f90nml
import xmitgcm
import cubedsphere.const as c

def flatten_ds(ds):
    if c.X in ds.dims:
        return xr.concat([ds.isel(**{c.FACEDIM: i}) for i in range(6)], dim=c.X)
    else:
        return xr.concat([ds.isel(**{c.FACEDIM: i}) for i in range(6)], dim=c.Xp1)

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

def open_mnc_dataset(outdir, iternumber):
    """
    Wrapper that opens simulation outputs from mnc outputs.

    :param outdir:
    :param iternumber:

    :return:
    """
    # read_parameters(outdir)

    dataset_list = []
    for fname in ["state", "secmomDiag", "dynDiag", "surfDiag"]:
        dataset = [xr.open_dataset("{}/{}.{:010d}.t{:03d}.nc".format(outdir, fname, iternumber, i)) for i in range(1, 7)]
        dataset_list.append(xr.concat(dataset, dim=range(6)))

    dataset_list = [ds_i.reset_coords(["XC", "YC"]) if "XC" in ds_i.coords else ds_i for ds_i in dataset_list]
    dataset_list = [ds_i.reset_coords(["iter"]) if "iter" in ds_i.coords else ds_i for ds_i in dataset_list]

    grid = [xr.open_dataset("{}/{}.t{:03d}.nc".format(outdir, "grid", i)) for i in range(1, 7)]
    dataset_list.append(xr.concat(grid, dim=range(6)))

    ds = xr.merge(dataset_list, compat="override")
    _rename_dict = {'XC': c.XC,
                    'XG': c.XG,
                    'YC': c.YC,
                    'YG': c.YG,
                    'X': c.X,
                    'Xp1': c.Xp1,
                    'Y': c.Y,
                    'Yp1': c.Yp1,
                    'AngleCS': c.AngleCS,
                    'AngleSN': c.AngleSN,
                    'concat_dim': c.FACEDIM,
                    'HFacC': c.HFacC,
                    'HFacW': c.HFacW,
                    'HFacS': c.HFacS,
                    }
    ds = ds.rename(_rename_dict)

    return ds

def open_ascii_dataset(outdir, iternumber, **kwargs):
    """
    Wrapper that opens simulation outputs from standard mitgcm outputs.

    :param outdir:
    :param iternumber:
    :param kwargs: everything else that is passed to xmitgcm

    :return:
    """
    ds = xmitgcm.open_mdsdataset(data_dir=outdir, iters=iternumber, grid_vars_to_coords=True, geometry="cs", **kwargs).load()

    # You might need to extend this if you plan to change values in const.py!
    _rename_dict = {'XC': c.XC,
                    'XG': c.XG,
                    'YC': c.YC,
                    'YG': c.YG,
                    'i': c.X,
                    'i_g':c.Xp1,
                    'j':c.Y,
                    'j_g':c.Yp1,
                    'CS':c.AngleCS,
                    'SN':c.AngleSN,
                    'face':c.FACEDIM,
                    'hFacC':c.HFacC,
                    'hFacW':c.HFacW,
                    'hFacS':c.HFacS,
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

