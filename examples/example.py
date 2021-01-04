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
ds_reg = regridder.regrid()
print(f"time needed to regrid dataset: {time.time()-t}")

# do some basic plotting to demonstrate the dataset
ds_reg["THETA"].isel(T=0,Zmd000020=0).plot()
cs.overplot_wind(ds_reg)
plt.show()

# Now also plotting theta without regridding (on the original grid):
cs.plotCS(ds["THETA"].isel(T=0,Zmd000020=0), ds, mask_size=2)
plt.show()