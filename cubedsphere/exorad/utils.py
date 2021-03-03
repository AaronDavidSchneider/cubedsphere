import cubedsphere as cs
import cubedsphere.const as c
import numpy as np
import os

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

    # Check if the data file exists
    if not os.path.isfile(datafile):
        raise FileNotFoundError('Data file not found at: '+datafile)
    else: # if it does:
        valueFound = False
        with open(datafile, 'r') as f:
            for line in f.readlines():
                if keyword in line and line[0] != '#':
                    value = line.split(keyword+'=', 1)[1].rstrip().rstrip(',')
                    valueFound = True
                    return value
        if not valueFound:
            raise NameError(r'No value could be associated with the keyword: '+keyword)

def exorad_postprocessing(ds, outdir=None, datafile=None):
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

    Returns
    ----------
    ds:
        Dataset to be returned
    """
    assert outdir is not None or datafile is not None, "please specify a datafile or a folder where we can find a datafile"

    if outdir is not None:
        datafile = f'{outdir}/data'

    attrs = {"p_ref": float(get_parameter(datafile, 'Ro_SeaLevel')),  # bottom layer pressure in pascal
             "cp": float(get_parameter(datafile, 'atm_Cp')),          # heat capacity at constant pressure
             "R": float(get_parameter(datafile, 'atm_Rd')),           # specific gas constant
             "g": float(get_parameter(datafile, 'gravity')),          # surface gravity in m/s^2
             "dt": int(get_parameter(datafile, 'deltaT')),            # time step size in s
             "radius": float(get_parameter(datafile, 'rSphere'))      # planet radius in m
             }

    ds.attrs.update(attrs)

    kappa = attrs["R"] / attrs["cp"]

    # Convert Temperature
    ds[c.T] = ds[c.T]*(ds[c.Z] / attrs["p_ref"]) ** kappa

    # calculate scale height
    H = attrs["R"] / attrs["g"] * ds[c.T]

    # calculate geometric height, not needed here ?!
    z = - H * np.log(ds[c.Z] / attrs["p_ref"])

    # interpolate vertical windspeed to cell center:
    if c.FACEDIM in ds.dims:
        grid = cs.init_grid_CS(ds=ds)
    else:
        grid = cs.init_grid_LL(ds=ds)

    W_interp = grid.interp(ds[c.W], axis=c.Z, to="center")

    # convert vertical wind speed from Pa/s to m/s
    ds[c.W] = - W_interp * H / ds[c.Z]

    return ds