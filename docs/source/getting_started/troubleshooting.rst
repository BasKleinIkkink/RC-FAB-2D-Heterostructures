Troubleshooting
-----------------------------
Of course everything works in an ideal world and you will never have any problems. But if you do, here are some things to try.

Installation
^^^^^^^^^^^^^^^^^
If you are having problems installing the software, try the following:
1. Make sure you have > Python3.9 installed with pip up to date.

On windows
```
python3.exe -m pip install --upgrade pip
```

On Linux
```
python3 -m pip install --upgrade pip
```

2. Make sure the wheel library is installed. This should be installed by default but if not it can be installed using the following line
```
python3 -m pip install wheel
```

Starting the system
^^^^^^^^^^^^^^^^^^^^^^^^
If you have problems starting the instrument this can have multiple causes. The most common are:
1. Not all the hardware is active. This can be fixed by setting the Enabled boolean in the hardware config to True.
2. Not all the hardware powered on.
3. The hardware is not connected to the computer.
4. The software is broken. If this is the case this can be a bit hard to fix, for this purpose the package contains several test suites
to test the backend functionality.

.. warning::
    The test suite only test the software and are built as units as much as possible. This means that if there is a hardware problem
    (like a loose usb connection) the test suite will not be able to detect this and still pass.