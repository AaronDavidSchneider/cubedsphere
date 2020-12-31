import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cubedsphere as cs
import xesmf as xe

outdir = "run"

# TODO: Wrapper function!!
ds_list = [xr.open_dataset("{}/state.0000276480.t{:03d}.nc".format(outdir,i)) for i in range(1,7)]
ds = xr.concat(ds_list, dim=range(6))

cs.plotCS(ds["Temp"].isel(T=0,Z=0), ds, mask_size=5)
plt.show()

grid = cs.init_grid(grid_dir=outdir)
T_average = grid.average(ds["Temp"],axis="Z")
cs.plotCS(T_average.isel(T=0), ds, mask_size=5)
plt.show()

regridder = cs.Regridder(ds,5,4)
regridder.regrid()

data_LL = regridder.regrid_single_data(ds["Temp"].isel(Z=0,T=0))
plt.pcolormesh(regridder.grid["lon_b"], regridder.grid["lat_b"], data_LL)
plt.show()
print(data_LL)