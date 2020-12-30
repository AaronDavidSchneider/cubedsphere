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

# TODO: use example grids from xesmf and hardcode grid_CS_list?
# TODO: C2L should regrid complete dataset?
# Compute GEOS-Chem grid, with half-polar cell
# http://wiki.seas.harvard.edu/geos-chem/index.php/GEOS-Chem_horizontal_grids#GMAO_4_x_5_grid
#lon_b = np.linspace(-182.5, 177.5, 73, endpoint=True)
#lat_b = np.linspace(-92, 92, 47, endpoint=True).clip(-90, 90)
#lat = (lat_b[1:]+lat_b[:-1])/2
#lon = (lon_b[1:]+lon_b[:-1])/2
#grid_LL = {'lat': lat, 'lon': lon, 'lat_b': lat_b, 'lon_b': lon_b}

grid_LL = xe.util.grid_global(5,4)

grid_CS_list = [None]*6
for i in range(6):
    grid_CS_list[i] = {'lat': ds['YC'][i], 'lon': ds['XC'][i],
                       'lat_b': ds['YG'][i], 'lon_b': ds['XG'][i]}

data_LL = cs.C2L(grid_CS_list, grid_LL, ds["Temp"].isel(T=0,Z=0))
plt.pcolormesh(grid_LL["lon_b"], grid_LL["lat_b"], data_LL)
plt.show()
print(data_LL)