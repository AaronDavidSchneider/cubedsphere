Usage
=====

Reading Data
----------------
We can either read mds data using

.. autofunction:: cubedsphere.open_ascii_dataset

We can also read NETCDF data which has been outputed from the mnc package

.. autofunction:: cubedsphere.open_mnc_dataset

Regridding
----------
.. autoclass:: cubedsphere.Regridder
    :members:
    :special-members: __init__, __call__

Create XGCM grids
-----------------
.. autofunction:: cubedsphere.init_grid_CS
.. autofunction:: cubedsphere.init_grid_LL

Plotting
-----------------
.. autofunction:: cubedsphere.plotCS
.. autofunction:: cubedsphere.overplot_wind
