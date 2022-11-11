import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class ControlDockWidget(QDockWidget):
    name = 'ControlDock'
    min_size = QSize(430, 380)
    max_size = min_size

    def __init__(self, parent=None):
        """
        Initialize the control dock widget.
        
        Parameters
        ----------
        parent : QMainWindow
            Parent window of the dock widget.
        """
        super().__init__(self.name, parent)
        self.setup_widget()

    def add_vel_presets(self, presets=["50 um/s", "500 um/s", "1 mm/s"]):
        """
        Add velocity presets to the velocity preset combo box
        
        Parameters
        ----------
        presets : list
            List of velocity presets to add to the combo box. Each entry has to
            follow the following syntax: <value> <unit> (seperated by a space).
        """
        for preset in presets:
            self.movePresetCombo.addItem(preset)

    def setup_widget(self):
        # Set some window attributes.
        self.textEdit = QTextEdit()
        self.textEdit.setFontPointSize(16)
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)

        # Define the main frame and grid in the docking widget
        self.controlFrame = QFrame(self)
        self.setWidget(self.controlFrame)
        self.controlFrame.setMinimumSize(QSize(400, 370))
        self.controlFrame.setMaximumSize(QSize(400, 370))
        self.controlFrame.setFrameShape(QFrame.StyledPanel)
        self.controlFrame.setFrameShadow(QFrame.Raised)
        self.grid_layout = QGridLayout(self.controlFrame)

        # Add the drive and jog move mode frame and layout
        self.moveModeFrame = QFrame(self.controlFrame)
        self.moveModeFrame.setMaximumSize(QSize(88, 220))
        self.moveModeFrame.setFrameShape(QFrame.StyledPanel)
        self.moveModeFrame.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3 = QVBoxLayout(self.moveModeFrame)  # Add the layout

        self.jogModeButton = QRadioButton(self.moveModeFrame)
        self.jogModeButton.setChecked(False)
        self.jogModeButton.setText(QCoreApplication.translate("MainWindow", u"Jog", None))
        self.verticalLayout_3.addWidget(self.jogModeButton)

        self.driveModeButton = QRadioButton(self.moveModeFrame)
        self.driveModeButton.setChecked(True)
        self.driveModeButton.setText(QCoreApplication.translate("MainWindow", u"Drive", None))
        self.verticalLayout_3.addWidget(self.driveModeButton)

        # Place the move mode frame in the dock frame
        self.grid_layout.addWidget(self.moveModeFrame, 0, 0, 1, 1)

        # Create the parameters frame and layout
        self.moveParamFrame = QFrame(self.controlFrame)
        self.moveParamFrame.setMinimumSize(QSize(370, 0))
        self.moveParamFrame.setMaximumSize(QSize(435, 112))
        self.moveParamFrame.setFrameShape(QFrame.StyledPanel)
        self.moveParamFrame.setFrameShadow(QFrame.Raised)
        self.grid_layout_9 = QGridLayout(self.moveParamFrame)

        # Create velocity presets
        self.movePresetLabel = QLabel(self.moveParamFrame)
        self.movePresetLabel.setText(QCoreApplication.translate("MainWindow", u"Presets :", None))
        self.grid_layout_9.addWidget(self.movePresetLabel, 0, 0, 1, 1)
        self.movePresetCombo = QComboBox(self.moveParamFrame)
        self.grid_layout_9.addWidget(self.movePresetCombo, 0, 1, 1, 3)

        # Create the velocity slider
        self.velSliderLabel = QLabel(self.moveParamFrame)
        self.velSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Velocity :", None))
        self.grid_layout_9.addWidget(self.velSliderLabel, 1, 0, 1, 1)
        self.velocitySlider = QSlider(self.moveParamFrame)  # Add the slider
        self.velocitySlider.setOrientation(Qt.Horizontal)
        self.grid_layout_9.addWidget(self.velocitySlider, 1, 1, 1, 1)  # Add the slider to the layout

        # Create the velocity value display
        self.velDispLabel = QLabel(self.moveParamFrame)
        self.grid_layout_9.addWidget(self.velDispLabel, 1, 3, 1, 1)
        self.velDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s", None))
        self.velDisp = QLCDNumber(self.moveParamFrame)
        self.velDisp.setFrameShape(QFrame.StyledPanel)
        self.velDisp.setDigitCount(3)
        self.velDisp.setSegmentStyle(QLCDNumber.Flat)
        self.grid_layout_9.addWidget(self.velDisp, 1, 2, 1, 1)
        self.velDispLable = QLabel(self.moveParamFrame)
        self.grid_layout_9.addWidget(self.velDispLable, 1, 3, 1, 1)

        # Connect the disp to the slider
        self.velocitySlider.sliderMoved.connect(self.velDisp.display)

        # Create the acceleration slider
        self.accSliderLabel = QLabel(self.moveParamFrame)
        self.accSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Acceleration :", None))
        self.grid_layout_9.addWidget(self.accSliderLabel, 2, 0, 1, 1)
        self.accSliderLabel = QLabel(self.moveParamFrame)
        self.grid_layout_9.addWidget(self.accSliderLabel, 2, 0, 1, 1)
        self.accSlider = QSlider(self.moveParamFrame)
        self.accSlider.setOrientation(Qt.Horizontal)
        self.grid_layout_9.addWidget(self.accSlider, 2, 1, 1, 1)

        # Create the acceleration value display
        self.accDispLabel = QLabel(self.moveParamFrame)
        self.accDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s^2", None))
        self.grid_layout_9.addWidget(self.accDispLabel, 2, 3, 1, 1)
        self.accDisp = QLCDNumber(self.moveParamFrame)
        self.accDisp.setFrameShape(QFrame.StyledPanel)
        self.accDisp.setDigitCount(3)
        self.accDisp.setSegmentStyle(QLCDNumber.Flat)
        self.grid_layout_9.addWidget(self.accDisp, 2, 2, 1, 1)
        self.accDispLabel = QLabel(self.moveParamFrame)
        self.grid_layout_9.addWidget(self.accDispLabel, 2, 3, 1, 1)

        # Connect the display to the slider
        self.accSlider.sliderMoved.connect(self.accDisp.display)

        # Add the movment parameters to the grid layout 
        self.grid_layout.addWidget(self.moveParamFrame, 3, 0, 1, 3)

        # Add the divider between buttons and sliders
        self.controlDiv = QFrame(self.controlFrame)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.grid_layout.addWidget(self.controlDiv, 1, 0, 1, 3)

        # Create the move buttons
        self.arrowFrame = QFrame(self.controlFrame)
        self.arrowFrame.setMinimumSize(QSize(220, 220))
        self.arrowFrame.setMaximumSize(QSize(220, 220))
        self.arrowFrame.setFrameShape(QFrame.StyledPanel)
        self.arrowFrame.setFrameShadow(QFrame.Raised)

        # Create the layout and add the buttons
        self.grid_layout_8 = QGridLayout(self.arrowFrame)
        self.moveRight = QPushButton(self.arrowFrame)
        self.moveRight.setMinimumSize(QSize(60, 60))
        self.moveRight.setMaximumSize(QSize(60, 60))
        self.moveRight.setStyleSheet(u"image: url(:/icons/arrows/arrow-right-solid.svg);")

        self.grid_layout_8.addWidget(self.moveRight, 1, 6, 1, 1)

        self.moveLeft = QPushButton(self.arrowFrame)
        self.moveLeft.setMinimumSize(QSize(60, 60))
        self.moveLeft.setMaximumSize(QSize(60, 60))
        self.moveLeft.setStyleSheet(u"image: url(:/icons/arrows/arrow-left-solid.svg);")

        self.grid_layout_8.addWidget(self.moveLeft, 1, 2, 1, 1)

        self.moveDown = QPushButton(self.arrowFrame)
        self.moveDown.setMinimumSize(QSize(60, 60))
        self.moveDown.setMaximumSize(QSize(60, 60))
        self.moveDown.setStyleSheet(u"image: url(:/icons/arrows/arrow-down-solid.svg);")

        self.grid_layout_8.addWidget(self.moveDown, 2, 4, 1, 1)

        self.moveUp = QPushButton(self.arrowFrame)
        self.moveUp.setMinimumSize(QSize(60, 60))
        self.moveUp.setMaximumSize(QSize(60, 60))
        self.moveUp.setStyleSheet(u"background-image: url(/icons/arrows/arrow-up-solid.png);")
        #self.moveUp.setIcon(QIcon("/icons/arrows/arrow-up-solid.svg"))
        #self.moveUp.setIconSize(QSize(60, 60))

        self.grid_layout_8.addWidget(self.moveUp, 0, 4, 1, 1)

        # Add the move lock button
        self.lockMoveButton = QPushButton(self.arrowFrame)
        self.lockMoveButton.setMinimumSize(QSize(60, 60))
        self.lockMoveButton.setMaximumSize(QSize(60, 60))
        self.lockMoveButton.setStyleSheet(u"image: url(:/icons/arrows/arrow-down-up-lock-solid.svg);")
        self.lockMoveButton.setCheckable(True)
        self.grid_layout_8.addWidget(self.lockMoveButton, 1, 4, 1, 1)
        self.grid_layout.addWidget(self.arrowFrame, 0, 1, 1, 1)


class MaskControlDockWidget(ControlDockWidget):
    name = "Mask Control"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_vel_presets()


class BaseControlDockWidget(ControlDockWidget):
    name = "Base Control"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_vel_presets()