# RC-FAB-2D-Heterostructures
This project involves setting up a home-made transfer set up with commercially obtained linear, rotational and goniometer stages and writing Python codes to automate motorized micromanipulators, and temperature controllers so that the linear stages can be remote-controlled, giving us the flexibility to operate the set-up in a reproducible manner without any physical proximity with the operator.

## Frame
This project is developed with flexibility in mind, this means that it should be as easy as possible to add new components.

### Adding hardware
Each hardware component is descibed by a class that inherits from the harware/base.py Base class. The Base class holds all the functions and attributes that the system expect a part to have. Not all functions have to be supported by the new hardware (NotSupportedError is optional) but the functions that raise a NotImplementedError should always be supported.

When the hardware class is created it can be added by simply creating an instance of the hardware object in the stacking_setup.Stacking_setup __init__ method and add it to the _hardware list.

### Adding Gcode commands
The Gcode parser is also made to be easily modifiable. All commands that are accepted (with their attributes) are listed in the configs.accepted_commands.ini file.

## Installation
This program is developed with Windows in mind, all functions will probably work on the general unix distro's but only windows 10 functionality is tested

### Installing on windows
```bash
# For windows
python3 -m venv .venv
.venv\Scripts\activate.bat
pip3 install -r requirements.txt
```

### Installing on RPI
Before installing make sure the swapspace is 2048mb

```bash
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=2048
sudo /etc/init.d/dphys-swapfile restart

```

Now the needed packages can be installed without issues

```bash
# For Unix/Debian
# When using RPI3 or 4 make sure to increase the swapspace to 2048 mb before installing
python3 -m venv .venv
source .venv/bin/activate

```

Make sure to change the swapspace back to the original value. Not changing it back won't
cause major issues but will lessen the lifetime of the SD card due to more read/write operations.

## Usage
For now only usage directly from code is possible

## Known problems
After installing you may get the 
