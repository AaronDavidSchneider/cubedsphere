# cubedsphere
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cubedsphere/badges/installer/conda.svg)](https://conda.anaconda.org/conda-forge) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/cubedsphere/badges/license.svg)](https://anaconda.org/conda-forge/cubedsphere) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/cubedsphere/badges/version.svg)](https://anaconda.org/conda-forge/cubedsphere) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/cubedsphere/badges/platforms.svg)](https://anaconda.org/conda-forge/cubedsphere) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/cubedsphere/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/cubedsphere)

Library for post processing of MITgcm cubed sphere data

## Capabilities:
- regrid cubed sphere datasets using [`xESMF`](https://xesmf.readthedocs.io/en/latest/) and [`xgcm`](https://xgcm.readthedocs.io/en/latest/)
- open datasets created by the [`mnc`](https://mitgcm.readthedocs.io/en/latest/outp_pkgs/outp_pkgs.html#netcdf-i-o-pkg-mnc) package
- open datasets using [`xmitgcm`](https://xmitgcm.readthedocs.io/en/latest/) (needs current PR [#98](https://github.com/MITgcm/xmitgcm/pull/98)) 
- plot original cubed sphere data
- some more small utilities
- more to come...

## Note:
Work in progress! This library is a collection of tools that I found useful to use for the interpretation of cubed sphere data.

## Getting Started
To learn how to install and use `cubedsphere` for your dataset, visit the [`cubedsphere` documentation](https://cubedsphere.readthedocs.io/en/latest).

## Credits
Many of the methods come from: https://github.com/JiaweiZhuang/cubedsphere

I would especially like to thank [@rabernat](https://github.com/rabernat) for providing  [`xgcm`](https://xgcm.readthedocs.io/en/latest/) and [@JiaweiZhuang](https://github.com/JiaweiZhuang) for providing [`xESMF`](https://xesmf.readthedocs.io/en/latest/).
