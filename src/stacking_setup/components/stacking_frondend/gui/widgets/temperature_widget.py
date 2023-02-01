import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QGroupBox,
    QComboBox,
    QRadioButton,
    QSpinBox,
    QLCDNumber,
    QGridLayout,
)
from PySide6.QtCharts import QChart, QLineSeries, QValueAxis, QChart, QChartView
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPen
import random


class TemperatureWidget(QGroupBox):
    name = "Temperature Widget"
    min_size = QSize(500, 200)
    max_size = QSize(500, 200)

    def __init__(self, settings, q, parent=None):
        """
        Initialize the control dock widget.

        Parameters
        ----------
        settings : Settings
            The settings object.
        q : Queue
            The queue object.
        parent : QMainWindow
            Parent window of the dock widget.
        """
        super().__init__(self.name, parent)
        self.settings = settings
        self.q = q
        # Define the main frame and grid in the docking widget
        self.mainVerticalLayout = QVBoxLayout(self)
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)

        # Add the chart
        # self.mainVerticalLayout.addWidget(self._create_chart())
        self.mainVerticalLayout.addWidget(self._create_numeric_temp_indicator())

        # Add the divider
        self.controlDiv = QFrame(self)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.controlDiv)

        # Add the temperature params
        self.mainVerticalLayout.addWidget(self._create_temp_params())
        self.mainFrame = self

        self.add_temp_presets(self.settings.temp_presets)

    def _create_save_and_reset(self):
        pass

    def _create_numeric_temp_indicator(self):
        """Add the numeric temperature indicator to the main frame."""
        frame = QFrame()
        horziontalLayout = QHBoxLayout(frame)
        self.targetLabel = QLabel("Target")
        self.tempUnitLabel = QLabel("°C")
        self.currentTempLabel = QLabel("Current")
        self.currentTempUnitLabel = QLabel("°C")
        self.targetTempDisp = QLCDNumber()
        self.currentTempDisp = QLCDNumber()

        # Set the styling of the lcd displays
        self.targetTempDisp.setSegmentStyle(QLCDNumber.Flat)
        self.currentTempDisp.setSegmentStyle(QLCDNumber.Flat)
        self.targetTempDisp.setFrameShape(QFrame.StyledPanel)
        self.currentTempDisp.setFrameShape(QFrame.StyledPanel)

        # Set the indicator size
        self.targetTempDisp.setFixedSize(self.settings.lcd_size)
        self.currentTempDisp.setFixedSize(self.settings.lcd_size)

        # Add to the frame layout
        horziontalLayout.addWidget(self.targetLabel)
        horziontalLayout.addWidget(self.targetTempDisp)
        horziontalLayout.addWidget(self.tempUnitLabel)
        horziontalLayout.addWidget(self.currentTempLabel)
        horziontalLayout.addWidget(self.currentTempDisp)
        horziontalLayout.addWidget(self.currentTempUnitLabel)
        return frame

    def _create_temp_params(self):
        paramFrame = QFrame()
        gridLayout = QGridLayout(paramFrame)

        # Add the on off toggle
        self.pid_toggle = QRadioButton()
        self.pid_toggle_label = QLabel()
        self.pid_toggle_label.setText("PID on/off:")

        # Add the presets and spinbox
        self.target_spin_box = QSpinBox()
        self.target_spin_box.setValue(0)

        # Add the spinbox label and unit label
        self.tempSpinLabel = QLabel()
        self.tempSpinLabel.setText("Target temperature :")
        self.tempSpinUnit = QLabel()
        self.tempSpinUnit.setText("°C")

        # Add the presets and combo box
        self.tempPresetCombo = QComboBox()
        self.tempPresetCombo.addItem("Custom")
        self.presetLabel = QLabel()
        self.presetLabel.setText("Presets :")

        # Add the params to the grid
        gridLayout.addWidget(self.tempSpinLabel, 2, 0, 1, 1)
        gridLayout.addWidget(self.target_spin_box, 2, 1, 1, 1)
        gridLayout.addWidget(self.tempSpinUnit, 2, 2, 2, 1)
        gridLayout.addWidget(self.presetLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.tempPresetCombo, 1, 1, 1, 1)
        gridLayout.addWidget(self.pid_toggle_label, 0, 0, 1, 1)
        gridLayout.addWidget(self.pid_toggle, 0, 1, 1, 1)

        return paramFrame

    # def _create_custom_ramping(self):
    #     """Create the widgets needed for custom ramping"""
    #     self.coolRampLabel = QLabel()
    #     self.coolRampLabel.setText("Cooling ramp :")
    #     self.coolRampCombo = QComboBox()
    #     self.coolRampCombo.addItem("Default")

    #     self.heatRampLabel = QLabel()
    #     self.heatRampLabel.setText("Heating ramp :")
    #     self.heatRampCombo = QComboBox()
    #     self.heatRampCombo.addItem("Default")

    #     frame = QFrame()
    #     grid = QGridLayout(frame)
    #     grid.addWidget(self.coolRampLabel, 0, 0, 1, 1)
    #     grid.addWidget(self.coolRampCombo, 0, 1, 1, 2)
    #     grid.addWidget(self.heatRampLabel, 1, 0, 1, 1)
    #     grid.addWidget(self.heatRampCombo, 1, 1, 1, 2)
    #     return frame

    def add_temp_presets(self, presets=["0 °C", "50 °C", "100 °C", "150 °C", "200 °C"]):
        """Add the temperature presets to the combo box."""
        for i in presets:
            self.tempPresetCombo.addItem(str(i))

    def connect_actions(self, menubar, toolbar):
        """
        Connect the actions to the menubar and toolbar.

        Parameters
        ----------
        menubar : QMenuBar
            The menubar of the main window.
        toolbar : QToolBar
            The toolbar of the main window.
        """
        # Connect the spinbox to the target temp indicator
        self.target_spin_box.valueChanged.connect(self._change_target_temp)
        self.pid_toggle.clicked.connect(self._toggle_pid)

        # Connect the target spinbox to the combobox change
        self.tempPresetCombo.currentIndexChanged.connect(self._change_spinbox_value)

        # Set the indicator to the current spinbox value
        self.targetTempDisp.display(self.target_spin_box.value())

    def _toggle_pid(self):
        state = 1 if self.pid_toggle.isChecked() else 0
        self.q.put('M815 S{}'.format(state))

    def _change_target_temp(self):
        """Change the target temperature of the indicator."""
        self.q.put('M140 S{}'.format(self.target_spin_box.value()))

    def _change_spinbox_value(self):
        """Change the value of the spinbox depending on the selected preset."""
        if self.tempPresetCombo.currentIndex() == 0:
            # Set the max value to 220
            self.target_spin_box.setDisabled(False)
            self.target_spin_box.setMaximum(220)
        else:
            # Set the spinbox to the selected value and disable
            value = int(self.tempPresetCombo.currentText().split(" ")[0])
            self.target_spin_box.setMaximum(value)
            self.target_spin_box.setValue(value)
            self.target_spin_box.setDisabled(True)

        # Send the updated target to the backend
        self._change_target_temp()

    def update_temperature(self, temp):
        """Update the current temperature of the indicator."""
        if 'L' not in temp.keys():
            return
        self.currentTempDisp.display(temp['L']['current'])
        self.targetTempDisp.display(temp['L']['target'])

    def estop(self, state=False):
        # Disable the sliders and spinboxes
        self.target_spin_box.setEnabled(state)
        self.tempPresetCombo.setEnabled(state)
        self.target_spin_box.setValue(23)
