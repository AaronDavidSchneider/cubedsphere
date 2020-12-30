ds_list = [xr.open_dataset("../run/state.0000276480.t{:03d}.nc".format(i)) for i in range(1,7)]
ds = xr.concat(ds_list, dim=range(6))

grid = init_grid()
T_average = grid.average(ds["Temp"],axis="Z")
zonal_mean = grid.average(ds["U"],axis="X")
zonal_mean = xr.concat([zonal_mean.isel(T=0,Z=0,concat_dim=i) for i in range(6)],dim="Y")
Y = [ds["YC"].isel(concat_dim = zonal_mean.concat_dim[i]) for i in range(len(zonal_mean.data))]
plt.plot(Y,zonal_mean)
plt.show()


plotCS_wrapper(ds["Temp"].isel(T=0,Z=0), ds, mask_size=5)
plt.show()
plotCS_wrapper(T_average.isel(T=0), ds, mask_size=5)
plt.show()

# Compute GEOS-Chem grid, with half-polar cell
# http://wiki.seas.harvard.edu/geos-chem/index.php/GEOS-Chem_horizontal_grids#GMAO_4_x_5_grid
lon_b = np.linspace(-182.5, 177.5, 73, endpoint=True)
lat_b = np.linspace(-92, 92, 47, endpoint=True).clip(-90, 90)
lat = (lat_b[1:]+lat_b[:-1])/2
lon = (lon_b[1:]+lon_b[:-1])/2
grid_LL = {'lat': lat, 'lon': lon, 'lat_b': lat_b, 'lon_b': lon_b}

grid_CS_list = [None]*6
for i in range(6):
    grid_CS_list[i] = {'lat': ds['YC'][i], 'lon': ds['XC'][i],
                       'lat_b': ds['YG'][i], 'lon_b': ds['XG'][i]}

data_LL = C2L(grid_CS_list, grid_LL, ds["Temp"].isel(T=0,Z=0))
plt.pcolormesh(grid_LL["lon_b"], grid_LL["lat_b"], data_LL)
plt.show()
print(data_LL)