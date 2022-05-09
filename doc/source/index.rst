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
- open datasets created by the `mnc <https://mitgcm.readthedocs.io/en/latest/outp_pkgs/outp_pkgs.html#netcdf-i-o-pkg-mnc>`_ package (depreciated)
- open datasets using `xmitgcm <https://xmitgcm.readthedocs.io/en/latest>`_ (needs current PR `#98 <https://github.com/MITgcm/xmitgcm/pull/98>`_ )
- plot original cubed sphere data
- some more small utilities
- more to come...

.. toctree::
   :maxdepth: 1
   :caption: Contents

   installation
   usage
   notebooks/example.ipynb
   exorad

Credits
-------
Many of the methods come from: https://github.com/JiaweiZhuang/cubedsphere

I would especially like to thank `@rabernat <https://github.com/rabernat>`_ for providing  `xgcm <https://xgcm.readthedocs.io/en/latest/>`_ and `@JiaweiZhuang <https://github.com/JiaweiZhuang>`_ for providing `xESMF <https://xesmf.readthedocs.io/en/latest/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


