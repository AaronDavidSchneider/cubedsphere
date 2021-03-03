"""
Module for regridding cubedsphere datasets
Inspired from https://github.com/JiaweiZhuang/cubedsphere/blob/master/example_notebooks/C2L_regrid.ipynb
"""
import xesmf as xe
import xarray as xr
import numpy as np
import warnings
import time
import cubedsphere.const as c
from .grid import init_grid_CS
from .utils import _flatten_ds

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


class Regridder:
    """
    Class that wraps the xESMF regridder for cs geometry.

    Only two methods are possible with the cs geometry: conservative when using concat_mode=False (requires lon_b
    to have different shape from lon and lat_b from lat) or nearest_s2d when using concat_mode=True.
    Conservative regridding should be used if possible!

    Attributes
    ----------
    regridder: list or xESMF regrid object
        (contains) the initialized xESMF regridder
    grid: dict
        output grid

    Examples
    --------
    >>> import cubedsphere as cs  # import cubedsphere
    >>> outdir = "../run"  # specify output directory
    >>> ds = cs.open_mnc_dataset(outdir, 276480)  # open dataset
    >>> regrid = cs.Regridder(ds)  # init regridder
    >>> ds_regrid = regrid()  # perform regridding of dataset

    Notes
    -----
    You can find more examples in the examples directory
    """
    def __init__(self, ds, d_lon=5, d_lat=4, input_grid=None, concat_mode=False, filename="weights", method='conservative', **kwargs):
        """
        Build the regridder. This step will create the output grid and weight files which will then be used to regrid the dataset.

        Parameters
        ----------
        ds: xarray DataSet
            Dataset to be regridded. Dataset must contain grid information.
        d_lon: integer
            Longitude step size, i.e. grid resolution.
        d_lat: integer
            Latitude step size, i.e. grid resolution.
        input_grid: xarray DataSet
            use input grid different to ds. Caution with this practice!
        concat_mode: boolean
            use one regridding instance instead of one regridder for each face
        filename: string
            filename for weights (weights will be name filename(+ _tile{i}).nc)
        method: string
            Regridding method. See xe.Regridder for options.
        kwargs :
            Optional parameters that are passed to xe.Regridder (see xe.Regridder for options).
        """
        t = time.time()
        self._ds = ds
        if input_grid is None:
            self._ds_grid_in = self._ds
        else:
            self._ds_grid_in = input_grid
            if input_grid != self._ds:
                print(
                    "Caution: You chose to use an input grid that is different from the dataset to be regridded,\n"
                    "Only do so, if you are really sure that the input_grid matches!\n")

        self.grid = self._build_output_grid(d_lon, d_lat)
        self._method = method
        self._concat_mode = concat_mode

        if self._concat_mode:
            self._build_regridder_concat(filename, **kwargs)
        else:
            self._build_regridder_faces(filename, **kwargs)

        print(f"time needed to build regridder: {time.time() - t}")
        print(f"Regridder will use {self._method} method")
        if self._method not in ["patch","conservative"]:
            print("Caution: The regridding method that you chose might not conserve fluxes")
        if self._method not in ["conservative", "nearest_s2d"]:
            print("Caution: The regridding method that you chose might return 0's on borders, double check by plotting the dataset")

    def _build_regridder_faces(self, filename, **kwargs):
        if np.all(self._ds_grid_in[c.lat].shape == self._ds_grid_in[c.lat_b].shape):
            self._method = "nearest_s2d"
            self._concat_mode = True
            self._build_regridder_concat(filename, **kwargs)
            print("falling back to concat mode. The ds you provide has no outer coordinates.")
            return

        self._grid_in = [None] * 6
        for i in range(6):
            self._grid_in[i] = {'lat': self._ds_grid_in[c.lat].isel(**{c.FACEDIM: i}),
                                'lon': self._ds_grid_in[c.lon].isel(**{c.FACEDIM: i}),
                                'lat_b': self._ds_grid_in[c.lat_b].isel(**{c.FACEDIM: i}),
                                'lon_b': self._ds_grid_in[c.lon_b].isel(**{c.FACEDIM: i})}

        if self._method in ["nearest_s2d", "nearest_d2s"]:
            self._method = "conservative"
            print("falling back to conservative. Nearest neighbour methods aint working for `concat_mode=False`")

        self.regridder = [
            xe.Regridder(self._grid_in[i], self.grid, filename=f"{filename}_tile{i + 1}.nc", method=self._method,
                         **kwargs)
            for i in range(6)]

    def _build_regridder_concat(self, filename, **kwargs):
        if self._method != "nearest_s2d":
            if np.all(self._ds_grid_in[c.lon].shape!=self._ds_grid_in[c.lon_b].shape):
                self._method = "conservative"
                self._concat_mode = False
                print(
                    f"falling back to {self._method} and `concat_mode={self._concat_mode}: The interpolation method you chose doesn't work with your grid geometry")

                self._build_regridder_faces(filename,**kwargs)
                return
            else:
                self._method = "nearest_s2d"
                print(f"falling back to {self._method}: The interpolation method you chose doesn't work with your grid geometry")

        self._grid_in = {'lat': _flatten_ds(self._ds_grid_in[c.lat]),
                         'lon': _flatten_ds(self._ds_grid_in[c.lon])}

        self.regridder = xe.Regridder(self._grid_in, self.grid, filename=f"{filename}.nc", method=self._method, periodic=False,
                                      **kwargs)

    def _build_output_grid(self, d_lon, d_lat):
        grid = xe.util.grid_global(d_lon, d_lat)
        grid_LL = {'lat': grid["lat"][:, 0].values, 'lon': grid["lon"][0, :].values,
                   'lat_b': grid["lat_b"][:, 0].values, 'lon_b': grid["lon_b"][0, :].values}
        return grid_LL

    def __call__(self, vector_names = None, **kwargs):
        """
        Wrapper that carries out the regridding from cubedsphere to latlon.

        Parameters
        ----------
        vector_names: list
            names of vectors in ds, each list entry should follow '{}NAME' format for 'UNAME' and 'VNAME'.
            if not provided, will fallback to '["{}VEL", "{}", "{}VELSQ", "{}THMASS"]'

        Returns
        -------
        ds: xarray DataSet
            regridded Dataset
        """

        # initialize an empty dataset
        ds = xr.Dataset()

        # specify vector quantities and exclude from scalar regridding (special treatment nescessary)
        if vector_names is None:
            vector_names = ["{}VEL", "{}", "{}VELSQ", "{}THMASS"]

        _all_vectors = [vector.format(direction) for direction in ["U","V"] for vector in vector_names]

        # We do not want to regrid grid values
        to_not_regrid_scalar = [c.lon_b, c.lon, c.lat_b, c.lat, c.drF, c.drC, c.drS, c.dxG, c.dxC, c.drW, c.dyC, c.dyG,
                                c.dxF, c.dyU, c.dxV, c.dyF,
                                c.HFacC, c.HFacW, c.HFacS, c.rAz, c.rA, c.rAw, c.rAs, c.AngleSN,
                                c.AngleCS]

        # We need to rotate scalar values first
        to_not_regrid_scalar = to_not_regrid_scalar + _all_vectors

        # init grid to interp edge quantities to center
        grid = init_grid_CS(ds=self._ds)

        # We first need interpolate quantites to the cell center (if nescessary)
        reg_all = np.all(self._ds[c.i].shape != self._ds[c.i_g].shape)
        for data in set(self._ds.data_vars) - set(to_not_regrid_scalar):
            dims = self._ds[data].dims
            if c.i_g in dims and c.j_g not in dims and reg_all:
                interp = grid.interp(self._ds[data], to="center", axis=c.i)
            elif c.j_g in dims and c.i_g not in dims and reg_all:
                interp = grid.interp(self._ds[data], to="center", axis=c.j)
            elif c.i_g in dims and c.j_g in dims and reg_all:
                interp = grid.interp(self._ds[data], to="center", axis=[c.i, c.j])
            elif c.i_g not in dims and c.j_g not in dims:
                interp = self._ds[data]
            else:
                interp = None

            # Do regridding for scalar data
            if interp is not None:
                ds[data] = self._regrid_wrapper(interp, **kwargs)


        # Regridding for vectors
        for vector in vector_names:
            try:
                # interpolate vectors to cell centers:
                interp_UV = grid.interp_2d_vector(vector={c.i: self._ds[vector.format("U")], c.j: self._ds[vector.format("V")]}, to="center")
                # rotate vectors geographic direction:
                vector_E, vector_N = self._rotate_vector_to_EN(interp_UV[c.i], interp_UV[c.j], self._ds[c.AngleCS], self._ds[c.AngleSN])
                # perform the regridding:
                ds[vector.format("U")] = self._regrid_wrapper(vector_E, **kwargs)
                ds[vector.format("V")] = self._regrid_wrapper(vector_N, **kwargs)
            except KeyError:
                pass

        # remove the face dimension from the dataset
        if c.FACEDIM in ds.dims:
            ds = ds.reset_coords(c.FACEDIM)

        # xESMF names longitude lon and latitude lat. We want to rename it to whatever we set in const.py to be consistent
        ds = ds.rename({"lon": c.lon, "lat": c.lat})

        # clean up weight files (see xESMF doc). Somehow not working in my xESMF version...
        # for regridder_i in self.regridder:
        #     regridder_i.clean_weight_file()

        return ds

    def _regrid_wrapper(self, ds_in, **kwargs):
        """
        wrapper to regrid general scalar dataarray.
        Caution: Horizontal dimensions must be the last two dimensions!

        Parameters
        ----------
        ds_in: xarray DataSet
            data to be regridded
        **kwargs
            additional parameters to be passed to regridding call

        Returns
        ----------
        numpy array:
            regridded data
        """
        if len(ds_in.shape) == 5:
            data_out = np.zeros([ds_in.shape[1], ds_in.shape[2], self.grid['lat'].size, self.grid['lon'].size])
        elif len(ds_in.shape) == 4:
            data_out = np.zeros([ds_in.shape[1], self.grid['lat'].size, self.grid['lon'].size])
        elif len(ds_in.shape) == 3:
            data_out = np.zeros([self.grid['lat'].size, self.grid['lon'].size])
        else:
            if c.FACEDIM in ds_in.dims:
                assert np.all(ds_in.isel(**{c.FACEDIM:0}) == ds_in.isel(**{c.FACEDIM:1})), "you have a really messed up input dataset!"
                return ds_in[0]
            else:
                return ds_in

        if self._concat_mode:
            data_out = self.regridder(_flatten_ds(ds_in), **kwargs)
        else:
            for i in range(6):
                # add up the results for 6 tiles
                data_out += self.regridder[i](ds_in.isel(**{c.FACEDIM:i}), **kwargs)

        return data_out


    def _rotate_vector_to_EN(self, U, V, AngleCS, AngleSN):
        """
        rotate vector to east north direction.
        Assumes that AngleCS and AngleSN are already of same dimension as V and U (i.e. already interpolated to cell center)

        Parameters
        ----------
        U: xarray Dataarray
            zonal vector component
        V: xarray Dataarray
            meridional vector component
        AngleCS: xarray Dataarray
            Cosine of angle of the grid center relative to the geographic direction
        AngleSN: xarray Dataarray
            Sine of angle of the grid center relative to the geographic direction

        Returns
        ----------
        uE: xarray Dataarray
            rotated zonal velocity
        vN: xarray Dataarray
            rotated meridional velocity

        """
        # rotate the vectors:
        uE = AngleCS * U - AngleSN * V
        vN = AngleSN * U + AngleCS * V

        # reorder coordinates:
        uE = uE.transpose(..., c.j, c.i)
        vN = vN.transpose(..., c.j, c.i)

        return uE, vN





