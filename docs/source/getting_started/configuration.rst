Configuration
=============

.. _configuration:
The project can be configured in two ways: local and remote. The main difference is if an
external IO controller is used or not. These examples are the most basic ways to configure the 
setup, but there are many more options available by creating a custom :class:`Middleware` method (see 
:ref:`programming_guidelines`).

.. _local_hardware_configuration:

Local configuration
-------------------

This is the easies configuration to set up, but depending on the used operating
system not all functions may be supported. In the local configuration all processes run
on one single system, in this case the main computer. The local configuration method 
is recommended for when new modules are being developed. This configuation has some pros 
and cons:

Pros
****
* Easy to set up
* Easy to debug

Cons
****
* Not all functions may be supported
* Instrument performance can be influenced by other processes running on the same
  computer (for example during a high workload)

.. warning::
    The xbox controller control mode is not supported on windows.

Local config example
********************

.. code-block:: python

    # This code block is an example of how to set up the local configuration
    # using a pipeline connection to run the backend on another cpu core.

    # Import the frond- and backend
    from stacking_setup.stacking_frondend.tui.main import main as ui_main
    from stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend

    # Import the middleware that connects the frond- and backend by mp.pipe for local use
    from multiprocessing import Pipe
    from stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection
    parent, child = Pipe()

    # Initiate the frond- and backend
    backend = StackingSetupBackend(PipelineConnection(child, 'BACKEND'))
    backend.start_backend()
    ui_main(PipelineConnection(parent, 'UI'))

.. _remote_hardware_configuration:

Remote configuration
--------------------

.. attention::
  Due to issues with the FTDI driver on Debian it is not possble to use all hardware 
  functions on a Raspberry Pi. All hardware that depend on the PyLabLib library will
  not work. This includes the Piezo actuators and rotation stage.

.. note::
  For some classes it is known that they do not work on a Raspberry Pi. For other
  classes this was not tested but in theory it should work.

In the remote configuration the processes are distributed over multiple systems. The
remote configuration is recommended for when the system is used in a production
environment. This configuration is more complex to set up, but has some advantages:

Pros
****
* All functions are supported
* Instrument performance is not influenced by other processes running on the same
  computer

Cons
****
* More complex to set up
* Harder to debug

Remote config example
*********************

With the remote setup there are two parts to the code. The first part is the code that
runs on the main computer, this is the same as the local configuration. The second part
is the code that runs on the remote computer (IO controller). The remote computer is the computer that
controls the hardware. The remote computer can be a Raspberry Pi or another computer with 
enough USB ports to connect all the hardware.

Python code for the main computer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # This code block is meanth to be run on he main computer
    # Import the frondend and the middleware methode. Because the remote setup is used
    # the pipeline connection cannot be used and a serial connection is used instead.
    from stacking_setup.stacking_frondend.tui.main import main as ui_main
    from stacking_setup.stacking_middleware.serial_connection import SerialConnection

    # When a remote middleware is used a handshake is performed before the user is allowed
    # to use the system. This is to prevent the user from using the system when the remote
    # computer is not connected.

    # Initiate the frondend
    ui_main(SerialConnection('COM3', 'UI'))

Python code for the remote computer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # This code block is meanth to be run on the remote computer
    # Import the backend and the middleware methode. Because the remote setup is used
    # the pipeline connection cannot be used and a serial connection is used instead.
    from stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend
    from stacking_setup.stacking_middleware.serial_connection import SerialConnection

    # Initiate the backend
    backend = StackingSetupBackend(SerialConnection('COM3', 'BACKEND'))
    backend.start_backend()