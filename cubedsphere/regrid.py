"""
Inspired from https://github.com/JiaweiZhuang/cubedsphere/blob/master/example_notebooks/C2L_regrid.ipynb
"""
import xesmf as xe
import numpy as np
from .const import FACEDIM

class Regridder:
    def __init__(self, ds, d_lon, d_lat, method='conservative', filename=None, **kwargs):

        self._ds = ds.rename({'XC': 'lon',
                              'XG': 'lon_b',
                              'YC': 'lat',
                              'YG': 'lat_b'})
        self._grid_in = [None] * 6
        for i in range(6):
            self._grid_in[i] = {'lat': self._ds['lat'].isel(**{FACEDIM:i}), 'lon': self._ds['lon'].isel(**{FACEDIM:i}),
                               'lat_b': self._ds['lat_b'].isel(**{FACEDIM:i}), 'lon_b': self._ds['lon_b'].isel(**{FACEDIM:i})}

        self.grid = self.build_output_grid(d_lon, d_lat)

        self.regridder = [xe.Regridder(self._grid_in[i], self.grid, method=method, filename=filename, **kwargs) for i in range(6)]

    def build_output_grid(self, d_lon, d_lat):
        grid = xe.util.grid_global(d_lon, d_lat)
        grid_LL = {'lat': grid["lat"][:, 0].values, 'lon': grid["lon"][0, :].values,
                   'lat_b': grid["lat_b"][:, 0].values, 'lon_b': grid["lon_b"][0, :].values}
        return grid_LL

    def regrid(self):
        ds = self._ds.copy()
        for data in self._ds:
            if data not in ["lon_b", "lat_b", "U", "V"]:
                if len(self._ds[data].shape) == 5:
                    ds[data] = self._regrid_4D_data(self._ds[data])
                elif len(self._ds[data].shape) == 4:
                    ds[data] = self._regrid_3D_data(self._ds[data])
                elif len(self._ds[data].shape) == 3:
                    ds[data] = self.regrid_single_data(self._ds[data])
        return ds


    def regrid_single_data(self, data, **kwargs):
        data_out = np.zeros([self.grid['lat'].size, self.grid['lon'].size])
        for i in range(6):
            # add up the results for 6 tiles
            data_out += self.regridder[i](data.isel(**{FACEDIM:i}),**kwargs)
        return data_out

    def _regrid_4D_data(self, data, **kwargs):
        data_out = np.zeros([data.shape[1], data.shape[2], self.grid['lat'].size, self.grid['lon'].size])
        for i in range(6):
            # add up the results for 6 tiles
            data_out += self.regridder[i](data.isel(**{FACEDIM:i}),**kwargs)
        return data_out

    def _regrid_3D_data(self, data, **kwargs):
        data_out = np.zeros([data.shape[1], self.grid['lat'].size, self.grid['lon'].size])
        for i in range(6):
            # add up the results for 6 tiles
            data_out += self.regridder[i](data.isel(**{FACEDIM:i}),**kwargs)
        return data_out





