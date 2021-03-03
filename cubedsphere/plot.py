"""
Library of utilities that can be used for plotting
"""

import numpy as np

from matplotlib import pyplot as plt
from matplotlib import cm

import cubedsphere.const as c
from .utils import _flatten_ds

def overplot_wind(ds_reg, U, V, stepsize=1):
    """
    Quick and dirty function for overplotting wind of a regridded dataset

    Parameters
    ----------
    ds_reg: xarray DataSet
        regridded dataset
    stepsize: integer
        specify the stepsize for which wind arrows should be plotted
    """
    ax = plt.gca()
    y, x = ds_reg["lat"].values, ds_reg["lon"].values
    xmesh, ymesh = np.meshgrid(x, y)
    ax.quiver(xmesh[::stepsize, ::stepsize], ymesh[::stepsize, ::stepsize], U[::stepsize, ::stepsize],
              V[::stepsize, ::stepsize])



def plotCS(dr, ds, mask_size=None, **kwargs):
    """
    A quick way to plot cubed-sphere data of resolution 6*N*N.
    Wrapping plotCS_quick_raw to work with xarray objects

    Parameters
    ----------
    dr: xarray DataArray
        The dimensions must be (y,x)
    ds: xarray DataSet (the parent DataSet of dr)
        Must contain XC, YC as coordinate variables.
    mask_size: None or int
        The overlap size of individual tiles. If None is chosen one might likely experience issues
    **kwargs
        Other keyword arguments such as cmap will be passed to plotCS_quick_raw() and subsequently to plt.pcolormesh()

    Returns
    -------
    ph: list
        List of mappabales
    """

    # must convert xarray objects to raw numpy arrays
    # otherwise numpy masking functions won't work

    x_dim, y_dim = c.lon, c.lat

    if len(ds[c.lon].shape) > 2:
        if ds[c.lon].shape[-1] == dr.shape[-1]:
            x_dim = c.lon
            x = _flatten_ds(ds[x_dim]).values
            data = _flatten_ds(dr).values
        elif ds[c.lon_b].shape[-1] == dr.shape[-1]:
            x_dim = c.lon_b
            x = _flatten_ds(ds[x_dim]).values
            data = _flatten_ds(dr).values
        if ds[c.lat].shape[-2] == dr.shape[-2]:
            y_dim = c.lat
            y = _flatten_ds(ds[y_dim]).values
        elif ds[c.lat_b].shape[-2] == dr.shape[-2]:
            y_dim = c.lat_b
            y = _flatten_ds(ds[y_dim]).values

    else:
        x = ds[x_dim].values
        y = ds[y_dim].values
        data = dr.values
    #assert dr.shape == ds[
    #    x_dim].shape, f"shape mismatch. shape of data: {dr.shape}, shape of coordinates: {ds[x_dim].shape}"
    #assert dr.shape == ds[
    #    y_dim].shape, f"shape mismatch. shape of data: {dr.shape}, shape of coordinates: {ds[y_dim].shape}"

    if mask_size is not None:
        try:
            mask = np.abs(x - 180) < mask_size
            data = np.ma.masked_where(mask, data)
        except IndexError:
            print("caution: No masking possible!")

    return _plot_cs_raw(x, y, data, **kwargs)


