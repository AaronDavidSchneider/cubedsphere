import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import f90nml

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
    _rename_dict = {'XC': 'lon',
                         'XG': 'lon_b',
                         'YC': 'lat',
                         'YG': 'lat_b'}
    ds = ds.rename(_rename_dict)

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

