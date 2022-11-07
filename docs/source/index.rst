.. Stacking setup documentation master file, created by
   sphinx-quickstart on Wed Oct 26 11:45:28 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Stacking setup's documentation!
==========================================

**Stacking setup** is a python library that is used to control custrom stacking setups for stacking 2D materials. The library consists of 3 parts: The backend, frondend, and middleware. 
All of the hardware control takes place in the backend components, all interactions with the user (except for CLI) takes place in the frondend components, the middleware connects the frond and backend.

.. note::

    The library is still in development and is not yet ready for use.

Getting started
---------------
.. toctree::
   :maxdepth: 1

   getting_started/getting_started
   LICENSE

Library contents
----------------
.. toctree::
   :maxdepth: 2

   apidoc_generated/modules
   apidoc_generated/stacking_setup.stacking_frondend
   apidoc_generated/stacking_setup.stacking_middleware
   apidoc_generated/stacking_setup.stacking_backend


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
