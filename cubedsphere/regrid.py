"""
Inspired from https://github.com/JiaweiZhuang/cubedsphere/blob/master/example_notebooks/C2L_regrid.ipynb
"""
import xesmf as xe
import xarray as xr
import numpy as np
import warnings
from .const import FACEDIM
from .grid import init_grid

warnings.simplefilter(action='ignore', category=FutureWarning)


class Regridder:
    def __init__(self, ds, d_lon=5, d_lat=4, filename="weights", method='conservative', **kwargs):
        """
        Build the regridder objects (one for each face).

        :param ds: dataset to be regridded. Dataset must contain grid information.
        :param d_lon: Longitude step size, i.e. grid resolution.
        :param d_lat: Latitude step size, i.e. grid resolution.
        :param filename: filename for weights (weights will be name filename + _tile{i}.nc)
        :param method: Regridding method. See xe.Regridder for options.
        :param kwargs: Optional parameters that are passed to xe.Regridder (see xe.Regridder for options).
        """
        self._rename_dict = {'XC': 'lon',
                              'XG': 'lon_b',
                              'YC': 'lat',
                              'YG': 'lat_b'}
        try:
            self._ds = ds.rename(self._rename_dict)
        except ValueError:
            self._ds = ds

        self._grid_in = [None] * 6
        for i in range(6):
            self._grid_in[i] = {'lat': self._ds['lat'].isel(**{FACEDIM:i}), 'lon': self._ds['lon'].isel(**{FACEDIM:i}),
                               'lat_b': self._ds['lat_b'].isel(**{FACEDIM:i}), 'lon_b': self._ds['lon_b'].isel(**{FACEDIM:i})}

        self.grid = self._build_output_grid(d_lon, d_lat)
        self._method = method

        self.regridder = [
            xe.Regridder(self._grid_in[i], self.grid, filename=f"{filename}_tile{i+1}.nc", method=self._method, **kwargs)
            for i in range(6)]

    def _build_output_grid(self, d_lon, d_lat):
        grid = xe.util.grid_global(d_lon, d_lat)
        grid_LL = {'lat': grid["lat"][:, 0].values, 'lon': grid["lon"][0, :].values,
                   'lat_b': grid["lat_b"][:, 0].values, 'lon_b': grid["lon_b"][0, :].values}
        return grid_LL

    def regrid(self):
        """
        Wrapper that carries out the regridding from cubedsphere to latlon.

        :return: regridded Dataset
        """

        # initialize an empty dataset
        ds = xr.Dataset()

        # specify vector quantities and exclude from scalar regridding (special treatment nescessary)
        vector_names = ["{}VEL", "{}", "{}VELSQ", "{}THMASS"]
        _all_vectors = [vector.format(direction) for direction in ["U","V"] for vector in vector_names]
        to_not_regrid_scalar = ["lon_b", "lat_b", "lon", "lat"] + _all_vectors

        # init grid to interp edge quantities to center
        grid = init_grid(ds=self._ds)

        # We first need interpolate quantites to the cell center (if nescessary)
        for data in set(self._ds.data_vars) - set(to_not_regrid_scalar):
            dims = self._ds[data].dims
            if "Xp1" in dims and "Yp1" not in dims:
                interp = grid.interp(self._ds[data], to="center", axis="X")
            elif "Yp1" in dims and "Xp1" not in dims:
                interp = grid.interp(self._ds[data], to="center", axis="Y")
            elif "Xp1" in dims and "Yp1" in dims:
                interp = grid.interp(self._ds[data], to="center", axis=["X","Y"])
            else:
                interp = self._ds[data]

            # Do regridding for scalar data
            ds[data] = self._regrid_wrapper(interp)

        # Regridding for vectors
        for vector in vector_names:
            try:
                # interpolate vectors to cell centers:
                interp_UV = grid.interp_2d_vector(vector={"X": self._ds[vector.format("U")], "Y": self._ds[vector.format("V")]}, to="center")
                # rotate vectors geographic direction:
                vector_E, vector_N = self._rotate_vector_to_EN(interp_UV["X"], interp_UV["Y"], self._ds["AngleCS"], self._ds["AngleSN"])
                # perform the regridding:
                ds[vector.format("U")] = self._regrid_wrapper(vector_E)
                ds[vector.format("V")] = self._regrid_wrapper(vector_N)
            except KeyError:
                pass

        # remove the face dimension from the dataset
        try:
            ds = ds.reset_coords(FACEDIM)
        except ValueError:
            print(
                "Warning: We could not remove the face dimension! Please check that your input dataset has only face dependencies where they belong.")

        # clean up weight files (see xESMF doc). Somehow not working in my xESMF version...
        # for regridder_i in self.regridder:
        #     regridder_i.clean_weight_file()

        return ds

    def _regrid_wrapper(self, ds_in, **kwargs):
        """
        wrapper to regrid general scalar dataarray.
        Caution: Horizontal dimensions must be the last two dimensions!

        :param ds_in: data to be regridded
        :param kwargs: additional parameters to be passed to regridding call

        :return: regridded data
        """
        if len(ds_in.shape) == 5:
            data_out = np.zeros([ds_in.shape[1], ds_in.shape[2], self.grid['lat'].size, self.grid['lon'].size])
        elif len(ds_in.shape) == 4:
            data_out = np.zeros([ds_in.shape[1], self.grid['lat'].size, self.grid['lon'].size])
        elif len(ds_in.shape) == 3:
            data_out = np.zeros([self.grid['lat'].size, self.grid['lon'].size])
        else:
            if FACEDIM in ds_in.dims:
                assert np.all(ds_in.isel(**{FACEDIM:0}) == ds_in.isel(**{FACEDIM:1})), "you have a really messed up input dataset!"
                return ds_in[0]
            else:
                return ds_in

        for i in range(6):
            # add up the results for 6 tiles
            data_out += self.regridder[i](ds_in.isel(**{FACEDIM:i}), **kwargs)

        return data_out


    def _rotate_vector_to_EN(self, U, V, AngleCS, AngleSN):
        """
        rotate vector to east north direction.
        Assumes that AngleCS and AngleSN are already of same dimension as V and U (i.e. already interpolated to cell center)

        :param U: zonal vector component
        :param V: meridional vector component
        :param AngleCS: Cosine of angle of the grid center relative to the geographic direction
        :param AngleSN: Sine of angle of the grid center relative to the geographic direction

        :return: uE, vN
        """
        # rotate the vectors:
        uE = AngleCS * U - AngleSN * V
        vN = AngleSN * U + AngleCS * V

        # reorder coordinates:
        uE = uE.transpose(..., "Y", "X")
        vN = vN.transpose(..., "Y", "X")

        return uE, vN





