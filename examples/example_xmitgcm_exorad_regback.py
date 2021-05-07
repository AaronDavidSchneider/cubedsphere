import matplotlib.pyplot as plt
import cubedsphere as cs
import cubedsphere.const as c

# Specify directory where the output files can be found
outdir_ascii = "/Users/schneider/codes/exo/exorad/exo_veri/exorad_full/run"

# open Dataset
ds_ascii, grid = cs.open_ascii_dataset(outdir_ascii, iternumber=100)

# converts wind
ds_ascii = cs.exorad_postprocessing(ds_ascii, outdir=outdir_ascii)

# regrid dataset
regrid = cs.Regridder(ds_ascii, input_type="cs", d_lon=5, d_lat=4, reuse_weights=False, filename="weights", concat_mode=False, cs_grid=grid)
# Note: once weights were created, we can also reuse files by using reuse_weights=True (saves time).
# Note: to test the concat mode, we can also use concat_mode=True
ds_reg = regrid()

reg_grid = regrid._build_output_grid(5, 4)
ds_reg["lon_b"] = reg_grid["lon_b"]
ds_reg["lat_b"] = reg_grid["lat_b"]

reg_back = cs.Regridder(ds_reg, input_type="ll", reuse_weights=False, filename="weights", concat_mode=False, cs_grid=grid)
ds_reg_back = reg_back()
# do some basic plotting to demonstrate the dataset
# determine which timestep and Z to use:
isel_dict = {c.time:0, c.Z:20}

# do some basic plotting to demonstrate the dataset
fig = plt.figure(figsize=(8,6), constrained_layout=True)
ds_reg[c.T].isel(**isel_dict).plot(add_colorbar=False)
U, V = ds_reg["U"].isel(**isel_dict).values, ds_reg["V"].isel(**isel_dict).values
#cs.overplot_wind(ds_reg, U, V)
plt.gca().set_aspect('equal')
plt.show()

# Now also plotting theta without regridding (on the original grid):
fig = plt.figure(figsize=(8,6), constrained_layout=True)
cs.plotCS(ds_reg_back[c.T].isel(**isel_dict), ds_reg_back, mask_size=10)
plt.gca().set_aspect('equal')
plt.show()