def _plot_cs_raw(x, y, data, projection=None, vmin=None, vmax=None, **kwargs):
    """
    Plots 2D scalar fields on the MITgcm cubed sphere grid with pcolormesh.

    Adapted from MITgcmutils (https://github.com/MITgcm/MITgcm/tree/master/utils/python/MITgcmutils/MITgcmutils/cs)

    Parameters
    ----------
    x: array_like
        'xg', that is, x coordinate of the points one half grid cell to the
        left and bottom, that is vorticity points for tracers, etc.
    y: array_like
        'yg', that is, y coordinate of same points
    data: array_like
        scalar field at tracer points
    projection: Basemap instance, optional
        used to transform if present.
        Unfortunatly, cylindrical and conic maps are limited to
        the [-180 180] range.
        projection = 'sphere' results in a 3D visualization on the sphere
        without any specific projection. Good for debugging.

    Returns
    -------
    ph: list
        List of mappabales
    """

    # pcol first divides the 2D cs-field(6*n,n) into six faces. Then for
    # each face, an extra row and colum is added from the neighboring faces in
    # order to fool pcolor into drawing the entire field and not just
    # (n-1,m-1) data points. There are two corner points that have no explicit
    # coordinates so that they have to be found by
    # interpolation/averaging. Then each face is divided into 4 tiles,
    # assuming cs-geometry, and each tile is plotted individually in
    # order to avoid problems due to ambigous longitude values (the jump
    # between -180 and 180, or 360 and 0 degrees). As long as the poles
    # are at the centers of the north and south faces and the first tile is
    # symmetric about its center this should work.

    # get the figure handle
    fig = plt.gcf()

    mapit = 0
    if projection != None:
        mp = projection
        if mp == 'sphere':
            mapit = -1
        else:
            mapit = 1

    # convert to [-180 180[ representation
    x = np.where(x > 180, x - 360., x)

    ny, nx = data.shape
    # determine range for color range
    cax = [data.min(), data.max()]
    if cax[1] - cax[0] == 0: cax = [cax[0] - 1, cax[1] + 1]

    if vmin != None: cax[0] = vmin
    if vmax != None: cax[1] = vmax

    if mapit == -1:
        # set up 3D plot
        if len(fig.axes) > 0:
            # if present, remove and replace the last axis of fig
            geom = fig.axes[-1].get_geometry()
            plt.delaxes(fig.axes[-1])
        else:
            # otherwise use full figure
            geom = ((1, 1, 1))
        ax = fig.add_subplot(geom[0], geom[1], geom[2], projection='3d',
                             facecolor='None')
        # define color range
        tmp = data - data.min()
        N = tmp / tmp.max()
        # use this colormap
        colmap = cm.jet
        colmap.set_bad('w', 1.0)
        mycolmap = colmap(N)  # cm.jet(N)

    ph = np.array([])
    jc = x.shape[0] // 2
    xxf = np.empty((jc + 1, jc + 1, 4))
    yyf = xxf
    ffld = np.empty((jc, jc, 4))
    xff = []
    yff = []
    fldf = []
    for k in range(0, 6):
        ix = np.arange(0, ny) + k * ny
        xff.append(x[0:ny, ix])
        yff.append(y[0:ny, ix])
        fldf.append(data[0:ny, ix])

    # find the missing corners by interpolation (one in the North Atlantic)
    xfodd = (xff[0][-1, 0] + xff[2][-1, 0] + xff[4][-1, 0]) / 3.
    yfodd = (yff[0][-1, 0] + yff[2][-1, 0] + yff[4][-1, 0]) / 3.
    # and one south of Australia
    xfeven = (xff[1][0, -1] + xff[3][0, -1] + xff[5][0, -1]) / 3.
    yfeven = (yff[1][0, -1] + yff[3][0, -1] + yff[5][0, -1]) / 3.

    # loop over tiles
    for k in range(0, 6):
        kodd = 2 * (k // 2)
        kodd2 = kodd
        if kodd == 4: kodd2 = kodd - 6
        keven = 2 * (k // 2)
        keven2 = keven
        if keven == 4: keven2 = keven - 6
        fld = fldf[k]
        if np.mod(k + 1, 2):
            xf = np.vstack([np.column_stack([xff[k], xff[1 + kodd][:, 0]]),
                            np.flipud(np.append(xff[2 + kodd2][:, 0], xfodd))])
            yf = np.vstack([np.column_stack([yff[k], yff[1 + kodd][:, 0]]),
                            np.flipud(np.append(yff[2 + kodd2][:, 0], yfodd))])
        else:
            xf = np.column_stack([np.vstack([xff[k], xff[2 + keven2][0, :]]),
                                  np.flipud(np.append(xff[3 + keven2][0, :],
                                                      xfeven))])
            yf = np.column_stack([np.vstack([yff[k], yff[2 + keven2][0, :]]),
                                  np.flipud(np.append(yff[3 + keven2][0, :],
                                                      yfeven))])

        if mapit == -1:
            ix = np.arange(0, ny) + k * ny
            # no projection at all (projection argument is 'sphere'),
            # just convert to cartesian coordinates and plot a 3D sphere
            deg2rad = np.pi / 180.
            xcart, ycart, zcart = _sph2cart(xf * deg2rad, yf * deg2rad)
            ax.plot_surface(xcart, ycart, zcart, rstride=1, cstride=1,
                            facecolors=mycolmap[0:ny, ix],
                            linewidth=2, shade=False)
            ph = np.append(ph, ax)
        else:
            # divide all faces into 4 because potential problems arise at
            # the centers
            for kf in range(0, 4):
                if kf == 0:
                    i0, i1, j0, j1 = 0, jc + 1, 0, jc + 1
                elif kf == 1:
                    i0, i1, j0, j1 = 0, jc + 1, jc, 2 * jc + 1
                elif kf == 2:
                    i0, i1, j0, j1 = jc, 2 * jc + 1, 0, jc + 1
                elif kf == 3:
                    i0, i1, j0, j1 = jc, 2 * jc + 1, jc, 2 * jc + 1
                xx = xf[i0:i1, j0:j1]
                yy = yf[i0:i1, j0:j1]
                ff = fld[i0:i1 - 1, j0:j1 - 1]
                if np.median(xx) < 0:
                    xx = np.where(xx >= 180, xx - 360., xx)
                else:
                    xx = np.where(xx <= -180, xx + 360., xx)

                # if provided use projection
                if mapit == 1: xx, yy = mp(xx, yy)

                # now finally plot 4x6 tiles
                ph = np.append(ph, plt.pcolormesh(xx, yy, ff,
                                                  vmin=cax[0], vmax=cax[1],
                                                  **kwargs))

    if mapit == -1:
        #        ax.axis('image')
        ax.set_axis_off()
        #        ax.set_visible=False
        # add a reasonable colormap
        m = cm.ScalarMappable(cmap=colmap)
        m.set_array(data)
        plt.colorbar(m)
    elif mapit == 0:
        ax = fig.axes[-1]
        ax.axis('image')
        plt.grid('on')

    return ph

def _sph2cart(azim_sph_coord, elev_sph_coord):
    r = np.cos(elev_sph_coord)
    x = -r * np.sin(azim_sph_coord)
    y = r * np.cos(azim_sph_coord)
    z = np.sin(elev_sph_coord)
    return x, y, z



