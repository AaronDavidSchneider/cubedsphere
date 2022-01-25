Installation
============

.. warning::
   You need OSX or Linux to use this package. `ESMPy <https://earthsystemmodeling.org/esmpy/>`_ (the dependency that handles the regridding) does not work with Windows.

.. note::
   Currently ``xgcm==0.5.2`` is required. You will get errors if you use a different version``

Preparation
-----------
Create conda environment:

.. code-block:: bash

    conda create -n mitgcm

Activate environment:

.. code-block:: bash

    conda activate mitgcm


prepackaged installation
-------------------------
Install cubedsphere:

.. code-block:: bash

    conda install -c conda-forge cubedsphere


Alternative: Installation of development version
------------------------------------------------
Clone the repository:

.. code-block:: bash

    git clone https://github.com/AaronDavidSchneider/cubedsphere.git
    cd cubedsphere


Install dependencies:

.. code-block:: bash

    conda install -c conda-forge xesmf esmpy xgcm xmitgcm matplotlib-base xarray

Install cubedsphere:

.. code-block:: bash

    pip install -e .

You can now import the cubedsphere package from everywhere on your system
