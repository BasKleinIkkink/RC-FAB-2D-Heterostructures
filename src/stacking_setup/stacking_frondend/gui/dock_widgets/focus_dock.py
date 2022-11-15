import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class FocusDockWidget(QDockWidget):
    name = 'FocusDock'
    min_size = QSize(500, 250)
    max_size = min_size

    def __init__(self, settings, parent=None):
        super().__init__(self.name, parent)
        # Define the main frame and grid in the docking widget
        self.settings = settings
        self.mainFrame = QFrame(self)
        self.setWidget(self.mainFrame)
        self.mainHorizontalLayout = QHBoxLayout(self.mainFrame)
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)

        # Add the move mode buttons in a horizontal layout wth the move modes
        moveModeLayout = QHBoxLayout()
        moveModeLayout.addWidget(self._create_move_mode_buttons())
        moveModeLayout.addWidget(self._create_move_buttons())

        # Add the move mode layout to the main layout
        self.mainHorizontalLayout.addLayout(moveModeLayout)

        # Add a vertical divider
        self.controlDiv = QFrame(self.mainFrame)
        self.controlDiv.setFrameShape(QFrame.VLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.mainHorizontalLayout.addWidget(self.controlDiv)

        # Add the position display widget and params in a vertical layout
        frame = QFrame()
        vertLayout = QVBoxLayout(frame)
        vertLayout.addWidget(self._create_position_display_widget())

        # Add a horizontal divider
        self.controlDiv = QFrame(frame)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        vertLayout.addWidget(self.controlDiv)

        # Add the params
        vertLayout.addWidget(self._create_move_preset_widget())

        # Add the frame to the main layout
        self.mainHorizontalLayout.addWidget(frame)


    def _create_move_mode_buttons(self):
        # Create the move mode buttons
        moveModeFrame = QFrame()
        moveModeLayout = QVBoxLayout(moveModeFrame)

        self.jogButton = QRadioButton("Jog")
        self.jogButton.setChecked(False)

        self.driveButton = QRadioButton("Drive")
        self.driveButton.setChecked(True)

        moveModeLayout.addWidget(self.jogButton)
        moveModeLayout.addWidget(self.driveButton)

        return moveModeFrame

    def _create_move_buttons(self):
        moveFrame = QFrame()
        moveFrame.setMinimumSize(QSize(74, 220))
        moveFrame.setMaximumSize(QSize(74, 220))
        moveLayout = QVBoxLayout(moveFrame)

        # Add the up, lock and down buttons
        self.upButton = QPushButton()
        self.lockButton = QPushButton()
        self.downButton = QPushButton()

        moveLayout.addWidget(self.upButton)
        moveLayout.addWidget(self.lockButton)
        moveLayout.addWidget(self.downButton)

        # Set the sizes to 60x60
        self.upButton.setFixedSize(self.settings.button_size)
        self.lockButton.setFixedSize(self.settings.button_size)
        self.downButton.setFixedSize(self.settings.button_size)

        return moveFrame

    def _create_position_display_widget(self):
        # Add the position display frame and layout
        positionDisplayFrame = QFrame()
        gridLayout = QGridLayout(positionDisplayFrame)

        # Set a fixed zise
        positionDisplayFrame.setMinimumSize(QSize(60, 60))
        positionDisplayFrame.setMaximumSize(QSize(100, 150))

        # Add the position labels
        self.zPosLabel = QLabel(positionDisplayFrame)
        self.zPosLabel.setText(QCoreApplication.translate("MainWindow", u"Z:", None))
        gridLayout.addWidget(self.zPosLabel, 0, 0, 1, 1)

        # Add the position displays
        self.zPosDisplay = QLCDNumber(positionDisplayFrame)
        self.zPosDisplay.setFrameShape(QFrame.StyledPanel)
        self.zPosDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.zPosDisplay.setFixedSize(self.settings.lcd_size)
        gridLayout.addWidget(self.zPosDisplay, 0, 1, 1, 1)

        self.positionDisplayGrid = gridLayout
        return positionDisplayFrame

    def _create_move_preset_widget(self):
        ## Create the parameters frame and layout
        moveParamFrame = QFrame()
        moveParamGrid = QGridLayout(moveParamFrame)
        
        # Create velocity presets
        self.movePresetLabel = QLabel(moveParamFrame)
        self.movePresetLabel.setText(QCoreApplication.translate("MainWindow", u"Scale :", None))
        self.movePresetCombo = QComboBox(moveParamFrame)

        # Create the velocity slider
        self.velSliderLabel = QLabel(moveParamFrame)
        self.velSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Velocity :", None))
        self.velocitySlider = QSlider(moveParamFrame)  # Add the slider
        self.velocitySlider.setOrientation(Qt.Horizontal)

        # Create the velocity value display
        self.velDispLabel = QLabel(moveParamFrame)
        self.velDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s", None))
        self.velDisp = QLCDNumber(moveParamFrame)
        self.velDisp.setFrameShape(QFrame.StyledPanel)
        self.velDisp.setSegmentStyle(QLCDNumber.Flat)
        self.velDisp.setFixedSize(self.settings.lcd_size)
        # Set the size to the same a the rest of the displays
        self.velDispLable = QLabel(moveParamFrame)

        # Connect the disp to the slider
        self.velocitySlider.sliderMoved.connect(self.velDisp.display)

        # Create the acceleration slider
        self.accSliderLabel = QLabel(moveParamFrame)
        self.accSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Acceleration :", None))
        self.accSlider = QSlider(moveParamFrame)
        self.accSlider.setOrientation(Qt.Horizontal)

        # Create the acceleration value display
        self.accDispLabel = QLabel(moveParamFrame)
        self.accDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s^2", None))
        self.accDisp = QLCDNumber(moveParamFrame)
        self.accDisp.setFrameShape(QFrame.StyledPanel)
        self.accDisp.setSegmentStyle(QLCDNumber.Flat)
        self.accDisp.setFixedSize(self.settings.lcd_size)
        
        # Add everything to the layout
        moveParamGrid.addWidget(self.movePresetLabel, 0, 0, 1, 1)
        moveParamGrid.addWidget(self.movePresetCombo, 0, 1, 1, 3)

        moveParamGrid.addWidget(self.velSliderLabel, 1, 0, 1, 1)
        moveParamGrid.addWidget(self.velocitySlider, 1, 1, 1, 2)  # Add the slider to the layout
        moveParamGrid.addWidget(self.velDispLabel, 1, 4, 1, 1)
        moveParamGrid.addWidget(self.velDisp, 1, 3, 1, 1)

        moveParamGrid.addWidget(self.accSliderLabel, 2, 0, 1, 1)
        moveParamGrid.addWidget(self.accSlider, 2, 1, 1, 2)
        moveParamGrid.addWidget(self.accDispLabel, 2, 4, 1, 1)
        moveParamGrid.addWidget(self.accDisp, 2, 3, 1, 1)

        # Connect the display to the slider
        self.accSlider.sliderMoved.connect(self.accDisp.display)

        self.moveParamGrid = moveParamGrid
        return moveParamFrame