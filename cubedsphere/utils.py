import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

def open_mnc_dataset(outdir, iternumber):
    """
    Wrapper that opens simulation outputs from mnc outputs.

    :param outdir:
    :param iternumber:

    :return:
    """
    dataset_list = []
    for fname in ["secmomDiag", "dynDiag", "surfDiag"]:
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

def overplot_wind(ds_reg, stepsize=1):
    """
    Quick and dirty function for overplotting wind of a regridded dataset

    :param ds_reg: regridded dataset
    :param stepsize: specify the stepsize for which wind arrows should be plotted

    :return:
    """
    ax = plt.gca()
    y, x = ds_reg["lat"].values, ds_reg["lon"].values
    xmesh, ymesh = np.meshgrid(x, y)
    U, V = ds_reg["UVEL"].isel(T=0, Zmd000020=0).values, ds_reg["VVEL"].isel(T=0, Zmd000020=0).values
    ax.quiver(xmesh[::stepsize, ::stepsize], ymesh[::stepsize, ::stepsize], U[::stepsize, ::stepsize],
              V[::stepsize, ::stepsize])

