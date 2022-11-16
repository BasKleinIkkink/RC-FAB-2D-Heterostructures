import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import qtawesome as qta


class ControlDockWidget(QDockWidget):
    name = 'ControlDock'
    min_size = QSize(430, 380)
    max_size = min_size

    def __init__(self, settings, parent=None):
        """
        Initialize the control dock widget.
        
        Parameters
        ----------
        parent : QMainWindow
            Parent window of the dock widget.
        """
        super().__init__(self.name, parent)
        self.setting = settings

        # Set some window attributes.
        #self.textEdit = QTextEdit()
        #self.textEdit.setFontPointSize(16)
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)
        
        # Define the main frame and grid in the docking widget
        mainFrame = QFrame(self)
        mainVerticalLayout = QVBoxLayout(mainFrame)
        self.setWidget(mainFrame)

        # Ad the move modes and buttons
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self._create_move_mode_buttons())
        horizontalLayout.addWidget(self._create_move_buttons_widget())

        # Add a vertical divider (not a spacer)
        verticalDivider = QFrame()
        verticalDivider.setFrameShape(QFrame.VLine)
        verticalDivider.setFrameShadow(QFrame.Sunken)
        horizontalLayout.addWidget(verticalDivider)

        # Add the position displays and labels
        horizontalLayout.addWidget(self._create_position_display_widget())
        mainVerticalLayout.addLayout(horizontalLayout)

        # Add the divider between buttons and sliders
        controlDiv = QFrame(mainFrame)
        controlDiv.setFrameShape(QFrame.HLine)
        controlDiv.setFrameShadow(QFrame.Sunken)
        mainVerticalLayout.addWidget(controlDiv)

        # Add the parameter sliders
        mainVerticalLayout.addWidget(self._create_move_preset_widget())
        self.mainVerticalLayout = mainVerticalLayout
        self.mainFrame = mainFrame


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

    def _create_move_buttons_widget(self):
        # Create the move buttons
        arrowFrame = QFrame()
        arrowFrame.setMinimumSize(QSize(220, 220))
        arrowFrame.setMaximumSize(QSize(220, 220))
        grid_layout = QGridLayout(arrowFrame)
        
        # Create the layout and add the buttons
        self.moveRight = QPushButton(qta.icon("fa.angle-right", options=[{'scale_factor': 2,}]), "")
        self.moveRight.setMinimumSize(self.setting.button_size)
        self.moveRight.setMaximumSize(self.setting.button_size)
        self.moveRight.setStyleSheet(u"image: url(:/icons/arrows/arrow-right-solid.svg);")
        

        self.moveLeft = QPushButton(qta.icon("fa.angle-left", options=[{'scale_factor': 2,}]), "")
        self.moveLeft.setMinimumSize(self.setting.button_size)
        self.moveLeft.setMaximumSize(self.setting.button_size)
        
        self.moveDown = QPushButton(qta.icon("fa.angle-down", options=[{'scale_factor': 2,}]), "")
        self.moveDown.setMinimumSize(self.setting.button_size)
        self.moveDown.setMaximumSize(self.setting.button_size)

        self.moveUp = QPushButton(qta.icon("fa.angle-up", options=[{'scale_factor': 2,}]), "")
        self.moveUp.setMinimumSize(self.setting.button_size)
        self.moveUp.setMaximumSize(self.setting.button_size)

        # Add the move lock button
        self.lockMoveButton = QPushButton(qta.icon("fa.lock", options=[{'scale_factor': 1.5,}]), "")
        self.lockMoveButton.setMinimumSize(self.setting.button_size)
        self.lockMoveButton.setMaximumSize(self.setting.button_size)
        self.lockMoveButton.setCheckable(True)
        
        grid_layout.addWidget(self.moveRight, 1, 2, 1, 1)
        grid_layout.addWidget(self.moveLeft, 1, 0, 1, 1)
        grid_layout.addWidget(self.moveDown, 2, 1, 1, 1)
        grid_layout.addWidget(self.moveUp, 0, 1, 1, 1)
        grid_layout.addWidget(self.lockMoveButton, 1, 1, 1, 1)

        self.arrowGrid = grid_layout
        return arrowFrame

    def _create_move_mode_buttons(self):
        # Add the drive and jog move mode frame and layout
        moveModeFrame = QFrame()
        moveModeFrame.setMinimumSize(QSize(80, 200))
        moveModeFrame.setMaximumSize(QSize(80, 200))
        verticalLayout_3 = QVBoxLayout(moveModeFrame)  # Add the layout

        self.jogModeButton = QRadioButton(moveModeFrame)
        self.jogModeButton.setChecked(False)
        self.jogModeButton.setText(QCoreApplication.translate("MainWindow", u"Jog", None))
        verticalLayout_3.addWidget(self.jogModeButton)

        self.driveModeButton = QRadioButton(moveModeFrame)
        self.driveModeButton.setChecked(True)
        self.driveModeButton.setText(QCoreApplication.translate("MainWindow", u"Drive", None))
        verticalLayout_3.addWidget(self.driveModeButton)

        return moveModeFrame

    def _create_position_display_widget(self):
        # Add the position display frame and layout
        positionDisplayFrame = QFrame()
        gridLayout = QGridLayout(positionDisplayFrame)

        # Add the position labels
        self.xPosLabel = QLabel(positionDisplayFrame)
        self.xPosLabel.setText(QCoreApplication.translate("MainWindow", u"X:", None))
        gridLayout.addWidget(self.xPosLabel, 0, 0, 1, 1)

        self.yPosLabel = QLabel(positionDisplayFrame)
        self.yPosLabel.setText(QCoreApplication.translate("MainWindow", u"Y:", None))
        gridLayout.addWidget(self.yPosLabel, 1, 0, 1, 1)

        # Add the position displays
        self.xPosDisplay = QLCDNumber(positionDisplayFrame)
        self.xPosDisplay.setFrameShape(QFrame.StyledPanel)
        self.xPosDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.xPosDisplay.setFixedSize(self.setting.lcd_size)
        gridLayout.addWidget(self.xPosDisplay, 0, 1, 1, 1)

        self.yPosDisplay = QLCDNumber(positionDisplayFrame)
        self.yPosDisplay.setFrameShape(QFrame.StyledPanel)
        self.yPosDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.yPosDisplay.setFixedSize(self.setting.lcd_size)
        gridLayout.addWidget(self.yPosDisplay, 1, 1, 1, 1)

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
        self.velDisp.setFixedSize(self.setting.lcd_size)
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
        self.accDisp.setFixedSize(self.setting.lcd_size)

        

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

