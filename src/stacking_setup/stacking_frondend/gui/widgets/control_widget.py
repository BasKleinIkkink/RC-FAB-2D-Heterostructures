import sys
from PySide6.QtCore import Qt, QSize, QCoreApplication
from PySide6.QtWidgets import (QComboBox, QGridLayout, QSpinBox, QLCDNumber,
                               QGroupBox, QHBoxLayout, QVBoxLayout, QLabel,
                               QFrame, QPushButton, QRadioButton, QSlider)
import qtawesome as qta


class ControlWidget(QGroupBox):
    name = 'ControlDock'
    min_size = QSize(430, 380)
    max_size = min_size

    def __init__(self, settings, q, parent=None):
        """
        Initialize the control dock widget.
        
        Parameters
        ----------
        settings : Settings
            The settings object.
        parent : QMainWindow
            Parent window of the dock widget.
        q : Queue
            Queue to send messages to the main thread.
        """
        super().__init__(self.name, parent)
        self.setting = settings
        self.q = q

        # Set some window attributes.
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)
        
        # Define the main frame and grid in the docking widget
        mainVerticalLayout = QVBoxLayout(self)

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
        controlDiv = QFrame(self)
        controlDiv.setFrameShape(QFrame.HLine)
        controlDiv.setFrameShadow(QFrame.Sunken)
        mainVerticalLayout.addWidget(controlDiv)

        # Add the parameter sliders
        mainVerticalLayout.addWidget(self._create_move_preset_widget())
        self.mainVerticalLayout = mainVerticalLayout
        self.mainFrame = self

    def add_vel_presets(self, presets=["50 um/s", "500 um/s", "1000 um/s"]):
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

        # Get the current selected
        new_scale = self.movePresetCombo.currentText()
        self.moveScale = float(new_scale.split(" ")[0])
        self.moveUnit = new_scale.split(" ")[1]

        # Set the units on the sliders
        self.velDispLabel.setText(self.moveUnit)
        self.velocitySlider.setMaximum(int(self.moveScale))
        self.velDisp.setMaximum(self.moveScale)

    def add_drive_step_presets(self, presets=["1 um", "500 nm",]):
        """
        Add drive step presets to the drive step combo box
        
        Parameters
        ----------
        presets : list
            List of drive step presets to add to the combo box. Each entry has to
            follow the following syntax: <value> <unit> (seperated by a space).
        """
        for preset in presets:
            self.driveStepCombo.addItem(preset)

        # Get the current selected
        new_scale = self.driveStepCombo.currentText()
        self.driveScale = float(new_scale.split(" ")[0])
        self.driveUnit = new_scale.split(" ")[1]

    def _create_move_buttons_widget(self):
        """Create the move buttons widget."""
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
        """Create the move mode buttons widget."""
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
        """Create the position display widget."""
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
        """Create the move preset widget."""
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
        self.velDisp = QSpinBox()
        self.velDisp.setFixedSize(self.setting.lcd_size)
        self.velDispLable = QLabel(moveParamFrame)

        # Drive step preset dropdown box
        self.driveStepLabel = QLabel(moveParamFrame)
        self.driveStepLabel.setText(QCoreApplication.translate("MainWindow", u"Drive step :", None))
        self.driveStepCombo = QComboBox(moveParamFrame)

        # Add everything to the layout
        moveParamGrid.addWidget(self.movePresetLabel, 0, 0, 1, 1)
        moveParamGrid.addWidget(self.movePresetCombo, 0, 1, 1, 3)
        moveParamGrid.addWidget(self.velSliderLabel, 1, 0, 1, 1)
        moveParamGrid.addWidget(self.velocitySlider, 1, 1, 1, 2)  # Add the slider to the layout
        moveParamGrid.addWidget(self.velDispLabel, 1, 4, 1, 1)
        moveParamGrid.addWidget(self.velDisp, 1, 3, 1, 1)
        moveParamGrid.addWidget(self.driveStepLabel, 2, 0, 1, 1)
        moveParamGrid.addWidget(self.driveStepCombo, 2, 1, 1, 3)

        self.moveParamGrid = moveParamGrid
        return moveParamFrame


