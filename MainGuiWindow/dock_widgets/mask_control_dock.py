from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class MaskControlDockWidget(QDockWidget):
    name = 'MaskControl'

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.maskControlBox = QGroupBox(self)
        self.maskControlBox.setObjectName(u"maskControlBox")
        sizePolicy.setHeightForWidth(self.maskControlBox.sizePolicy().hasHeightForWidth())
        self.maskControlBox.setSizePolicy(sizePolicy)
        self.maskControlBox.setMinimumSize(QSize(433, 390))
        self.maskControlBox.setMaximumSize(QSize(433, 390))
        self.gridLayout_2 = QGridLayout(self.maskControlBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.maskControlFrame = QFrame(self.maskControlBox)
        self.maskControlFrame.setObjectName(u"maskControlFrame")
        self.maskControlFrame.setMinimumSize(QSize(405, 370))
        self.maskControlFrame.setMaximumSize(QSize(405, 370))
        self.maskControlFrame.setFrameShape(QFrame.StyledPanel)
        self.maskControlFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_14 = QGridLayout(self.maskControlFrame)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.maskMoveModeFrame = QFrame(self.maskControlFrame)
        self.maskMoveModeFrame.setObjectName(u"maskMoveModeFrame")
        self.maskMoveModeFrame.setMaximumSize(QSize(88, 220))
        self.maskMoveModeFrame.setFrameShape(QFrame.StyledPanel)
        self.maskMoveModeFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.maskMoveModeFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.maskJogModeButton = QRadioButton(self.maskMoveModeFrame)
        self.maskJogModeButton.setObjectName(u"maskJogModeButton")

        self.verticalLayout_2.addWidget(self.maskJogModeButton)

        self.maskDriveModeButton = QRadioButton(self.maskMoveModeFrame)
        self.maskDriveModeButton.setObjectName(u"maskDriveModeButton")
        self.maskDriveModeButton.setChecked(True)

        self.verticalLayout_2.addWidget(self.maskDriveModeButton)


        self.gridLayout_14.addWidget(self.maskMoveModeFrame, 0, 0, 1, 1)

        self.maskMoveParamFrame = QFrame(self.maskControlFrame)
        self.maskMoveParamFrame.setObjectName(u"maskMoveParamFrame")
        self.maskMoveParamFrame.setMinimumSize(QSize(370, 0))
        self.maskMoveParamFrame.setMaximumSize(QSize(435, 112))
        self.maskMoveParamFrame.setFrameShape(QFrame.StyledPanel)
        self.maskMoveParamFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_10 = QGridLayout(self.maskMoveParamFrame)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.maskMovePresetLabel = QLabel(self.maskMoveParamFrame)
        self.maskMovePresetLabel.setObjectName(u"maskMovePresetLabel")

        self.gridLayout_10.addWidget(self.maskMovePresetLabel, 0, 0, 1, 1)

        self.maskVelSliderLabel = QLabel(self.maskMoveParamFrame)
        self.maskVelSliderLabel.setObjectName(u"maskVelSliderLabel")

        self.gridLayout_10.addWidget(self.maskVelSliderLabel, 1, 0, 1, 1)

        self.maskVelSlider = QSlider(self.maskMoveParamFrame)
        self.maskVelSlider.setObjectName(u"maskVelSlider")
        self.maskVelSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_10.addWidget(self.maskVelSlider, 1, 1, 1, 1)

        self.maskVelDisp = QLCDNumber(self.maskMoveParamFrame)
        self.maskVelDisp.setObjectName(u"maskVelDisp")
        self.maskVelDisp.setFrameShape(QFrame.StyledPanel)
        self.maskVelDisp.setDigitCount(3)
        self.maskVelDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_10.addWidget(self.maskVelDisp, 1, 2, 1, 1)

        self.maskVelDispLabel = QLabel(self.maskMoveParamFrame)
        self.maskVelDispLabel.setObjectName(u"maskVelDispLabel")

        self.gridLayout_10.addWidget(self.maskVelDispLabel, 1, 3, 1, 1)

        self.maskAccSliderLabel = QLabel(self.maskMoveParamFrame)
        self.maskAccSliderLabel.setObjectName(u"maskAccSliderLabel")

        self.gridLayout_10.addWidget(self.maskAccSliderLabel, 2, 0, 1, 1)

        self.maskAccSlider = QSlider(self.maskMoveParamFrame)
        self.maskAccSlider.setObjectName(u"maskAccSlider")
        self.maskAccSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_10.addWidget(self.maskAccSlider, 2, 1, 1, 1)

        self.maskAccDisp = QLCDNumber(self.maskMoveParamFrame)
        self.maskAccDisp.setObjectName(u"maskAccDisp")
        self.maskAccDisp.setFrameShape(QFrame.StyledPanel)
        self.maskAccDisp.setDigitCount(3)
        self.maskAccDisp.setSegmentStyle(QLCDNumber.Flat)

        self.gridLayout_10.addWidget(self.maskAccDisp, 2, 2, 1, 1)

        self.maskAccDispLabel = QLabel(self.maskMoveParamFrame)
        self.maskAccDispLabel.setObjectName(u"maskAccDispLabel")

        self.gridLayout_10.addWidget(self.maskAccDispLabel, 2, 3, 1, 1)

        self.maskMovePresetCombo = QComboBox(self.maskMoveParamFrame)
        self.maskMovePresetCombo.addItem("")
        self.maskMovePresetCombo.addItem("")
        self.maskMovePresetCombo.addItem("")
        self.maskMovePresetCombo.addItem("")
        self.maskMovePresetCombo.setObjectName(u"maskMovePresetCombo")

        self.gridLayout_10.addWidget(self.maskMovePresetCombo, 0, 1, 1, 3)


        self.gridLayout_14.addWidget(self.maskMoveParamFrame, 2, 0, 1, 3)

        self.maskControlDiv = QFrame(self.maskControlFrame)
        self.maskControlDiv.setObjectName(u"maskControlDiv")
        self.maskControlDiv.setFrameShape(QFrame.HLine)
        self.maskControlDiv.setFrameShadow(QFrame.Sunken)

        self.gridLayout_14.addWidget(self.maskControlDiv, 1, 0, 1, 3)

        self.maskArrowFrame = QFrame(self.maskControlFrame)
        self.maskArrowFrame.setObjectName(u"maskArrowFrame")
        self.maskArrowFrame.setMinimumSize(QSize(220, 220))
        self.maskArrowFrame.setMaximumSize(QSize(220, 220))
        self.maskArrowFrame.setFrameShape(QFrame.StyledPanel)
        self.maskArrowFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_7 = QGridLayout(self.maskArrowFrame)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.maskMoveLeft = QPushButton(self.maskArrowFrame)
        self.maskMoveLeft.setObjectName(u"maskMoveLeft")
        self.maskMoveLeft.setMinimumSize(QSize(60, 60))
        self.maskMoveLeft.setMaximumSize(QSize(60, 60))
        self.maskMoveLeft.setStyleSheet(u"image: url(:/icons/arrows/arrow-left-solid.svg);")

        self.gridLayout_7.addWidget(self.maskMoveLeft, 1, 0, 1, 1)

        self.maskMoveRight = QPushButton(self.maskArrowFrame)
        self.maskMoveRight.setObjectName(u"maskMoveRight")
        self.maskMoveRight.setMinimumSize(QSize(60, 60))
        self.maskMoveRight.setMaximumSize(QSize(60, 60))
        self.maskMoveRight.setStyleSheet(u"image: url(:/icons/arrows/arrow-right-solid.svg);")

        self.gridLayout_7.addWidget(self.maskMoveRight, 1, 4, 1, 1)

        self.maskMoveDown = QPushButton(self.maskArrowFrame)
        self.maskMoveDown.setObjectName(u"maskMoveDown")
        self.maskMoveDown.setMinimumSize(QSize(60, 60))
        self.maskMoveDown.setMaximumSize(QSize(60, 60))
        self.maskMoveDown.setStyleSheet(u"image: url(:/icons/arrows/arrow-down-solid.svg);")

        self.gridLayout_7.addWidget(self.maskMoveDown, 2, 1, 1, 1)

        self.maskMoveUp = QPushButton(self.maskArrowFrame)
        self.maskMoveUp.setObjectName(u"maskMoveUp")
        self.maskMoveUp.setMinimumSize(QSize(60, 60))
        self.maskMoveUp.setMaximumSize(QSize(60, 60))
        self.maskMoveUp.setStyleSheet(u"image: url(:/icons/arrows/arrow-up-solid.svg);")

        self.gridLayout_7.addWidget(self.maskMoveUp, 0, 1, 1, 1)

        self.maskLockMoveButton = QPushButton(self.maskArrowFrame)
        self.maskLockMoveButton.setObjectName(u"maskLockMoveButton")
        self.maskLockMoveButton.setMinimumSize(QSize(60, 60))
        self.maskLockMoveButton.setMaximumSize(QSize(60, 60))
        self.maskLockMoveButton.setStyleSheet(u"image: url(:/icons/arrows/arrow-up-solid.svg);")
        self.maskLockMoveButton.setCheckable(True)
