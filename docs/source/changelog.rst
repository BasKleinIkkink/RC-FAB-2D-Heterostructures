Changelog
==============
.. note::
    From version V0.0.1 to V0.0.5 are no longer available on github. The reson for thius is that the packages
    contain too many bugs and are not stable enough to be used. The package is currently under development
    and only releases above version V1.0.0 can be considered stable.

V0.0.1
----------
Created the initial version of the package with the main structures for the backend middleware
and the frontend components.

V0.0.2
----------

Changed
^^^^^^^^^
- Moved some of the middleware functions to the :class:`Base` middleware class to make inheritance
for new middleware methods easier

Added
^^^^^^^^
- The first versions for the :class:`KIM101` and :class:`KDC101` classes for controlling the hardware
- The main parsing functions for the :class:`GcodeParser`
- Unittests for the :class:`GcodeParser`

Removed
^^^^^^^^^^
Not applicable

V0.0.3
----------

Changed
^^^^^^^^^
- Fixed thread safety issues with the controller classes and middleware by using threading locks
and multiprocessing events
- Moved general functions from the hardware class to a seperate class that can be used for class inheritance
- Moved the configuration settings to a seperate file for easier access and editing
- Created a file containing the accepted Gcode commands and their corresponding functions

Added
^^^^^^^^
- Added the emergency multiprocessing event and distibuted it to all hardware classes
- Added the unittest for the :class:`StackingSetupBackend`
- Added numpy style doctrings to the existing classes for autogenerating docs with Sphinx
- Added the controll classes for the :class:`PIA13` actuator.
- Added the :class:`PRMTZ8/M` for controlling the rotation stage
- Added the TUI frondend so the backend can be tested by sendig GcodeCommands to the backend

Removed
^^^^^^^^^^
Not applicable

V0.0.4
----------

Changed
^^^^^^^^^
- Edited the way error codes are passed from the component classes to the :class:`StackingSetupBackend` so 
errors are handled more elegantly (only critical errors will stop the system)

Added
^^^^^^^^
- Added the controll class for the TangoDesktop microscope controller
- Added the :class:`PipelineCommunication` class as a middleware method for running the backend in another process
on the same computer
- Added the :class:`SerialCommunication` class as a middleware method for running the backend on an IO controller
(for example RPI)

Removed
^^^^^^^^^^
Not applicable

V0.0.5
----------

Changed
^^^^^^^^^
- Moved the functionality of the :class:`PRMTZ8/M` to the :class:`SampleHolder` class

Added
^^^^^^^^
- Added the Ffirst version of the GUI made in PySide6 (QT)
- Added the :class:`MainXYController` class for controlling the main XY stage, sample heater and cooling.


