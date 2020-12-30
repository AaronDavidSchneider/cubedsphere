"""
Inspired from https://github.com/JiaweiZhuang/cubedsphere/blob/master/example_notebooks/C2L_regrid.ipynb
"""
import xesmf as xe
import numpy as np

def regrid(ds_in, ds_out, dr_in, filename=None):
    """Convenience function for one-time regridding"""
    regridder = xe.Regridder(ds_in, ds_out, method='conservative',
                             filename=filename)
    dr_out = regridder(dr_in)
    # keep weights on the disk for next time
    # regridder.clean_weight_file()

    return dr_out


def C2L(grid_CS_list, grid_LL, data_CS):
    '''
    Regrid Cubedsphere to LatLon
    '''
    data_out = np.zeros([grid_LL['lat'].size, grid_LL['lon'].size])
    for i in range(6):
        # add up the results for 6 tiles
        data_out += regrid(grid_CS_list[i], grid_LL, data_CS[i],
                           filename='weights_tile{0}.nc'.format(i + 1))

    return data_out