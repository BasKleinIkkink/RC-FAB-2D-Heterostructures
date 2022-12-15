.. _installation:

Installation
============

Before the library can be used, it must be installed.

Deciding installation method
----------------------------

It is possible to install the library in multible ways and in multiple
configurations. Below is a short summary of installation methods and
usefull configurations

Pulling from github
-------------------

The easies way to install the library is to use the git repository. This does
mean that the complete libraty will be installed (frondend, middleware and backend)
this is normally not a problem but can cause issues on some systems.

To get the code from the git repository use the following command:

.. code-block:: bash

    git clone https://github.com/Nynra/RC-FAB-2D-Heterostructure.git

.. note::
    Because the library is in development it is saved in a private repository and 
    can only be accessed by the developers. If you want access to the repository
    please send an email to PI-Bhattacharyya-Members@Physics.LeidenUniv.nl with
    your github username, and reason for access

This will build a wheel from the source code and install it in the current
python environment. This is the recommended way to install the library.

Installing from local file
--------------------------

If you have a local copy of the source code it is also possible to partly install
the library. This can for now only be done by deleting the unwanted files from the
source code. This is not recommended but can be usefull if you want to install
only the backend or the middleware. The wheel file for installation can then be build 
using the following command:

On windows:

.. code-block:: bash

    python -m build


On linux:

.. code-block:: bash

    python3 -m build
