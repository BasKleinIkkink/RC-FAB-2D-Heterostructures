Gotchas
----------------------------
Thera are some nuances in the software that are good to know during operation and/or development


Backend
^^^^^^^^^^^^^^
- There are no range boundries set (except for the base xy stages), this is due to the fact that the piezos have inaccurate positioning and
the rotation stage can rotate continues. This means that the software will not stop you from moving the stages outside of the range of the part.
This means the parts can get damaged if the operator is not careful.

Graphical user interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- The GUI can be used to change the velocity of the stages at once. This means the rotation and mask speed are changed at the same time. Because
two move on different scales the piezos are capped on a max speed when a high rotation speed is set and the rotation is capped at a minimum speed when
the piezos are set to a low speed etc.

.. attention::
    This works the same for drive steps. A consequence of this is that when f.e. a 10mm drive step is set it will take a very long time for the piezo to
    move this distance, as the speed is not that high.