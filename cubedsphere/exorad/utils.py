import astropy.units as u
import numpy as np
import os
from f90nml import Parser
import xarray as xr

import cubedsphere as cs
import cubedsphere.const as c


class MITgcmDataParser(Parser):
    def __init__(self):
        super().__init__()
        self.comment_tokens += '#'
        self.end_comma = True
        self.indent = " "
        self.column_width = 72
        self.sparse_arrays = True


def get_parameter(datafile, keyword):
    """
    Function to parse the MITgcm 'data' file and return the parameter values
    of the given specific keyword.

    Parameters
    ----------
    datafile: string
        Full path to the MITgcm data file.
    keyword: string
        Parameter of which the value is required.

    Returns
    ----------
    value: string
        The value associated with the given keyword is returned as a string (!).
    """

    if not os.path.isfile(datafile):
        raise FileNotFoundError("could not find the datafile.")

    parser = MITgcmDataParser()
    data = parser.read(datafile)

    for section in data:
        for key, val in data[section].items():
            if key.lower() == keyword.lower():
                return val

    raise KeyError("Keyword not found")


def convert_vertical_to_bar(ds, dim):
    """
    Convert the vertical dimension to bar.

    Parameters
    ----------
    ds: Dataset
        dataset to be converted
    dim: str
        Vertical dimension to be converted

    Returns
    -------
    ds: Dataset
        dataset with converted dimension
    """
    ds[dim] = (np.array(ds[dim]) * u.Pa).to(u.bar).value
    return ds


def convert_winds_and_T(ds, T_dim, W_dim):
    """
    Convert winds and temperature in dataset.
    Winds are converted from Pa/s to m/s.
    Temperatures are converted from potential temperature to ordinary temperature

    Parameters
    ----------
    ds: Dataset
        dataset to be converted
    T_dim: str
        temperature datadimension to be converted
    W_dim: str
        vertical wind datadimension to be converted

    Returns
    -------
    ds: Dataset
        dataset with converted dimension
    """
    kappa = ds.attrs["R"] / ds.attrs["cp"]
    ds[T_dim] = ds[T_dim] * (ds[c.Z] / ds.attrs["p_ref"]) ** kappa

    # calculate scale height
    H = ds.attrs["R"] / ds.attrs["g"] * ds[T_dim]

    # calculate geometric height
    ds[c.Z_geo] = - H * np.log(ds[c.Z] / ds.attrs["p_ref"])

    if W_dim in ds:
        # interpolate vertical windspeed to cell center:
        if c.FACEDIM in ds.dims:
            grid = cs.init_grid_CS(ds=ds)
        else:
            grid = cs.init_grid_LL(ds=ds)

        W_interp = grid.interp(ds[W_dim], axis=c.Z, to="center")

        # convert vertical wind speed from Pa/s to m/s
        ds[W_dim] = - W_interp * H / ds[c.Z]

    return ds


def exorad_postprocessing(ds, outdir=None, datafile=None, convert_to_bar=True, convert_to_days=True):
    """
    Preliminaray postprocessing on exorad dataset.
    This function converts the vertical windspeed from Pa into meters and saves attributes to the dataset.

    Parameters
    ----------
    ds: Dataset
        dataset to be extended
    outdir: string
        directory in which to find the data file (following the convention f'{outdir}/data')
    datafile: string
        alternatively specify datafile directly
    convert_to_bar: (Optional) bool
        convert vertical pressure dimension to bar
    convert_to_days: (Optional) bool
        convert time dimension to days

    Returns
    ----------
    ds:
        Dataset to be returned
    """
    assert outdir is not None or datafile is not None, "please specify a datafile or a folder where we can find a datafile"

    if outdir is not None:
        datafile = f'{outdir}/data'

    attrs = {"p_ref": float(get_parameter(datafile, 'Ro_SeaLevel')),  # bottom layer pressure in pascal
             "cp": float(get_parameter(datafile, 'atm_Cp')),  # heat capacity at constant pressure
             "R": float(get_parameter(datafile, 'atm_Rd')),  # specific gas constant
             "g": float(get_parameter(datafile, 'gravity')),  # surface gravity in m/s^2
             "dt": int(get_parameter(datafile, 'deltaT')),  # time step size in s
             "radius": float(get_parameter(datafile, 'rSphere'))  # planet radius in m
             }

    ds.attrs.update(attrs)

    # Convert Temperature and winds
    if c.T in ds:
        ds = convert_winds_and_T(ds, c.T, c.W)
    if c.Ttave in ds:
        ds = convert_winds_and_T(ds, c.Ttave, c.wVeltave)

    if convert_to_bar:
        for dim in {c.Z, c.Z_l, c.Z_p1, c.Z_u}:
            if dim in ds.dims:
                ds = convert_vertical_to_bar(ds, dim)

    if convert_to_days:
        ds[c.time] = ds.iter * ds.attrs["dt"] / (3600 * 24)

    return ds
