import matplotlib.pyplot as plt
import cubedsphere as cs
import cubedsphere.const as c

# Specify directory where the output files can be found
outdir_ascii = "/Volumes/SCRATCH/sim_output/xmitgcm_test/ascii_test"

# open Dataset
ds_ascii = cs.open_ascii_dataset(outdir_ascii, iternumber=276480)

# regrid dataset
regrid = cs.Regridder(ds_ascii, 5, 4, reuse_weights=False, filename="weights", concat_mode=False)
# Note: once weights were created, we can also reuse files by using reuse_weights=True (saves time).
# Note: to test the concat mode, we can also use concat_mode=True
ds_reg = regrid()

# do some basic plotting to demonstrate the dataset
# determine which timestep and Z to use:
isel_dict = {c.time:0, c.Z:0}

# do some basic plotting to demonstrate the dataset
fig = plt.figure(figsize=(8,6), constrained_layout=True)
ds_reg[c.T].isel(**isel_dict).plot(vmin=260,vmax=312, add_colorbar=False)
U, V = ds_reg["U"].isel(**isel_dict).values, ds_reg["V"].isel(**isel_dict).values
cs.overplot_wind(ds_reg, U, V)
plt.gca().set_aspect('equal')
plt.savefig("../doc/images/temp_ascii_reg.png")
plt.show()

# Now also plotting theta without regridding (on the original grid):
fig = plt.figure(figsize=(8,6), constrained_layout=True)
cs.plotCS(ds_ascii[c.T].isel(**isel_dict), ds_ascii, mask_size=5, vmin=260,vmax=312)
plt.gca().set_aspect('equal')
plt.savefig("../doc/images/temp_ascii_direct.png")
plt.show()