.. _programming_guidelines:

Programming guidelines
======================

Because this project is bigger than the average program a TN student writes
it is important to keep a consistant syntax and style over the complete program
for this reason we have decided to use the following guidelines

* Use 4 spaces for indentation
* Use 80 characters per line
* Use camelCase with the first letter uppercase for classes
* Use snake_case for variables and functions
* Use numpy style docstrings
    * Give a summary of every function
    * Give a description of every parameter (do not use : in the description, sphinx does not like it)
    * Give a description of the return value
* Use type hints and typeguarding for functions that accept input or give an output

.. note::

    Type hinting and typeguarding are not nessessary for functionality but make a more rugget
    program and make it easier to read and understand. It also makes debugging in the remote configuration
    easier.

.. note::

    For some more info on typeguarding and hinting see the following links:
    * `type hinting <https://docs.python.org/3/library/typing.html>`_
    * `typeguarding <https://pypi.org/project/typeguard/>`_

New module guidelines
---------------------

The python program is developed with the idea of modularity in mind, this means
that the program functionality should be easily extendable and by users. To make
this as easy as possible the following guidelines are used:

* New functionality is implemented by classes that inherit from the respective
    base class. This means:
    * New hardware modules should inherit from stacking_setup.stacking_backend.hardware.base.Base
    * New middleware modules should inherit from stacking_setup.stacking_backend.middleware.base.BaseConnector
* To make the system more rugget static typing and typeguarding is used to make
    sure that the correct types are passed to the functions. This means that
    every function that accepts input or gives an output other than None should have 
    a type annotation using ``typing`` and the ``@typechecked`` decorator
    should be used. For more information see the typeguard documentation
    (https://typeguard.readthedocs.io/en/latest/)

New command guidelines
----------------------

Because the system is controlled using the Marlin Gcode command set it is also
possible to add new commands to the system. To make this as easy as possible the 
following guidelines are used:

* New commands should be added to the ``stacking_setup.stacking_backend.stacking_setup.StackingSetupBackend`` class. The function name should be the ID of the command, for example ``M114()``.
* The command function should accept the attributes in dict format (see the  ``stacking_setup.stacking_backend.gcode_parser.GcodeParser`` class for more information)
* The command name, accepted attributes and attirbute types should be added to the ACCEPTED_COMMANDS dict in the ``stacking_setup.stacking_backend.config.accepted_commands.py`` file