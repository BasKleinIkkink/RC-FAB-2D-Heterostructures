import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                                 QGroupBox, QComboBox, QCheckBox, QSpinBox,
                                 QLCDNumber, QGridLayout)
from PySide6.QtCharts import (QChart, QLineSeries, QValueAxis,
                            QChart, QChartView)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPen
import random


class TemperatureWidget(QGroupBox):
    name = 'Temperature Dock'
    min_size = QSize(450, 450)
    max_size = QSize(500, 450)

    def __init__(self, settings, q, parent=None):
        """
        Initialize the control dock widget.
        
        Parameters
        ----------
        settings : Settings
            The settings object.
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
        self.mainVerticalLayout.addWidget(self._create_chart())
        self.mainVerticalLayout.addWidget(self._create_numeric_temp_indicator())

        # Add the divider
        self.controlDiv = QFrame(self)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.controlDiv)

        # Add the temperature params
        self.mainVerticalLayout.addWidget(self._create_temp_params())
        self.mainFrame = self

        # Add another divider
        self.controlDiv = QFrame(self)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.controlDiv)

        self.mainVerticalLayout.addWidget(self._create_custom_ramping())

        self.add_temp_presets()

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
        gridLayout.addWidget(self.tempSpinLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.target_spin_box, 1, 1, 1, 1)
        gridLayout.addWidget(self.tempSpinUnit, 1, 2, 1, 1)
        gridLayout.addWidget(self.presetLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.tempPresetCombo, 0, 1, 1, 1)

        return paramFrame

    def _create_custom_ramping(self):
        """Create the widgets needed for custom ramping"""
        self.coolRampLabel = QLabel()
        self.coolRampLabel.setText("Cooling ramp :")
        self.coolRampCombo = QComboBox()
        self.coolRampCombo.addItem("Default")

        self.heatRampLabel = QLabel()
        self.heatRampLabel.setText("Heating ramp :")
        self.heatRampCombo = QComboBox()
        self.heatRampCombo.addItem("Default")

        frame = QFrame()
        grid = QGridLayout(frame)
        grid.addWidget(self.coolRampLabel, 0, 0, 1, 1)
        grid.addWidget(self.coolRampCombo, 0, 1, 1, 2)
        grid.addWidget(self.heatRampLabel, 1, 0, 1, 1)
        grid.addWidget(self.heatRampCombo, 1, 1, 1, 2)
        return frame

    def _create_chart(self):
        """Add the chart to the main frame."""
        chart = self.Chart()
        chart.legend().hide()
        chart.setAnimationOptions(QChart.AllAnimations)
        self.chart_view = QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart = chart
        return self.chart_view

    def add_temp_presets(self, presets=["0 °C", "50 °C", "100 °C", "150 °C", "200 °C"]):
        """Add the temperature presets to the combo box."""
        for i in presets:
            self.tempPresetCombo.addItem(i)

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
        self.target_spin_box.valueChanged.connect(self._change_target_indicator)
        # self.target_spin_box.valueChanged.connect(self._set_custom_preset)

        # Connect the target spinbox to the combobox change
        self.tempPresetCombo.currentIndexChanged.connect(self._change_spinbox_value)

        # Set the indicator to the current spinbox value
        self.targetTempDisp.display(self.target_spin_box.value())

    def _change_target_indicator(self):
        """Change the target temperature of the indicator."""
        print('Change target indicator')
        self.targetTempDisp.display(self.target_spin_box.value())

        # Aslo update the value in the graph
        self.chart.target_temp = self.target_spin_box.value()

    def _change_spinbox_value(self):
        """Change the value of the spinbox depending on the selected preset."""
        print('Lock spinbox value')
        
        if self.tempPresetCombo.currentIndex() == 0:
            # Set the max value to 250
            self.target_spin_box.setDisabled(False)
            self.target_spin_box.setMaximum(250)
        else:
            # Set the spinbox to the selected value and disable
            value = int(self.tempPresetCombo.currentText().split(" ")[0])
            self.target_spin_box.setMaximum(value)
            self.target_spin_box.setValue(value)
            self.target_spin_box.setDisabled(True)

    def update_temperatures(self, temps):
        """Update the current temperature of the indicator."""
        if 'N' in temps:
            self.currentTempDisp.display(temps['N']['current'])
            self.targetTempDisp.display(temps['N']['target'])


    class Chart(QChart):

        def __init__(self, parent=None):
            super().__init__(QChart.ChartTypeCartesian, parent, Qt.WindowFlags())
            self._timer = QTimer()
            self._series = QLineSeries(self)
            self._set_temp = QLineSeries(self)
            self._titles = []
            self._axisX = QValueAxis()
            self._axisY = QValueAxis()
            self._step = 0
            self._x = 0
            self._y = 0
            self._target_temp = 0
            self.step_size = 1

            self._timer.timeout.connect(self.handleTimeout)
            self._timer.setInterval(1000)

            green = QPen(Qt.green)
            green.setWidth(3)
            self._series.setPen(green)
            self._series.append(self._x, self._y)

            red = QPen(Qt.red)
            red.setWidth(3)
            self._set_temp.setPen(red)
            self._set_temp.append(self._x, self._target_temp)

            self.addSeries(self._series)
            self.addSeries(self._set_temp)
            self.addAxis(self._axisX, Qt.AlignBottom)
            self.addAxis(self._axisY, Qt.AlignLeft)

            self._series.attachAxis(self._axisX)
            self._series.attachAxis(self._axisY)
            self._set_temp.attachAxis(self._axisX)
            self._set_temp.attachAxis(self._axisY)
            self._axisX.setTickCount(10)
            self._axisX.setRange(0, 60)
            self._axisY.setRange(0, 50)
            
            # Change the background to transparent
            brush = QBrush(Qt.transparent)
            self.setBackgroundBrush(brush)

            # Set the ylasbel as the temperature unit
            self._axisY.setTitleText("Temp (°C)")
            self._axisX.setTitleText("Time (s)")

            self._timer.start()

        @property
        def target_temp(self):
            return self._target_temp

        @target_temp.setter
        def target_temp(self, value):
            self._target_temp = value

        @Slot()
        def handleTimeout(self):
            x = self.plotArea().width() / self._axisX.tickCount()
            y = (self._axisX.max() - self._axisX.min()) / self._axisX.tickCount()
            self._x += y
            self._y = random.uniform(0, 50) - 2.5
            self._series.append(self._x, self._y)
            self._set_temp.append(self._x, self._target_temp)

            # Update the y axis mx to 10% above the max value
            if self._y > self._target_temp:
                self._axisY.setRange(0, y)
            else:
                self._axisY.setRange(0, self._target_temp)

            self.scroll(x, 0)
            #if self._x == 100:
            #    self._timer.stop()

            # Always plot the target temp in red