class MaskControlDockWidget(ControlDockWidget):
    name = "Mask and Sample Control"
    max_size = QSize(430, 800)

    def __init__(self, settings, parent=None):
        super().__init__(settings, parent)
        self._add_extra_buttons()
        self._add_extra_positions()
        self.add_vel_presets()

        # Add a divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.divider)

        self.mainVerticalLayout.addWidget(self._create_vacuum_settings())

    def _add_extra_buttons(self):
        #self.add_vel_presets()

        # Add the rotation buttons to the linear move frame
        self.rotateLeft = QPushButton(qta.icon("fa.rotate-left", options=[{'scale_factor': 1.3,}]), "")
        self.rotateLeft.setMinimumSize(self.setting.button_size)
        self.rotateLeft.setMaximumSize(self.setting.button_size)

        self.rotateRight = QPushButton(qta.icon("fa.rotate-right", options=[{'scale_factor': 1.3,}]), "")
        self.rotateRight.setMinimumSize(self.setting.button_size)
        self.rotateRight.setMaximumSize(self.setting.button_size)

        # Add the move up and down buttons to the buttonframe
        self.moveZUp = QPushButton(qta.icon("fa.angle-double-up", options=[{'scale_factor': 2,}]), "")
        self.moveZUp.setMinimumSize(self.setting.button_size)
        self.moveZUp.setMaximumSize(self.setting.button_size)


        self.moveZDown = QPushButton(qta.icon("fa.angle-double-down", options=[{'scale_factor': 2,}]), "")
        self.moveZDown.setMinimumSize(self.setting.button_size)
        self.moveZDown.setMaximumSize(self.setting.button_size)
        self.moveZDown.setStyleSheet(u"image: url(:/icons/arrows/arrow-down-solid.svg);")

        # Add the new buttons to the button frame
        self.arrowGrid.addWidget(self.rotateLeft, 0, 0, 1, 1)
        self.arrowGrid.addWidget(self.rotateRight, 0, 2, 1, 1)
        self.arrowGrid.addWidget(self.moveZUp, 2, 0, 1, 1)
        self.arrowGrid.addWidget(self.moveZDown, 2, 2, 1, 1)

    def _add_extra_positions(self):
        # Add the rotation buttons to the linear move frame
        self.yPosLabel = QLabel()
        self.yPosLabel.setText(QCoreApplication.translate("MainWindow", u"Z:", None))
        self.positionDisplayGrid.addWidget(self.yPosLabel, 3, 0, 1, 1)

        # Add the position displays
        self.xPosDisplay = QLCDNumber()
        self.xPosDisplay.setFrameShape(QFrame.StyledPanel)
        self.xPosDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.xPosDisplay.setFixedSize(self.setting.lcd_size)
        self.positionDisplayGrid.addWidget(self.xPosDisplay, 3, 1, 1, 1)

        self.yPosLabel = QLabel()
        self.yPosLabel.setText(QCoreApplication.translate("MainWindow", u"R:", None))
        self.positionDisplayGrid.addWidget(self.yPosLabel, 4, 0, 1, 1)

        # Add the position displays
        self.xPosDisplay = QLCDNumber()
        self.xPosDisplay.setFrameShape(QFrame.StyledPanel)
        self.xPosDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.xPosDisplay.setFixedSize(self.setting.lcd_size)
        self.positionDisplayGrid.addWidget(self.xPosDisplay, 4, 1, 1, 1)
        

    def _create_vacuum_settings(self):
        # Add the divider between the presets and vacuum settings
        vacFrame = QFrame()
        horizontalLayout = QHBoxLayout(vacFrame)

        # Add the start and stop vacuum buttons
        self.vacuumLabel = QLabel()
        horizontalLayout.addWidget(self.vacuumLabel)
        self.vacuumLabel.setText("Vacuum pump: ")
        self.startVacButton = QRadioButton()
        self.startVacButton.setChecked(False)
        self.startVacButton.setText("Start")
        horizontalLayout.addWidget(self.startVacButton)
        self.stopVacButton = QRadioButton()
        self.stopVacButton.setChecked(True)
        self.stopVacButton.setText("Stop")
        horizontalLayout.addWidget(self.stopVacButton)

        horizontalLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        return vacFrame

class BaseControlDockWidget(ControlDockWidget):
    name = "Base Control"

    def __init__(self, settings, parent=None):
        super().__init__(settings, parent)
        self.add_vel_presets()