Installation
============

.. warning::
   You need OSX or Linux to use this package. `ESMPy <`https://earthsystemmodeling.org/esmpy/>`_ (the dependency that handles the regridding) does not work with Windows.


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

.. warning::
   You currently need to perform an extra step to open ascii files (the default MITgcm output).
   Go to a direction where you store code, open a terminal and type:

   .. code-block:: bash

      git clone https://github.com/MITgcm/xmitgcm.git
      cd xmitgcm
      git fetch origin pull/98/head:cs_support
      git checkout cs_support
      pip install -e .

   Keep an eye on the PR `#98 <https://github.com/MITgcm/xmitgcm/pull/98>`_. The above steps will not be nescessary anymore once this pullrequest has been merged.


Alternative: Installation of development version
------------------------------------------------
Clone the repository:

.. code-block:: bash

    git clone https://github.com/AaronDavidSchneider/cubedsphere.git
    cd cubedsphere


Install dependencies:

.. code-block:: bash

    conda install -c conda-forge xesmf esmpy xgcm matplotlib

Install cubedsphere:

.. code-block:: bash

    pip install -e .

You can now import the cubedsphere package from everywhere on your system