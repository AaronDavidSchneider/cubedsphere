# cubedsphere
Library for post processing of MITgcm cubed sphere data

## Note:
Work in progress! This library is a collection of tools that I found useful to use for the interpretation of cubed sphere data.

## ToDo:
**Postprocessing**:
- [ ] convert vertical dimensions to physical dimensions
- [ ] interface `xmitgcm` to enable the use of `.meta` and `.data` files

**Testing**:
- [ ] compare results with matlab scripts

**Interface**:
- [ ] which values should be hardcoded?
- [ ] special tools needed for exorad?

## Installation:
**Clone this repo**:<br>
```shell
git clone https://github.com/AaronDavidSchneider/cubedsphere.git
cd cubedsphere
```
**Create conda environment:**<br>
```shell
conda create -n mitgcm
```

**Activate environment:**<br>
```shell
conda activate mitgcm
```

**Install dependencies**:<br>
```shell
conda install -c conda-forge xesmf esmpy xgcm matplotlib
```

**Install `cubedsphere`**:<br>
```shell
pip install -e .
```

You can now import the `cubedsphere` package from everywhere on your system 
## Example Usage
See `examples/example.py`. The following plots have been created using data from `tutorial_held_suarez_cs`.
```python
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
```
Only takes 3 seconds!
```python
# do some basic plotting to demonstrate the dataset
# determine which timestep and Z to use:
isel_dict = {"T":1,"Zmd000020":0}

# do some basic plotting to demonstrate the dataset
ds_reg["THETA"].isel(**isel_dict).plot()
U, V = ds_reg["UVEL"].isel(**isel_dict).values, ds_reg["VVEL"].isel(**isel_dict).values
cs.overplot_wind(ds_reg, U, V)
plt.show()
```
![](docs/theta_reg.png)
```python
# Now also plotting theta without regridding (on the original grid):
cs.plotCS(ds["THETA"].isel(**isel_dict), ds, mask_size=5)
plt.show()
```
![](docs/theta_direct.png)

## Credits
Many of the methods come from: https://github.com/JiaweiZhuang/cubedsphere

I would especially like to thank @rabernat for providing `xgcm` and @JiaweiZhuang for providing `xESMF`.