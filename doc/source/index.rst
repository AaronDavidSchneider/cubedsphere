.. cubedsphere documentation master file, created by
   sphinx-quickstart on Mon Jan 11 14:18:49 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to cubedsphere's documentation!
=======================================
Library for post processing of MITgcm cubed sphere data

Capabilities
-------------
- regrid cubed sphere datasets using `xESMF <https://xesmf.readthedocs.io/en/latest>`_ and `xgcm <https://xgcm.readthedocs.io/en/latest>`_
- open datasets created by the `mnc <https://mitgcm.readthedocs.io/en/latest/outp_pkgs/outp_pkgs.html#netcdf-i-o-pkg-mnc>`_ package
- open datasets using `xmitgcm <https://xmitgcm.readthedocs.io/en/latest>`_ (needs current PR `#98 <https://github.com/MITgcm/xmitgcm/pull/98>`_ )
- plot original cubed sphere data
- some more small utilities
- more to come...

Note
-----
Work in progress! This library is a collection of tools that I found useful to use for the interpretation of cubed sphere data.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   installation
   usage
   examples
   exorad

ToDo
----
Postprocessing:

- [x] interface `xmitgcm` to enable the use of `.meta` and `.data` files *-> added wrapper*
- [x] how do we expand lon_b and lat_b from left to outer for xmitgcm wrapper? *-> either nc file or soon with `xmitgcm.utils.get_grid_from_input`*

Testing:

- [ ] compare results with matlab scripts

Interface:

- [x] which values should be hardcoded? *-> done in const.py*
- [x] special tools needed for exorad?

future Ideas:

- [ ] use `ESMPy <https://gist.github.com/JiaweiZhuang/990e8019c4103aec8353434a88f24b8a>`_ as an alternative to xESMF (requires 6 processors)

Credits
-------
Many of the methods come from: https://github.com/JiaweiZhuang/cubedsphere

I would especially like to thank `@rabernat <https://github.com/rabernat>`_ for providing  `xgcm <https://xgcm.readthedocs.io/en/latest/>`_ and `@JiaweiZhuang <https://github.com/JiaweiZhuang>`_ for providing `xESMF <https://xesmf.readthedocs.io/en/latest/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


