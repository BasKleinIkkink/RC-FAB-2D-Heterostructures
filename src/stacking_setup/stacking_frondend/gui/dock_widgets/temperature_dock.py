import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCharts import QChart, QSplineSeries, QValueAxis
from PySide6.QtCharts import QChart, QChartView
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPen
import random


class TemperatureDockWidget(QDockWidget):
    name = 'Temperature Dock'
    min_size = QSize(450, 450)
    max_size = QSize(500, 450)

    def __init__(self, settings, parent=None):
        """
        Initialize the control dock widget.
        
        Parameters
        ----------
        parent : QMainWindow
            Parent window of the dock widget.
        """
        super().__init__(self.name, parent)
        self.settings = settings
        # Define the main frame and grid in the docking widget
        self.mainFrame = QFrame(self)
        self.setWidget(self.mainFrame)
        self.mainVerticalLayout = QVBoxLayout(self.mainFrame)
        self.setMinimumSize(self.min_size)
        self.setMaximumSize(self.max_size)

        # Add the chart
        self.mainVerticalLayout.addWidget(self._create_chart())

        # Add the divider
        self.controlDiv = QFrame(self.mainFrame)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.controlDiv)

        # Add the temperature params
        self.mainVerticalLayout.addWidget(self._create_temp_params())

    def _create_save_and_reset(self):
        pass

    def _create_temp_params(self):
        paramFrame = QFrame()
        gridLayout = QGridLayout(paramFrame)
        
        # Add the presets and spinbox
        spin_box = QSpinBox()
        spin_box.setValue(50)

        # Add the spinbox label and unit label
        tempSpinLabel = QLabel()
        tempSpinLabel.setText("Temperature :")
        tempSpinUnit = QLabel()
        tempSpinUnit.setText("°C")

        # Add the presets and combo box
        self.tempPresetCombo = QComboBox()
        presetLabel = QLabel()
        presetLabel.setText("Presets :")

        # Add the params to the grid
        gridLayout.addWidget(tempSpinLabel, 1, 0, 1, 1)
        gridLayout.addWidget(spin_box, 1, 1, 1, 1)
        gridLayout.addWidget(tempSpinUnit, 1, 2, 1, 1)
        gridLayout.addWidget(presetLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.tempPresetCombo, 0, 1, 1, 1)

        return paramFrame

    def _create_chart(self):
        """Add the chart to the main frame."""
        chart = self.Chart()
        chart.setTitle("Temperature")
        chart.legend().hide()
        chart.setAnimationOptions(QChart.AllAnimations)
        self.chart_view = QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        return self.chart_view

    def add_temp_presets(self, presets=[]):
        """Add the temperature presets to the combo box."""
        for i in presets:
            self.tempPresetCombo.addItem(i)

    class Chart(QChart):

        def __init__(self, parent=None):
            super().__init__(QChart.ChartTypeCartesian, parent, Qt.WindowFlags())
            self._timer = QTimer()
            self._series = QSplineSeries(self)
            self._titles = []
            self._axisX = QValueAxis()
            self._axisY = QValueAxis()
            self._step = 0
            self._x = 5
            self._y = 1

            #self._timer.timeout.connect(self.handleTimeout)
            #self._timer.setInterval(1000)

            green = QPen(Qt.green)
            green.setWidth(3)
            self._series.setPen(green)
            self._series.append(self._x, self._y)

            self.addSeries(self._series)
            self.addAxis(self._axisX, Qt.AlignBottom)
            self.addAxis(self._axisY, Qt.AlignLeft)

            self._series.attachAxis(self._axisX)
            self._series.attachAxis(self._axisY)
            self._axisX.setTickCount(5)
            self._axisX.setRange(0, 10)
            self._axisY.setRange(-5, 10)

            self._timer.start()

        @Slot()
        def handleTimeout(self):
            x = self.plotArea().width() / self._axisX.tickCount()
            y = (self._axisX.max() - self._axisX.min()) / self._axisX.tickCount()
            self._x += y
            self._y = random.uniform(0, 5) - 2.5
            self._series.append(self._x, self._y)
            self.scroll(x, 0)
            if self._x == 100:
                self._timer.stop()