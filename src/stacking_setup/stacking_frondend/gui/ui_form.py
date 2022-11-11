# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1201, 918)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        
        font = QFont()
        font.setBold(True)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.mainFrame = QFrame(self.centralWidget)
        self.mainFrame.setObjectName(u"mainFrame")
        self.mainFrame.setFrameShape(QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_11 = QGridLayout(self.mainFrame)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        
        self.gridLayout_7.addWidget(self.maskLockMoveButton, 1, 1, 1, 1)


        self.gridLayout_14.addWidget(self.maskArrowFrame, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.maskControlFrame, 0, 1, 1, 1)


        self.gridLayout_11.addWidget(self.maskControlBox, 2, 0, 1, 1)

        self.temperatureControlBox = QGroupBox(self.mainFrame)
        self.temperatureControlBox.setObjectName(u"temperatureControlBox")
        sizePolicy.setHeightForWidth(self.temperatureControlBox.sizePolicy().hasHeightForWidth())
        self.temperatureControlBox.setSizePolicy(sizePolicy)
        self.temperatureControlBox.setCheckable(False)
        self.gridLayout_12 = QGridLayout(self.temperatureControlBox)
        self.gridLayout_12.setObjectName(u"gridLayout_12")

        self.gridLayout_11.addWidget(self.temperatureControlBox, 0, 2, 2, 1)

        self.baseControlBox = QGroupBox(self.mainFrame)
        self.baseControlBox.setObjectName(u"baseControlBox")
        sizePolicy.setHeightForWidth(self.baseControlBox.sizePolicy().hasHeightForWidth())
        self.baseControlBox.setSizePolicy(sizePolicy)
        self.baseControlBox.setMinimumSize(QSize(433, 390))
        self.baseControlBox.setMaximumSize(QSize(433, 390))
        self.gridLayout_3 = QGridLayout(self.baseControlBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.baseControlFrame = QFrame(self.baseControlBox)
        self.baseControlFrame.setObjectName(u"baseControlFrame")
        self.baseControlFrame.setMinimumSize(QSize(405, 370))
        self.baseControlFrame.setMaximumSize(QSize(405, 370))
        self.baseControlFrame.setFrameShape(QFrame.StyledPanel)
        self.baseControlFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_15 = QGridLayout(self.baseControlFrame)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.baseMoveModeFrame = QFrame(self.baseControlFrame)
        self.baseMoveModeFrame.setObjectName(u"baseMoveModeFrame")
        self.baseMoveModeFrame.setMaximumSize(QSize(88, 220))
        self.baseMoveModeFrame.setFrameShape(QFrame.StyledPanel)
        self.baseMoveModeFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.baseMoveModeFrame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.baseJogModeButton = QRadioButton(self.baseMoveModeFrame)
        self.baseJogModeButton.setObjectName(u"baseJogModeButton")
        self.baseJogModeButton.setChecked(False)

        self.verticalLayout_3.addWidget(self.baseJogModeButton)

        self.baseDriveModeButton = QRadioButton(self.baseMoveModeFrame)
        self.baseDriveModeButton.setObjectName(u"baseDriveModeButton")
        self.baseDriveModeButton.setChecked(True)

        self.verticalLayout_3.addWidget(self.baseDriveModeButton)


        self.gridLayout_15.addWidget(self.baseMoveModeFrame, 0, 0, 1, 1)

        self.baseMoveParamFrame = QFrame(self.baseControlFrame)
        self.baseMoveParamFrame.setObjectName(u"baseMoveParamFrame")
        self.baseMoveParamFrame.setMinimumSize(QSize(370, 0))
        self.baseMoveParamFrame.setMaximumSize(QSize(435, 112))
        self.baseMoveParamFrame.setFrameShape(QFrame.StyledPanel)
        self.baseMoveParamFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_9 = QGridLayout(self.baseMoveParamFrame)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.baseMovePresetLabel = QLabel(self.baseMoveParamFrame)
        self.baseMovePresetLabel.setObjectName(u"baseMovePresetLabel")

        self.gridLayout_9.addWidget(self.baseMovePresetLabel, 0, 0, 1, 1)

        self.baseVelSliderLabel = QLabel(self.baseMoveParamFrame)
        self.baseVelSliderLabel.setObjectName(u"baseVelSliderLabel")

        self.gridLayout_9.addWidget(self.baseVelSliderLabel, 1, 0, 1, 1)

        self.baseVelocitySlider = QSlider(self.baseMoveParamFrame)
        self.baseVelocitySlider.setObjectName(u"baseVelocitySlider")
        self.baseVelocitySlider.setOrientation(Qt.Horizontal)

        self.gridLayout_9.addWidget(self.baseVelocitySlider, 1, 1, 1, 1)

        self.baseVelDisp = QLCDNumber(self.baseMoveParamFrame)
        self.baseVelDisp.setObjectName(u"baseVelDisp")
        self.baseVelDisp.setFrameShape(QFrame.StyledPanel)
        self.baseVelDisp.setDigitCount(3)
        self.baseVelDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_9.addWidget(self.baseVelDisp, 1, 2, 1, 1)

        self.baseVelDispLable = QLabel(self.baseMoveParamFrame)
        self.baseVelDispLable.setObjectName(u"baseVelDispLable")

        self.gridLayout_9.addWidget(self.baseVelDispLable, 1, 3, 1, 1)

        self.baseAccSliderLabel = QLabel(self.baseMoveParamFrame)
        self.baseAccSliderLabel.setObjectName(u"baseAccSliderLabel")

        self.gridLayout_9.addWidget(self.baseAccSliderLabel, 2, 0, 1, 1)

        self.baseAccSlider = QSlider(self.baseMoveParamFrame)
        self.baseAccSlider.setObjectName(u"baseAccSlider")
        self.baseAccSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_9.addWidget(self.baseAccSlider, 2, 1, 1, 1)

        self.baseAccDisp = QLCDNumber(self.baseMoveParamFrame)
        self.baseAccDisp.setObjectName(u"baseAccDisp")
        self.baseAccDisp.setFrameShape(QFrame.StyledPanel)
        self.baseAccDisp.setDigitCount(3)
        self.baseAccDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_9.addWidget(self.baseAccDisp, 2, 2, 1, 1)

        self.baseAccDispLabel = QLabel(self.baseMoveParamFrame)
        self.baseAccDispLabel.setObjectName(u"baseAccDispLabel")

        self.gridLayout_9.addWidget(self.baseAccDispLabel, 2, 3, 1, 1)

        self.baseMovePresetCombo = QComboBox(self.baseMoveParamFrame)
        self.baseMovePresetCombo.addItem("")
        self.baseMovePresetCombo.addItem("")
        self.baseMovePresetCombo.addItem("")
        self.baseMovePresetCombo.setObjectName(u"baseMovePresetCombo")

        self.gridLayout_9.addWidget(self.baseMovePresetCombo, 0, 1, 1, 3)


        self.gridLayout_15.addWidget(self.baseMoveParamFrame, 3, 0, 1, 3)

        self.baseControlDiv = QFrame(self.baseControlFrame)
        self.baseControlDiv.setObjectName(u"baseControlDiv")
        self.baseControlDiv.setFrameShape(QFrame.HLine)
        self.baseControlDiv.setFrameShadow(QFrame.Sunken)

        self.gridLayout_15.addWidget(self.baseControlDiv, 1, 0, 1, 3)

        self.baseArrowFrame = QFrame(self.baseControlFrame)
        self.baseArrowFrame.setObjectName(u"baseArrowFrame")
        self.baseArrowFrame.setMinimumSize(QSize(220, 220))
        self.baseArrowFrame.setMaximumSize(QSize(220, 220))
        self.baseArrowFrame.setFrameShape(QFrame.StyledPanel)
        self.baseArrowFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_8 = QGridLayout(self.baseArrowFrame)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.baseMoveRight = QPushButton(self.baseArrowFrame)
        self.baseMoveRight.setObjectName(u"baseMoveRight")
        self.baseMoveRight.setMinimumSize(QSize(60, 60))
        self.baseMoveRight.setMaximumSize(QSize(60, 60))
        self.baseMoveRight.setStyleSheet(u"image: url(:/icons/arrows/arrow-right-solid.svg);")

        self.gridLayout_8.addWidget(self.baseMoveRight, 1, 6, 1, 1)

        self.baseMoveLeft = QPushButton(self.baseArrowFrame)
        self.baseMoveLeft.setObjectName(u"baseMoveLeft")
        self.baseMoveLeft.setMinimumSize(QSize(60, 60))
        self.baseMoveLeft.setMaximumSize(QSize(60, 60))
        self.baseMoveLeft.setStyleSheet(u"image: url(:/icons/arrows/arrow-left-solid.svg);")

        self.gridLayout_8.addWidget(self.baseMoveLeft, 1, 2, 1, 1)

        self.baseMoveDown = QPushButton(self.baseArrowFrame)
        self.baseMoveDown.setObjectName(u"baseMoveDown")
        self.baseMoveDown.setMinimumSize(QSize(60, 60))
        self.baseMoveDown.setMaximumSize(QSize(60, 60))
        self.baseMoveDown.setStyleSheet(u"image: url(:/icons/arrows/arrow-down-solid.svg);")

        self.gridLayout_8.addWidget(self.baseMoveDown, 2, 4, 1, 1)

        self.baseMoveUp = QPushButton(self.baseArrowFrame)
        self.baseMoveUp.setObjectName(u"baseMoveUp")
        self.baseMoveUp.setMinimumSize(QSize(60, 60))
        self.baseMoveUp.setMaximumSize(QSize(60, 60))
        self.baseMoveUp.setStyleSheet(u"image: url(:/icons/arrows/arrow-up-solid.svg);")

        self.gridLayout_8.addWidget(self.baseMoveUp, 0, 4, 1, 1)

        self.baseLockMoveButton = QPushButton(self.baseArrowFrame)
        self.baseLockMoveButton.setObjectName(u"baseLockMoveButton")
        self.baseLockMoveButton.setMinimumSize(QSize(60, 60))
        self.baseLockMoveButton.setMaximumSize(QSize(60, 60))
        self.baseLockMoveButton.setStyleSheet(u"image: url(:/icons/arrows/icons/arrows/arrow-down-up-lock-solid.svg);")
        self.baseLockMoveButton.setCheckable(True)

        self.gridLayout_8.addWidget(self.baseLockMoveButton, 1, 4, 1, 1)


        self.gridLayout_15.addWidget(self.baseArrowFrame, 0, 1, 1, 1)


        self.gridLayout_3.addWidget(self.baseControlFrame, 0, 0, 1, 1)


        self.gridLayout_11.addWidget(self.baseControlBox, 0, 0, 2, 1)

        self.systemStateBox = QGroupBox(self.mainFrame)
        self.systemStateBox.setObjectName(u"systemStateBox")
        sizePolicy.setHeightForWidth(self.systemStateBox.sizePolicy().hasHeightForWidth())
        self.systemStateBox.setSizePolicy(sizePolicy)
        self.systemStateBox.setMinimumSize(QSize(340, 390))
        self.systemStateBox.setMaximumSize(QSize(340, 390))
        self.gridLayout_4 = QGridLayout(self.systemStateBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.systemStateFrame = QFrame(self.systemStateBox)
        self.systemStateFrame.setObjectName(u"systemStateFrame")
        self.systemStateFrame.setMinimumSize(QSize(0, 320))
        self.systemStateFrame.setMaximumSize(QSize(16777215, 320))
        self.systemStateFrame.setFrameShape(QFrame.StyledPanel)
        self.systemStateFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.systemStateFrame)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.maskXPosDispLabel = QLabel(self.systemStateFrame)
        self.maskXPosDispLabel.setObjectName(u"maskXPosDispLabel")

        self.gridLayout_5.addWidget(self.maskXPosDispLabel, 3, 0, 1, 1)

        self.baseYPosDispLabel = QLabel(self.systemStateFrame)
        self.baseYPosDispLabel.setObjectName(u"baseYPosDispLabel")

        self.gridLayout_5.addWidget(self.baseYPosDispLabel, 8, 0, 1, 1)

        self.maskZPosDisp = QLCDNumber(self.systemStateFrame)
        self.maskZPosDisp.setObjectName(u"maskZPosDisp")
        self.maskZPosDisp.setMaximumSize(QSize(75, 35))
        self.maskZPosDisp.setFrameShape(QFrame.StyledPanel)
        self.maskZPosDisp.setSmallDecimalPoint(True)
        self.maskZPosDisp.setDigitCount(7)
        self.maskZPosDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.maskZPosDisp, 5, 1, 1, 1)

        self.baseXPosDisp = QLCDNumber(self.systemStateFrame)
        self.baseXPosDisp.setObjectName(u"baseXPosDisp")
        sizePolicy.setHeightForWidth(self.baseXPosDisp.sizePolicy().hasHeightForWidth())
        self.baseXPosDisp.setSizePolicy(sizePolicy)
        self.baseXPosDisp.setMinimumSize(QSize(30, 30))
        self.baseXPosDisp.setMaximumSize(QSize(75, 35))
        self.baseXPosDisp.setFrameShape(QFrame.StyledPanel)
        self.baseXPosDisp.setSmallDecimalPoint(True)
        self.baseXPosDisp.setDigitCount(7)
        self.baseXPosDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.baseXPosDisp, 7, 1, 1, 1)

        self.sampleTempDisp = QLCDNumber(self.systemStateFrame)
        self.sampleTempDisp.setObjectName(u"sampleTempDisp")
        self.sampleTempDisp.setMinimumSize(QSize(75, 35))
        self.sampleTempDisp.setMaximumSize(QSize(75, 35))
        self.sampleTempDisp.setFrameShape(QFrame.StyledPanel)
        self.sampleTempDisp.setSmallDecimalPoint(True)
        self.sampleTempDisp.setDigitCount(7)
        self.sampleTempDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.sampleTempDisp, 0, 1, 1, 1)

        self.maskYPosDispLabel = QLabel(self.systemStateFrame)
        self.maskYPosDispLabel.setObjectName(u"maskYPosDispLabel")

        self.gridLayout_5.addWidget(self.maskYPosDispLabel, 4, 0, 1, 1)

        self.samplePosDispLabel = QLabel(self.systemStateFrame)
        self.samplePosDispLabel.setObjectName(u"samplePosDispLabel")

        self.gridLayout_5.addWidget(self.samplePosDispLabel, 1, 0, 1, 1)

        self.samplePosDisp = QLCDNumber(self.systemStateFrame)
        self.samplePosDisp.setObjectName(u"samplePosDisp")
        self.samplePosDisp.setMinimumSize(QSize(75, 35))
        self.samplePosDisp.setMaximumSize(QSize(75, 35))
        self.samplePosDisp.setFrameShape(QFrame.StyledPanel)
        self.samplePosDisp.setSmallDecimalPoint(True)
        self.samplePosDisp.setDigitCount(7)
        self.samplePosDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.samplePosDisp, 1, 1, 1, 1)

        self.sampleTempDispLabel = QLabel(self.systemStateFrame)
        self.sampleTempDispLabel.setObjectName(u"sampleTempDispLabel")

        self.gridLayout_5.addWidget(self.sampleTempDispLabel, 0, 0, 1, 1)

        self.maskXPosDisp = QLCDNumber(self.systemStateFrame)
        self.maskXPosDisp.setObjectName(u"maskXPosDisp")
        self.maskXPosDisp.setMaximumSize(QSize(75, 35))
        self.maskXPosDisp.setFrameShape(QFrame.StyledPanel)
        self.maskXPosDisp.setFrameShadow(QFrame.Raised)
        self.maskXPosDisp.setSmallDecimalPoint(True)
        self.maskXPosDisp.setDigitCount(7)
        self.maskXPosDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.maskXPosDisp, 3, 1, 1, 1)

        self.baseYPosDisp = QLCDNumber(self.systemStateFrame)
        self.baseYPosDisp.setObjectName(u"baseYPosDisp")
        self.baseYPosDisp.setMaximumSize(QSize(75, 35))
        self.baseYPosDisp.setFrameShape(QFrame.StyledPanel)
        self.baseYPosDisp.setSmallDecimalPoint(True)
        self.baseYPosDisp.setDigitCount(7)
        self.baseYPosDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.baseYPosDisp, 8, 1, 1, 1)

        self.maskZPosDispLabel = QLabel(self.systemStateFrame)
        self.maskZPosDispLabel.setObjectName(u"maskZPosDispLabel")

        self.gridLayout_5.addWidget(self.maskZPosDispLabel, 5, 0, 1, 1)

        self.baseXPosDispLabel = QLabel(self.systemStateFrame)
        self.baseXPosDispLabel.setObjectName(u"baseXPosDispLabel")

        self.gridLayout_5.addWidget(self.baseXPosDispLabel, 7, 0, 1, 1)

        self.maskYPosDisp = QLCDNumber(self.systemStateFrame)
        self.maskYPosDisp.setObjectName(u"maskYPosDisp")
        self.maskYPosDisp.setMaximumSize(QSize(75, 35))
        self.maskYPosDisp.setFrameShape(QFrame.StyledPanel)
        self.maskYPosDisp.setSmallDecimalPoint(True)
        self.maskYPosDisp.setDigitCount(7)
        self.maskYPosDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_5.addWidget(self.maskYPosDisp, 4, 1, 1, 1)

        self.label = QLabel(self.systemStateFrame)
        self.label.setObjectName(u"label")

        self.gridLayout_5.addWidget(self.label, 0, 2, 1, 1)

        self.label_2 = QLabel(self.systemStateFrame)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_5.addWidget(self.label_2, 1, 2, 1, 1)

        self.label_3 = QLabel(self.systemStateFrame)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_5.addWidget(self.label_3, 3, 2, 1, 1)

        self.label_4 = QLabel(self.systemStateFrame)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_5.addWidget(self.label_4, 4, 2, 1, 1)

        self.label_5 = QLabel(self.systemStateFrame)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_5.addWidget(self.label_5, 5, 2, 1, 1)

        self.label_6 = QLabel(self.systemStateFrame)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_5.addWidget(self.label_6, 7, 2, 1, 1)

        self.label_7 = QLabel(self.systemStateFrame)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_5.addWidget(self.label_7, 8, 2, 1, 1)

        self.maskDiv = QFrame(self.systemStateFrame)
        self.maskDiv.setObjectName(u"maskDiv")
        self.maskDiv.setFrameShape(QFrame.HLine)
        self.maskDiv.setFrameShadow(QFrame.Sunken)

        self.gridLayout_5.addWidget(self.maskDiv, 6, 0, 1, 3)

        self.rotationDiv = QFrame(self.systemStateFrame)
        self.rotationDiv.setObjectName(u"rotationDiv")
        self.rotationDiv.setFrameShape(QFrame.HLine)
        self.rotationDiv.setFrameShadow(QFrame.Sunken)

        self.gridLayout_5.addWidget(self.rotationDiv, 2, 0, 1, 3)


        self.gridLayout_4.addWidget(self.systemStateFrame, 0, 0, 1, 2)


        self.gridLayout_11.addWidget(self.systemStateBox, 2, 1, 1, 1)

        self.systemMessagesBox = QGroupBox(self.mainFrame)
        self.systemMessagesBox.setObjectName(u"systemMessagesBox")
        sizePolicy.setHeightForWidth(self.systemMessagesBox.sizePolicy().hasHeightForWidth())
        self.systemMessagesBox.setSizePolicy(sizePolicy)
        self.systemMessagesBox.setMaximumSize(QSize(16777215, 433))
        self.verticalLayout = QVBoxLayout(self.systemMessagesBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollAreaFrame = QScrollArea(self.systemMessagesBox)
        self.scrollAreaFrame.setObjectName(u"scrollAreaFrame")
        self.scrollAreaFrame.setMinimumSize(QSize(340, 0))
        self.scrollAreaFrame.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 338, 337))
        self.scrollAreaFrame.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollAreaFrame)


        self.gridLayout_11.addWidget(self.systemMessagesBox, 2, 2, 1, 1)

        self.sampleControlBox = QGroupBox(self.mainFrame)
        self.sampleControlBox.setObjectName(u"sampleControlBox")
        sizePolicy.setHeightForWidth(self.sampleControlBox.sizePolicy().hasHeightForWidth())
        self.sampleControlBox.setSizePolicy(sizePolicy)
        self.sampleControlBox.setMinimumSize(QSize(340, 0))
        self.sampleControlBox.setMaximumSize(QSize(340, 390))
        self.gridLayout_6 = QGridLayout(self.sampleControlBox)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.sampleControlFrame = QFrame(self.sampleControlBox)
        self.sampleControlFrame.setObjectName(u"sampleControlFrame")
        sizePolicy.setHeightForWidth(self.sampleControlFrame.sizePolicy().hasHeightForWidth())
        self.sampleControlFrame.setSizePolicy(sizePolicy)
        self.sampleControlFrame.setMinimumSize(QSize(320, 265))
        self.sampleControlFrame.setMaximumSize(QSize(320, 265))
        self.sampleControlFrame.setFrameShape(QFrame.StyledPanel)
        self.sampleControlFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_13 = QGridLayout(self.sampleControlFrame)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.vacuumPumpButton = QRadioButton(self.sampleControlFrame)
        self.vacuumPumpButton.setObjectName(u"vacuumPumpButton")

        self.gridLayout_13.addWidget(self.vacuumPumpButton, 0, 0, 1, 2)

        self.sampleVacuumDiv = QFrame(self.sampleControlFrame)
        self.sampleVacuumDiv.setObjectName(u"sampleVacuumDiv")
        self.sampleVacuumDiv.setFrameShape(QFrame.HLine)
        self.sampleVacuumDiv.setFrameShadow(QFrame.Sunken)

        self.gridLayout_13.addWidget(self.sampleVacuumDiv, 1, 0, 1, 4)

        self.sampleJogModeButton = QRadioButton(self.sampleControlFrame)
        self.buttonGroup = QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.sampleJogModeButton)
        self.sampleJogModeButton.setObjectName(u"sampleJogModeButton")

        self.gridLayout_13.addWidget(self.sampleJogModeButton, 2, 0, 1, 1)

        self.sampleDriveModeButton = QRadioButton(self.sampleControlFrame)
        self.buttonGroup.addButton(self.sampleDriveModeButton)
        self.sampleDriveModeButton.setObjectName(u"sampleDriveModeButton")
        self.sampleDriveModeButton.setChecked(True)

        self.gridLayout_13.addWidget(self.sampleDriveModeButton, 2, 1, 1, 1)

        self.sampleRotateLeft = QPushButton(self.sampleControlFrame)
        self.sampleRotateLeft.setObjectName(u"sampleRotateLeft")
        self.sampleRotateLeft.setMinimumSize(QSize(60, 60))
        self.sampleRotateLeft.setMaximumSize(QSize(60, 60))

        self.gridLayout_13.addWidget(self.sampleRotateLeft, 3, 0, 1, 1)

        self.sampleMoveParamsDiv = QFrame(self.sampleControlFrame)
        self.sampleMoveParamsDiv.setObjectName(u"sampleMoveParamsDiv")
        self.sampleMoveParamsDiv.setFrameShape(QFrame.HLine)
        self.sampleMoveParamsDiv.setFrameShadow(QFrame.Sunken)

        self.gridLayout_13.addWidget(self.sampleMoveParamsDiv, 4, 0, 1, 4)

        self.samplePresetComboLabel = QLabel(self.sampleControlFrame)
        self.samplePresetComboLabel.setObjectName(u"samplePresetComboLabel")

        self.gridLayout_13.addWidget(self.samplePresetComboLabel, 5, 0, 1, 1)

        self.sampleMovePresetCombo = QComboBox(self.sampleControlFrame)
        self.sampleMovePresetCombo.addItem("")
        self.sampleMovePresetCombo.addItem("")
        self.sampleMovePresetCombo.addItem("")
        self.sampleMovePresetCombo.addItem("")
        self.sampleMovePresetCombo.setObjectName(u"sampleMovePresetCombo")

        self.gridLayout_13.addWidget(self.sampleMovePresetCombo, 5, 1, 1, 3)

        self.sampleVelSliderLabel = QLabel(self.sampleControlFrame)
        self.sampleVelSliderLabel.setObjectName(u"sampleVelSliderLabel")

        self.gridLayout_13.addWidget(self.sampleVelSliderLabel, 6, 0, 1, 1)

        self.sampleVelSlider = QSlider(self.sampleControlFrame)
        self.sampleVelSlider.setObjectName(u"sampleVelSlider")
        self.sampleVelSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_13.addWidget(self.sampleVelSlider, 6, 1, 1, 1)

        self.sampleVelDisp = QLCDNumber(self.sampleControlFrame)
        self.sampleVelDisp.setObjectName(u"sampleVelDisp")
        self.sampleVelDisp.setFrameShape(QFrame.StyledPanel)
        self.sampleVelDisp.setDigitCount(3)
        self.sampleVelDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_13.addWidget(self.sampleVelDisp, 6, 2, 1, 1)

        self.sampleVelDispLabel = QLabel(self.sampleControlFrame)
        self.sampleVelDispLabel.setObjectName(u"sampleVelDispLabel")

        self.gridLayout_13.addWidget(self.sampleVelDispLabel, 6, 3, 1, 1)

        self.sampleAccSliderLabel = QLabel(self.sampleControlFrame)
        self.sampleAccSliderLabel.setObjectName(u"sampleAccSliderLabel")

        self.gridLayout_13.addWidget(self.sampleAccSliderLabel, 7, 0, 1, 1)

        self.sampleAccSlider = QSlider(self.sampleControlFrame)
        self.sampleAccSlider.setObjectName(u"sampleAccSlider")
        self.sampleAccSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_13.addWidget(self.sampleAccSlider, 7, 1, 1, 1)

        self.sampleAccDisp = QLCDNumber(self.sampleControlFrame)
        self.sampleAccDisp.setObjectName(u"sampleAccDisp")
        self.sampleAccDisp.setFrameShape(QFrame.StyledPanel)
        self.sampleAccDisp.setDigitCount(3)
        self.sampleAccDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_13.addWidget(self.sampleAccDisp, 7, 2, 1, 1)

        self.sampleAccDispLabel = QLabel(self.sampleControlFrame)
        self.sampleAccDispLabel.setObjectName(u"sampleAccDispLabel")

        self.gridLayout_13.addWidget(self.sampleAccDispLabel, 7, 3, 1, 1)

        self.sampleRotateRight = QPushButton(self.sampleControlFrame)
        self.sampleRotateRight.setObjectName(u"sampleRotateRight")
        self.sampleRotateRight.setMinimumSize(QSize(60, 60))
        self.sampleRotateRight.setMaximumSize(QSize(60, 60))

        self.gridLayout_13.addWidget(self.sampleRotateRight, 3, 1, 1, 1)

        self.sampleRotateLockButton = QPushButton(self.sampleControlFrame)
        self.sampleRotateLockButton.setObjectName(u"sampleRotateLockButton")
        self.sampleRotateLockButton.setMinimumSize(QSize(60, 60))
        self.sampleRotateLockButton.setMaximumSize(QSize(60, 60))
        self.sampleRotateLockButton.setCheckable(True)

        self.gridLayout_13.addWidget(self.sampleRotateLockButton, 3, 2, 1, 2)


        self.gridLayout_6.addWidget(self.sampleControlFrame, 0, 0, 1, 1)


        self.gridLayout_11.addWidget(self.sampleControlBox, 0, 1, 2, 1)


        self.gridLayout.addWidget(self.mainFrame, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralWidget)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy1)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1201, 25))
        self.menuConfiguration = QMenu(self.menubar)
        self.menuConfiguration.setObjectName(u"menuConfiguration")
        self.menuStandard_configs = QMenu(self.menuConfiguration)
        self.menuStandard_configs.setObjectName(u"menuStandard_configs")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menubar)

        self.toolBar.addAction(self.actionEmergency_stop)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSave_config)
        self.toolBar.addSeparator()
        self.menubar.addAction(self.menuConfiguration.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menuConfiguration.addAction(self.menuStandard_configs.menuAction())
        self.menuConfiguration.addAction(self.actionCustom_config)
        self.menuConfiguration.addAction(self.actionSave_config)
        self.menuStandard_configs.addAction(self.actionDefault)
        self.menuStandard_configs.addAction(self.actionScanning)
        self.menuView.addAction(self.actionBase_control)
        self.menuView.addAction(self.actionMas_control)
        self.menuView.addAction(self.actionSample_control)
        self.menuView.addAction(self.actionControl_mode)
        self.menuView.addAction(self.actionSystem_state)
        self.menuView.addAction(self.actionTemperature_control)
        self.menuView.addAction(self.actionSystem_messages)

        self.retranslateUi(MainWindow)
        self.actionBase_control.toggled.connect(self.baseControlBox.setVisible)
        self.actionMas_control.toggled.connect(self.maskControlBox.setVisible)
        self.actionSample_control.toggled.connect(self.sampleControlBox.setVisible)
        self.actionSystem_messages.toggled.connect(self.systemMessagesBox.setVisible)
        self.actionSystem_state.toggled.connect(self.systemStateBox.setVisible)
        self.actionTemperature_control.toggled.connect(self.temperatureControlBox.setVisible)
        self.actionJoystick.triggered.connect(self.actionKeyboard.toggle)
        self.baseLockMoveButton.toggled.connect(self.baseMoveLeft.setDisabled)
        self.baseLockMoveButton.toggled.connect(self.baseMoveDown.setDisabled)
        self.baseLockMoveButton.toggled.connect(self.baseMoveRight.setDisabled)
        self.baseLockMoveButton.toggled.connect(self.baseMoveUp.setDisabled)
        self.maskLockMoveButton.toggled.connect(self.maskMoveDown.setDisabled)
        self.maskLockMoveButton.toggled.connect(self.maskMoveLeft.setDisabled)
        self.maskLockMoveButton.toggled.connect(self.maskMoveUp.setDisabled)
        self.maskLockMoveButton.toggled.connect(self.maskMoveRight.setDisabled)
        self.actionJoystick.triggered.connect(self.actionController.toggle)
        self.actionEmergency_stop.triggered.connect(self.baseLockMoveButton.toggle)
        self.sampleRotateLockButton.toggled.connect(self.sampleRotateRight.setDisabled)
        self.sampleRotateLockButton.toggled.connect(self.sampleRotateLeft.setDisabled)
        self.actionEmergency_stop.triggered.connect(self.maskLockMoveButton.toggle)
        self.actionEmergency_stop.triggered.connect(self.sampleRotateLockButton.toggle)
        self.maskAccSlider.sliderMoved.connect(self.maskAccDisp.display)
        self.maskVelSlider.sliderMoved.connect(self.maskVelDisp.display)
        self.baseAccSlider.sliderMoved.connect(self.baseAccDisp.display)
        self.baseVelocitySlider.sliderMoved.connect(self.baseVelDisp.display)
        self.sampleAccSlider.sliderMoved.connect(self.sampleAccDisp.display)
        self.sampleVelSlider.sliderMoved.connect(self.sampleVelDisp.display)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionDefault.setText(QCoreApplication.translate("MainWindow", u"Default", None))
        self.actionCustom_config.setText(QCoreApplication.translate("MainWindow", u"Custom config", None))
        self.actionSave_config.setText(QCoreApplication.translate("MainWindow", u"Save current config", None))
        self.actionScanning.setText(QCoreApplication.translate("MainWindow", u"Scanning", None))
        self.actionBase_control.setText(QCoreApplication.translate("MainWindow", u"Base  control", None))
        self.actionMas_control.setText(QCoreApplication.translate("MainWindow", u"Mask control", None))
        self.actionSample_control.setText(QCoreApplication.translate("MainWindow", u"Sample control", None))
        self.actionControl_mode.setText(QCoreApplication.translate("MainWindow", u"Control mode", None))
        self.actionSystem_state.setText(QCoreApplication.translate("MainWindow", u"System state", None))
        self.actionTemperature_control.setText(QCoreApplication.translate("MainWindow", u"Temperature control", None))
        self.actionSystem_messages.setText(QCoreApplication.translate("MainWindow", u"System messages", None))
        self.actionEmergency_stop.setText(QCoreApplication.translate("MainWindow", u"Emergency stop", None))
#if QT_CONFIG(shortcut)
        self.actionEmergency_stop.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionJoystick.setText(QCoreApplication.translate("MainWindow", u"Joystick", None))
        self.actionController.setText(QCoreApplication.translate("MainWindow", u"Controller", None))
        self.actionUser_interface.setText(QCoreApplication.translate("MainWindow", u"User interface", None))
        self.actionKeyboard.setText(QCoreApplication.translate("MainWindow", u"Keyboard", None))
        self.maskControlBox.setTitle(QCoreApplication.translate("MainWindow", u"Mask control", None))
        self.maskJogModeButton.setText(QCoreApplication.translate("MainWindow", u"Jog", None))
        self.maskDriveModeButton.setText(QCoreApplication.translate("MainWindow", u"Drive", None))
        self.maskMovePresetLabel.setText(QCoreApplication.translate("MainWindow", u"Presets :", None))
        self.maskVelSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Velocity :", None))
        self.maskVelDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s", None))
        self.maskAccSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Acceleration :", None))
        self.maskAccDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s^2", None))
        self.maskMovePresetCombo.setItemText(0, QCoreApplication.translate("MainWindow", u"500 nm/s", None))
        self.maskMovePresetCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"1 um/s", None))
        self.maskMovePresetCombo.setItemText(2, QCoreApplication.translate("MainWindow", u"5 um/s", None))
        self.maskMovePresetCombo.setItemText(3, QCoreApplication.translate("MainWindow", u"40 um/s", None))

        self.maskMoveLeft.setText("")
        self.maskMoveRight.setText("")
        self.maskMoveDown.setText("")
        self.maskMoveUp.setText("")
        self.maskLockMoveButton.setText("")
        self.temperatureControlBox.setTitle(QCoreApplication.translate("MainWindow", u"Temperature control", None))
        self.baseControlBox.setTitle(QCoreApplication.translate("MainWindow", u"Base control", None))
        self.baseJogModeButton.setText(QCoreApplication.translate("MainWindow", u"Jog", None))
        self.baseDriveModeButton.setText(QCoreApplication.translate("MainWindow", u"Drive", None))
        self.baseMovePresetLabel.setText(QCoreApplication.translate("MainWindow", u"Presets :", None))
        self.baseVelSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Velocity :", None))
        self.baseVelDispLable.setText(QCoreApplication.translate("MainWindow", u"um/s", None))
        self.baseAccSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Acceleration :", None))
        self.baseAccDispLabel.setText(QCoreApplication.translate("MainWindow", u"um/s^2", None))
        self.baseMovePresetCombo.setItemText(0, QCoreApplication.translate("MainWindow", u"50 um/s", None))
        self.baseMovePresetCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"0.5 mm/s", None))
        self.baseMovePresetCombo.setItemText(2, QCoreApplication.translate("MainWindow", u"1 mm/s", None))

        self.baseMoveRight.setText("")
        self.baseMoveLeft.setText("")
        self.baseMoveDown.setText("")
        self.baseMoveUp.setText("")
        self.baseLockMoveButton.setText("")
        self.systemStateBox.setTitle(QCoreApplication.translate("MainWindow", u"System state", None))
        self.maskXPosDispLabel.setText(QCoreApplication.translate("MainWindow", u"Mask x :", None))
        self.baseYPosDispLabel.setText(QCoreApplication.translate("MainWindow", u"Base y :", None))
        self.maskYPosDispLabel.setText(QCoreApplication.translate("MainWindow", u"Mask y :", None))
        self.samplePosDispLabel.setText(QCoreApplication.translate("MainWindow", u"Rotation :", None))
        self.sampleTempDispLabel.setText(QCoreApplication.translate("MainWindow", u"Sample Temp :", None))
        self.maskZPosDispLabel.setText(QCoreApplication.translate("MainWindow", u"Mask z :", None))
        self.baseXPosDispLabel.setText(QCoreApplication.translate("MainWindow", u"Base x :", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.systemMessagesBox.setTitle(QCoreApplication.translate("MainWindow", u"System messages", None))
        self.sampleControlBox.setTitle(QCoreApplication.translate("MainWindow", u"Sample holder control", None))
        self.vacuumPumpButton.setText(QCoreApplication.translate("MainWindow", u"Vacuup pump on/off", None))
        self.sampleJogModeButton.setText(QCoreApplication.translate("MainWindow", u"Jog", None))
        self.sampleDriveModeButton.setText(QCoreApplication.translate("MainWindow", u"Drive", None))
        self.sampleRotateLeft.setText("")
        self.samplePresetComboLabel.setText(QCoreApplication.translate("MainWindow", u"Presets :", None))
        self.sampleMovePresetCombo.setItemText(0, QCoreApplication.translate("MainWindow", u"1 mrad/s", None))
        self.sampleMovePresetCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"10 mrad/s", None))
        self.sampleMovePresetCombo.setItemText(2, QCoreApplication.translate("MainWindow", u"100 mrad/s", None))
        self.sampleMovePresetCombo.setItemText(3, QCoreApplication.translate("MainWindow", u"250 mrad/s", None))

        self.sampleVelSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Velocity :", None))
        self.sampleVelDispLabel.setText(QCoreApplication.translate("MainWindow", u"ur/s", None))
        self.sampleAccSliderLabel.setText(QCoreApplication.translate("MainWindow", u"Acceleration :", None))
        self.sampleAccDispLabel.setText(QCoreApplication.translate("MainWindow", u"ur/s^2", None))
        self.sampleRotateRight.setText("")
        self.sampleRotateLockButton.setText("")
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
        self.menuConfiguration.setTitle(QCoreApplication.translate("MainWindow", u"Configuration", None))
        self.menuStandard_configs.setTitle(QCoreApplication.translate("MainWindow", u"Standard configs", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
    # retranslateUi

