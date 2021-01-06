import matplotlib.pyplot as plt
import cubedsphere as cs
import time

# Specify directory where the output files can be found
outdir_ascii = "/Users/schneider/codes/MITgcm/verification/tutorial_held_suarez_cs/run"

# open Dataset
ds_ascii = cs.open_ascii_dataset(outdir_ascii, iternumber=276480)

# regrid dataset
t = time.time()
regridder = cs.Regridder(ds_ascii, 5, 4, reuse_weights=False, filename="weights", concat_mode=False)
# Note: once weights were created, we can also reuse files by using reuse_weights=True (saves time).
# Note: to test the concat mode, we can also use concat_mode=True
ds_reg = regridder.regrid()
print(f"time needed to regrid dataset: {time.time()-t}")

# do some basic plotting to demonstrate the dataset
# determine which timestep and Z to use:
isel_dict = {"time":0,"k":0}
ds_reg["T"].isel(**isel_dict).plot(vmin=260,vmax=312)

# do some basic plotting to demonstrate the dataset
U, V = ds_reg["U"].isel(**isel_dict).values, ds_reg["V"].isel(**isel_dict).values
cs.overplot_wind(ds_reg, U, V)
plt.savefig("../docs/temp_ascii_reg.png")
plt.show()

# Now also plotting theta without regridding (on the original grid):
cs.plotCS(ds_ascii["T"].isel(**isel_dict), ds_ascii, mask_size=5)
plt.savefig("../docs/temp_ascii_direct.png")
plt.show()