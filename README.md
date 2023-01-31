# RC-FAB-2D-Heterostructures
This project involves setting up a home-made transfer set up with commercially obtained linear, rotational and goniometer stages and writing Python codes to automate motorized micromanipulators, and temperature controllers so that the linear stages can be remote-controlled, giving us the flexibility to operate the set-up in a reproducible manner without any physical proximity with the operator.

For more information about the package see the docs folder. If you want to build the html documentation from the .rst files run the following code from within the repository folder.

```bash
pip3 install sphinx
pip3 install fugro
cd docs
make html
```

The documentation can now be found in the `docs -> build -> html` folder

## Installation
This program is developed with Windows in mind, all functions will probably work on the general unix distro's but only windows 10 functionality is tested

From local repository folder
```bash
# For windows
python3 -m venv .venv
.venv\Scripts\activate.bat
pip3 install -r requirements.txt
```


