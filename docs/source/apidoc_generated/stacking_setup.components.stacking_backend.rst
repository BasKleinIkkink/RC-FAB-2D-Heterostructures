stacking\_backend package
====================================================

The backend contains all the needed modules to controll the connected hardware in a 
3D printer like style. The backend is build around the :func:`StackingSetupBackend` class.
The backend can be used as a standalone model and accepts Marlin flavour GCode commands over the
chosen :ref:`Middleware` method.

.. note::
   The backend workflow is pretty straight forward. The backend is initialized with a
   :class:`StackingSetup` object and is given an instance of a :ref:`middleware` object.
   All the communication to the backend should be send over the :ref:`middleware` object.

Subpackages
-----------

.. toctree::
   :maxdepth: 2

   stacking_setup.components.stacking_backend.components
   stacking_setup.components.stacking_backend.configs
   stacking_setup.components.stacking_backend.controllers

Submodules
----------

The main modules in the backend package contain the StackingSetupBackend and GcodeParser 
classes. These classes form the backbone of the system. Every piece of harware is initiated
and controlled from the StackingSetupBackend class and all commands are parsed by the 
GcodeParser class.


stacking\_backend.catch\_remote\_exceptions module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: stacking_setup.components.stacking_backend.catch_remote_exceptions
   :members:
   :undoc-members:
   :show-inheritance:

stacking\_backend.exceptions module
--------------------------------------------------------------

.. automodule:: stacking_setup.components.stacking_backend.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

stacking\_backend.gcode\_parser module
----------------------------------------------------------------

.. automodule:: stacking_setup.components.stacking_backend.gcode_parser
   :members:
   :undoc-members:
   :show-inheritance:

stacking\_backend.repeated\_timer module
-------------------------------------------------------------------

.. automodule:: stacking_setup.components.stacking_backend.repeated_timer
   :members:
   :undoc-members:
   :show-inheritance:

stacking\_backend.stacking\_setup module
-------------------------------------------------------------------

.. automodule:: stacking_setup.components.stacking_backend.stacking_setup
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: stacking_setup.components.stacking_backend
   :members:
   :undoc-members:
   :show-inheritance:
