import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import qtawesome as qta


class FocusWidget(QGroupBox):
    name = 'Focus Widget'
    min_size = QSize(500, 250)
    max_size = min_size

    def __init__(self, settings, q, parent=None):
        """
        Initialize the focus widget

        Parameters
        ----------
        settings : Settings
            The settings object
        q : Queue
            The queue to send commands to
        parent : QWidget
            The parent widget
        """
        super().__init__(self.name, parent)
        # Define the main frame and grid in the docking widget
        self.settings = settings
        self.q = q
        self.mainHorizontalLayout = QHBoxLayout(self)
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)

        # Add the move mode buttons in a horizontal layout wth the move modes
        moveModeLayout = QHBoxLayout()
        moveModeLayout.addWidget(self._create_move_mode_buttons())
        moveModeLayout.addWidget(self._create_move_buttons())

        # Add the move mode layout to the main layout
        self.mainHorizontalLayout.addLayout(moveModeLayout)

        # Add a vertical divider
        self.controlDiv = QFrame(self)
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

        self.add_vel_presets(self.settings.focus_vel_presets)
        self.add_drive_step_presets(self.settings.focus_drive_step_presets)

        # Add the frame to the main layout
        self.mainHorizontalLayout.addWidget(frame)
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

    def add_drive_step_presets(self, presets=["1 um", "10 um", "100 um"]):
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

    def _create_move_mode_buttons(self):
        """Create the move mode buttons"""
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
        """Create the move buttons"""	
        moveFrame = QFrame()
        moveFrame.setMinimumSize(QSize(74, 220))
        moveFrame.setMaximumSize(QSize(74, 220))
        moveLayout = QVBoxLayout(moveFrame)

        # Add the up, lock and down buttons
        self.upButton = QPushButton(qta.icon("fa.angle-double-up", options=[{'scale_factor': 2,}]), "")
        self.lockButton = QPushButton(qta.icon("fa.lock", options=[{'scale_factor': 1.5,}]), "")
        self.downButton = QPushButton(qta.icon("fa.angle-double-down", options=[{'scale_factor': 2,}]), "")

        moveLayout.addWidget(self.upButton)
        moveLayout.addWidget(self.lockButton)
        self.lockButton.setCheckable(True)
        moveLayout.addWidget(self.downButton)

        # Set the sizes to 60x60
        self.upButton.setFixedSize(self.settings.button_size)
        self.lockButton.setFixedSize(self.settings.button_size)
        self.downButton.setFixedSize(self.settings.button_size)

        return moveFrame

    def _create_position_display_widget(self):
        """Create the position display widget"""
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
        """Create the move preset widget"""
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
        self.velDispLabel = QLabel()
        self.velDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s", None))
        self.velDisp = QSpinBox()
        self.velDisp.setFixedSize(self.settings.lcd_size)
        self.velDispLable = QLabel()

        # Add the drive step dropdown box
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

    def connect_actions(self, menubar, toolbar):
        """
        Connect the actions to the buttons
        
        Parameters
        ----------
        menubar : QMenuBar
            The menu bar
        toolbar : QToolBar
            The toolbar
        """
        
        # Connect the disp to the slider
        self.velocitySlider.valueChanged.connect(lambda : self.velDisp.setValue(self.velocitySlider.value()))
        self.velDisp.valueChanged.connect(lambda : self.velocitySlider.setValue(self.velDisp.value()))

        # Connect the movment buttons
        self.upButton.clicked.connect(self._move_z_up)
        self.downButton.clicked.connect(self._move_z_down)
        self.lockButton.clicked.connect(self._toggle_lock_movement)

        # Connect the move mode buttons
        self.jogButton.clicked.connect(self._turn_on_jog_mode)
        self.driveButton.clicked.connect(self._turn_on_drive_mode)

        self._connect_movement_scale()

    def _connect_movement_scale(self):
        """Connect the movement scale"""
        # Connect a change the move preset combo box to the movement scale
        self.movePresetCombo.currentIndexChanged.connect(self._change_movement_scale)

    def _change_movement_scale(self):
        """Change the movement scale"""
        # The new scale is between 0 and the given value in the given unit
        new_scale = self.movePresetCombo.currentText()
        self.moveScale = float(new_scale.split(" ")[0])
        self.moveUnit = new_scale.split(" ")[1]

        # Set the units on the sliders
        self.velDispLabel.setText(self.moveUnit)
        self.velocitySlider.setMaximum(int(self.moveScale))
        self.velDisp.setMaximum(self.moveScale)

    def _move_z_up(self):
        """Move the z stage up"""
        print("Move up")

    def _move_z_down(self):
        """Move the z stage down"""
        print("Move down")

    def _turn_on_drive_mode(self):
        """Turn on drive mode"""
        print("Turn on drive mode")

    def _turn_on_jog_mode(self):
        """Turn on jog mode"""
        print("Turn on jog mode")

    def _toggle_lock_movement(self):
        """Toggle the lock movement button"""
        print("Lock movement")
        button_state = self.lockButton.isChecked()
        self.upButton.setEnabled(not button_state)
        self.downButton.setEnabled(not button_state)