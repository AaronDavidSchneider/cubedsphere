Installation
============

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

    conda install -c conda-forge xesmf esmpy xgcm matplotlib cubedsphere

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