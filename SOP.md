# Dora the Explorer Standard Operating Procedure
date: 13-02-2023
by: Bas Klein Ikkink

## Introduction
Welcome to the short SOP fot the Dora the Explorer stacking setup. This file
will give a short explanation on the different functions of the instrument.

Why Dora the Explorer? Well we are exploring the wonderful world of van der 
Waals Heterostructures aren't we?

## General
### Startup
1. Turn on the main instrument power block
2. Turn on the components
	a. KIM101
	b. KDC101
	c. TangoDesktop
	d. Olympus LED source
3. Turn on the PC power block and the PC

### Shutdown
DO NOT TURN OFF THE POWERBLOCK FIRST!!
2. Turn off all the components seperatly
3. Turn off the component power block
4. Turn off the PC
5. Turn off the PC power block

### Graphical User Interface operation.
1. Run the main.py file in the RC-2D-FAB-Heterostructures folder.
2. Wait for the base stage homing to finish
3. The system can now be controlled using the arrow keys in two different modes
	Drive: Move a predetermined distance
	Jog: Move until the button is released by the user
4. The temperature can be controlled by changing the temperature in the drop
	box or type in the wanted temperature. To start or stop heating toggle the PID
	button
5. The interface can be stopped by simply clicking the X in the top right corner
	
### Command Line Interface operation
NOT RECOMMENDED FOR NORMAL USERS!! USE THE GUI INSTEAD
1. Open the main.py file in the RC-2D-FAB-Heterostructures folder.
2. Comment out line 9 and uncomment line 8.
3. Run the file to start the system
4. Wait for the base stage homing to finish
5. The system can now be controlled using Gcode commands (see the
	stacking setup backend class documentation for supported commands)
6. The interface can be stopped by sending the command 'exit()'

## Troubleshooting
In most cases the error showed in the terminal gives enough information to fix the error
(in most cases hardware is not powered or connected). Turning the system on and off is also
a solid strategy.

