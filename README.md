# RC-FAB-2D-Heterostructures
This project involves setting up a home-made transfer set up with commercially obtained linear, rotational and goniometer stages and writing Python codes to automate motorized micromanipulators, and temperature controllers so that the linear stages can be remote-controlled, giving us the flexibility to operate the set-up in a reproducible manner without any physical proximity with the operator.

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
