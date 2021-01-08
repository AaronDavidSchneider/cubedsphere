# cubedsphere
Library for post processing of MITgcm cubed sphere data

## Capabilities:
- regrid cubed sphere datasets using [`xESMF`](https://xesmf.readthedocs.io/en/latest/) and [`xgcm`](https://xgcm.readthedocs.io/en/latest/)
- open datasets created by the [`mnc`](https://mitgcm.readthedocs.io/en/latest/outp_pkgs/outp_pkgs.html#netcdf-i-o-pkg-mnc) package
- open datasets using [`xmitgcm`](https://xmitgcm.readthedocs.io/en/latest/) (needs current PR [#98](https://github.com/MITgcm/xmitgcm/pull/98)) 
- plot original cubed sphere data
- some more small utilities
- more to come...

## Note:
Work in progress! This library is a collection of tools that I found useful to use for the interpretation of cubed sphere data.

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
import cubedsphere.const as c

# Specify directory where the output files can be found
outdir = "/Volumes/SCRATCH/sim_output/xmitgcm_test/nc_test"

# open Dataset
ds = cs.open_mnc_dataset(outdir, 276480)

# regrid dataset
regridder = cs.Regridder(ds, 5, 4, reuse_weights=False, filename="weights", concat_mode=False)
# Note: once weights were created, we can also reuse files by using reuse_weights=True (saves time).
ds_reg = regridder.regrid()
```
Only takes few seconds!
```python
# do some basic plotting to demonstrate the dataset
# determine which timestep and Z to use:
isel_dict = {c.time:0, c.Z:0}

# do some basic plotting to demonstrate the dataset
fig = plt.figure(figsize=(8,6), constrained_layout=True)
ds_reg[c.T].isel(**isel_dict).plot(vmin=260,vmax=312, add_colorbar=False)
U, V = ds_reg["U"].isel(**isel_dict).values, ds_reg["V"].isel(**isel_dict).values
cs.overplot_wind(ds_reg, U, V)
plt.gca().set_aspect('equal')
plt.savefig("../docs/temp_reg.png")
plt.show()

```
![](docs/temp_reg.png)
```python
# Now also plotting theta without regridding (on the original grid):
fig = plt.figure(figsize=(8,6), constrained_layout=True)
cs.plotCS(ds[c.T].isel(**isel_dict), ds, mask_size=5, vmin=260, vmax=312)
plt.gca().set_aspect('equal')
plt.savefig("../docs/temp_direct.png")
plt.show()
```
![](docs/temp_direct.png)

### Tests with xmitgcm:
See `examples/example_xmitgcm.py`

Since we do not have the grid information, we need to fallback to the `nearest_s2d` interpolation with concat mode. Concat mode means that instead of regridding each face individually and summing up the results, we first concatenate the ds along the X dimension and regrid on the flattened dataset afterwards.

![](docs/temp_ascii_reg.png)

We can fix this and keep using `conservative regridding` by using the grid files from the mnc dataset:

![](docs/temp_ascii_input_grid_reg.png)

In the future we will use `xmitgcm.utils.get_grid_from_input` function instead.

## ToDo:
**Postprocessing**:
- [x] interface `xmitgcm` to enable the use of `.meta` and `.data` files *-> added wrapper*
- [x] how do we expand lon_b and lat_b from left to outer for xmitgcm wrapper? *-> either nc file or soon with `xmitgcm.utils.get_grid_from_input`*

**Testing**:
- [ ] compare results with matlab scripts

**Interface**:
- [x] which values should be hardcoded? *-> done in const.py*
- [x] special tools needed for exorad?

## future Ideas:
**Regridding tools**:
- [ ] use [ESMPy](https://gist.github.com/JiaweiZhuang/990e8019c4103aec8353434a88f24b8a) as an alternative to xESMF (requires 6 processors)

## Credits
Many of the methods come from: https://github.com/JiaweiZhuang/cubedsphere

I would especially like to thank [@rabernat](https://github.com/rabernat) for providing  [`xgcm`](https://xgcm.readthedocs.io/en/latest/) and [@JiaweiZhuang](https://github.com/JiaweiZhuang) for providing [`xESMF`](https://xesmf.readthedocs.io/en/latest/).