class MaskControlWidget(ControlWidget):
    name = "Mask and Sample Control"
    max_size = QSize(430, 450)
    min_size = max_size

    def __init__(self, settings, q, parent=None):
        """Create the mask control widget."""
        super().__init__(settings, q, parent)
        self._add_extra_buttons()
        self._add_extra_positions()

        # Get and set the preset vaues
        self.add_vel_presets(self.setting.mask_vel_presets)
        self.add_drive_step_presets(self.setting.mask_drive_step_presets)

        # Add a divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.divider)

        self.mainVerticalLayout.addWidget(self._create_vacuum_settings())

    def _add_extra_buttons(self):
        """Add the extra buttons to the widget."""

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
        """Add the extra positions to the widget."""
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
        """Create the vacuum settings frame."""
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

    def connect_actions(self, menubar, toolbar):
        """
        Connect the actions to the buttons.
        
        Parameters
        ----------
        menubar : QMenuBar
            The menu bar to connect the actions to.
        toolbar : QToolBar
            The toolbar to connect the actions to.
        """
        # Connect the buttons to the actions
        self.moveLeft.clicked.connect(self._move_left)
        self.moveRight.clicked.connect(self._move_right)
        self.moveUp.clicked.connect(self._move_up)
        self.moveDown.clicked.connect(self._move_down)
        self.rotateLeft.clicked.connect(self._rotate_left)
        self.rotateRight.clicked.connect(self._rotate_right)
        self.moveZUp.clicked.connect(self._move_z_up)
        self.moveZDown.clicked.connect(self._move_z_down)
        self.lockMoveButton.clicked.connect(self._lock_movement)

        # Connect vacuum pump buttons
        self.startVacButton.clicked.connect(self._turn_on_vacuum)
        self.stopVacButton.clicked.connect(self._turn_off_vacuum)

        # Connect the move mode buttons
        self.jogModeButton.clicked.connect(self._turn_on_jog_mode)
        self.driveModeButton.clicked.connect(self._turn_on_drive_mode)
        self._connect_movement_scale()

        # Connect the disp to the slider
        self.velocitySlider.valueChanged.connect(lambda : self.velDisp.setValue(self.velocitySlider.value()))
        self.velDisp.valueChanged.connect(lambda : self.velocitySlider.setValue(self.velDisp.value()))

    def _connect_movement_scale(self):
        """Connect the movement scale to the movement buttons."""
        # Connect a change the move preset combo box to the movement scale
        self.movePresetCombo.currentIndexChanged.connect(self._change_movement_scale)

    def _change_movement_scale(self):
        """Change the movement scale based on the move preset combo box."""
        # The new scale is between 0 and the given value in the given unit
        new_scale = self.movePresetCombo.currentText()
        self.moveScale = float(new_scale.split(" ")[0])
        self.moveUnit = new_scale.split(" ")[1]

        # Set the units and scale on the sliders
        self.velDispLabel.setText(self.moveUnit)
        self.velocitySlider.setMaximum(int(self.moveScale))
        self.velDisp.setMaximum(self.moveScale)

    def _move_left(self):
        """Move the stage left."""
        print("Move left")

    def _move_right(self):
        """Move the stage right."""
        print("Move right")

    def _move_up(self):
        """Move the stage up."""
        print("Move up")

    def _move_down(self):
        """Move the stage down."""
        print("Move down")

    def _rotate_left(self):
        """Rotate the stage left."""
        self.q.put('G1 L1')
        print("Rotate left")

    def _rotate_right(self):
        """Rotate the stage right."""
        self.q.put('G1 L-1')
        print("Rotate right")

    def _move_z_up(self):
        """Move the stage up in the z direction."""
        print("Move z up")

    def _move_z_down(self):
        """Move the stage down in the z direction."""
        print("Move z down")

    def _turn_on_vacuum(self):
        """Turn on the vacuum pump."""
        print("Turn on vacuum")

    def _turn_off_vacuum(self):
        """Turn off the vacuum pump."""
        print("Turn off vacuum")

    def _turn_on_drive_mode(self):
        """Turn on drive mode."""
        print("Turn on drive mode")

    def _turn_on_jog_mode(self):
        """Turn on jog mode."""
        print("Turn on jog mode")

    def _lock_movement(self):
        """Lock the movement of the stage."""
        print("Lock movement")
        button_state = self.lockMoveButton.isChecked()
        self.moveUp.setEnabled(not button_state)
        self.moveDown.setEnabled(not button_state)
        self.moveLeft.setEnabled(not button_state)
        self.moveRight.setEnabled(not button_state)
        self.rotateLeft.setEnabled(not button_state)
        self.rotateRight.setEnabled(not button_state)
        self.moveZUp.setEnabled(not button_state)
        self.moveZDown.setEnabled(not button_state)

    
