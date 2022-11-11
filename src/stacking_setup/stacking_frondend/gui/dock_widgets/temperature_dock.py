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

    def setup_widget(self):
        """Set up the widget."""
        # Define the main frame and grid in the docking widget
        self.mainFrame = QFrame(self)
        self.setWidget(self.mainFrame)
        self.mainFrame.setMinimumSize(QSize(420, 420))
        self.mainFrame.setMaximumSize(QSize(420, 420))
        self.mainFrame.setFrameShape(QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QFrame.Raised)
        self.verticle_layout = QVBoxLayout(self.mainFrame)

        # Add the chart
        self._add_chart()

        # Add the divider
        self.controlDiv = QFrame(self.mainFrame)
        self.controlDiv.setFrameShape(QFrame.HLine)
        self.controlDiv.setFrameShadow(QFrame.Sunken)
        self.verticle_layout.addWidget(self.controlDiv)

        # Create the parameters frame and layout
        self.tempParamFrame = QFrame(self.mainFrame)
        self.tempParamFrame.setMinimumSize(QSize(370, 0))
        self.tempParamFrame.setMaximumSize(QSize(435, 112))
        self.tempParamFrame.setFrameShape(QFrame.StyledPanel)
        self.tempParamFrame.setFrameShadow(QFrame.Raised)
        self.grid_layout = QGridLayout(self.tempParamFrame)

        spin_box = QSpinBox()
        spin_box.setValue(50)
        self.grid_layout.addWidget(spin_box, 0, 1, 1, 2)

        # Add the parameters frame to the main grid layout
        self.verticle_layout.addWidget(self.tempParamFrame)

    def _add_chart(self):
        """Add the chart to the main frame."""
        chart = self.Chart()
        chart.setTitle("Temperature")
        chart.legend().hide()
        chart.setAnimationOptions(QChart.AllAnimations)
        self.chart_view = QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.verticle_layout.addWidget(self.chart_view)

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

            self._timer.timeout.connect(self.handleTimeout)
            self._timer.setInterval(1000)

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