import matplotlib.pyplot as plt
import cubedsphere as cs
import time

# Specify directory where the output files can be found
outdir = "run"

# open Dataset
ds = cs.open_mnc_dataset(outdir, 276480)

# regrid dataset
t = time.time()
regridder = cs.Regridder(ds, 5, 4, reuse_weights=False, filename="weights")
# Note: once weights were created, we can also reuse files by using reuse_weights=True (saves time).
ds_reg = regridder.regrid()
print(f"time needed to regrid dataset: {time.time()-t}")

# do some basic plotting to demonstrate the dataset
# determine which timestep and Z to use:
isel_dict = {"T":1,"Zmd000020":0}

# do some basic plotting to demonstrate the dataset
ds_reg["THETA"].isel(**isel_dict).plot()
U, V = ds_reg["UVEL"].isel(**isel_dict).values, ds_reg["VVEL"].isel(**isel_dict).values
cs.overplot_wind(ds_reg, U, V)
plt.savefig("../docs/theta_reg.png")
plt.show()

# Now also plotting theta without regridding (on the original grid):
cs.plotCS(ds["THETA"].isel(**isel_dict), ds, mask_size=5)
plt.savefig("../docs/theta_direct.png")
plt.show()