class BaseControlWidget(ControlWidget):
    name = "Base Control"

    def __init__(self, settings, q, parent=None):
        """Initialize the base control widget."""
        super().__init__(settings, q, parent)
        self.add_vel_presets(self.setting.base_vel_presets)
        self.add_drive_step_presets(self.setting.base_drive_step_presets)

    def connect_actions(self, menubar, toolbar):
        """
        Connect the actions to the buttons.
        
        Parameters
        ----------
        menubar : QMenuBar
            The menu bar to add the menu to.
        toolbar : QToolBar
            The toolbar to add the buttons to.
        """
        # Connect the buttons to the actions
        self.moveLeft.clicked.connect(self._move_left)
        self.moveRight.clicked.connect(self._move_right)
        self.moveUp.clicked.connect(self._move_up)
        self.moveDown.clicked.connect(self._move_down)
        self.lockMoveButton.clicked.connect(self._lock_movement)

        # Connect the move mode buttons
        self.jogModeButton.clicked.connect(self._turn_on_jog_mode)
        self.driveModeButton.clicked.connect(self._turn_on_drive_mode)

        # Connect the disp to the slider
        self.velocitySlider.valueChanged.connect(lambda : self.velDisp.setValue(self.velocitySlider.value()))
        # Connect the spinbox to the slider
        self.velDisp.valueChanged.connect(lambda : self.velocitySlider.setValue(self.velDisp.value()))

        self._connect_movement_scale()

    def _connect_movement_scale(self):
        """Connect the movement scale to the movement buttons."""
        # Connect a change the move preset combo box to the movement scale
        self.movePresetCombo.currentIndexChanged.connect(self._change_movement_scale)

    def _change_movement_scale(self):
        """Change the movement scale based on the move preset combo box."""
        # The new scale is between 0 and the given value in the given unit
        new_scale = self.movePresetCombo.currentText()
        self.moveScale = float(new_scale.split(" ")[0])
        self.moveUnit = new_scale.split(" ")[1]

        # Set the units on the sliders
        self.velDispLabel.setText(self.moveUnit)
        self.velocitySlider.setMaximum(int(self.moveScale))
        self.velDisp.setMaximum(self.moveScale)

    def _move_left(self):
        """Move the stage left."""
        print("Move left")

    def _move_right(self):
        """Move the stage right."""
        print("Move right")

    def _move_up(self):
        """Move the stage up."""
        print("Move up")

    def _move_down(self):
        """Move the stage down."""
        print("Move down")

    def _lock_movement(self):
        """Lock the movement of the stage."""
        print("Lock movement")
        button_state = self.lockMoveButton.isChecked()
        self.moveUp.setEnabled(not button_state)
        self.moveDown.setEnabled(not button_state)
        self.moveLeft.setEnabled(not button_state)
        self.moveRight.setEnabled(not button_state)

    def _turn_on_drive_mode(self):
        """Turn on drive mode."""
        print("Turn on drive mode")

    def _turn_on_jog_mode(self):
        """Turn on jog mode."""
        print("Turn on jog mode")