# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from PySide6.QtCore import (QRegularExpression,
                            QSortFilterProxyModel, Qt, Slot)
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
                               QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QTreeView, QVBoxLayout, QWidget)
from ....stacking_middleware.message import Message
from random import randint
import datetime
import datetime

REGULAR_EXPRESSION = 0
WILDCARD = 1
FIXED_STRING = 2


class SystemMessageWidget(QWidget):
    name = 'System Messages'
    commands_to_ignore = ['M114', 'M154', 'M155']

    def __init__(self, settings, parent=None):
        """
        Initialize the widget.
        
        Parameters
        ----------
        settings : Settings
            The settings object.
        parent : QWidget, optional
            The parent widget.
        """
        super().__init__(parent)
        self.settings = settings
        self.setup_widget()
        self.set_source_model(self._create_model())

    def setup_widget(self):
        """Setup the widget."""
        self._proxy_model = QSortFilterProxyModel()
        self._proxy_model.setDynamicSortFilter(True)

        # self._source_group_box = QGroupBox("Original Model")
        self._proxy_group_box = QGroupBox(self.name)

        self._source_view = QTreeView()
        self._source_view.setRootIsDecorated(False)
        self._source_view.setAlternatingRowColors(True)

        self._proxy_view = QTreeView()
        self._proxy_view.setRootIsDecorated(False)
        self._proxy_view.setAlternatingRowColors(True)
        self._proxy_view.setModel(self._proxy_model)
        self._proxy_view.setSortingEnabled(True)

        self._sort_case_sensitivity_check_box = QCheckBox("Case sensitive sorting")
        self._filter_case_sensitivity_check_box = QCheckBox("Case sensitive filter")

        self._filter_pattern_line_edit = QLineEdit()
        self._filter_pattern_line_edit.setClearButtonEnabled(True)
        self._filter_pattern_label = QLabel("&Filter pattern:")
        self._filter_pattern_label.setBuddy(self._filter_pattern_line_edit)

        self._filter_syntax_combo_box = QComboBox()
        self._filter_syntax_combo_box.addItem("Regular expression",
                                          REGULAR_EXPRESSION)
        self._filter_syntax_combo_box.addItem("Wildcard",
                                          WILDCARD)
        self._filter_syntax_combo_box.addItem("Fixed string",
                                          FIXED_STRING)
        self._filter_syntax_label = QLabel("Filter &syntax:")
        self._filter_syntax_label.setBuddy(self._filter_syntax_combo_box)

        self._filter_column_combo_box = QComboBox()
        self._filter_column_combo_box.addItem("Time")
        self._filter_column_combo_box.addItem("Exit-code")
        self._filter_column_combo_box.addItem("Command")
        self._filter_column_combo_box.addItem("Message")
        self._filter_column_label = QLabel("Filter &column:")
        self._filter_column_label.setBuddy(self._filter_column_combo_box)

        self._filter_pattern_line_edit.textChanged.connect(self.filter_reg_exp_changed)
        self._filter_syntax_combo_box.currentIndexChanged.connect(self.filter_reg_exp_changed)
        self._filter_column_combo_box.currentIndexChanged.connect(self.filter_column_changed)
        self._filter_case_sensitivity_check_box.toggled.connect(self.filter_reg_exp_changed)
        self._sort_case_sensitivity_check_box.toggled.connect(self.sort_changed)

        proxy_layout = QGridLayout()
        proxy_layout.addWidget(self._proxy_view, 0, 0, 1, 3)
        proxy_layout.addWidget(self._filter_pattern_label, 1, 0)
        proxy_layout.addWidget(self._filter_pattern_line_edit, 1, 1, 1, 2)
        proxy_layout.addWidget(self._filter_syntax_label, 2, 0)
        proxy_layout.addWidget(self._filter_syntax_combo_box, 2, 1, 1, 2)
        proxy_layout.addWidget(self._filter_column_label, 3, 0)
        proxy_layout.addWidget(self._filter_column_combo_box, 3, 1, 1, 2)
        proxy_layout.addWidget(self._filter_case_sensitivity_check_box, 4, 0, 1, 2)
        proxy_layout.addWidget(self._sort_case_sensitivity_check_box, 4, 2)
        self._proxy_group_box.setLayout(proxy_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._proxy_group_box)
        self.setLayout(main_layout)

        self.setWindowTitle("Basic Sort/Filter Model")
        # self.resize(500, 450)

        self._proxy_view.sortByColumn(1, Qt.AscendingOrder)
        self._filter_column_combo_box.setCurrentIndex(1)

        self._filter_pattern_line_edit.setText("")
        self._filter_case_sensitivity_check_box.setChecked(True)
        self._sort_case_sensitivity_check_box.setChecked(True)

    def set_source_model(self, model):
        """
        Set the source model.
        
        Parameters
        ----------
        model : QAbstractItemModel
            The source model.
        """
        self._proxy_model.setSourceModel(model)
        self._source_view.setModel(model)
        self.model = model

    @Slot()
    def filter_reg_exp_changed(self):
        """Filter the model using regex."""
        syntax_nr = self._filter_syntax_combo_box.currentData()
        pattern = self._filter_pattern_line_edit.text()
        if syntax_nr == WILDCARD:
            pattern = QRegularExpression.wildcardToRegularExpression(pattern)
        elif syntax_nr == FIXED_STRING:
            pattern = QRegularExpression.escape(pattern)

        reg_exp = QRegularExpression(pattern)
        if not self._filter_case_sensitivity_check_box.isChecked():
            options = reg_exp.patternOptions()
            options |= QRegularExpression.CaseInsensitiveOption
            reg_exp.setPatternOptions(options)
        self._proxy_model.setFilterRegularExpression(reg_exp)

    @Slot()
    def filter_column_changed(self):
        """Filter the model using a column."""
        self._proxy_model.setFilterKeyColumn(self._filter_column_combo_box.currentIndex())

    @Slot()
    def sort_changed(self):
        """Sort the model."""
        if self._sort_case_sensitivity_check_box.isChecked():
            case_sensitivity = Qt.CaseSensitive
        else:
            case_sensitivity = Qt.CaseInsensitive

        self._proxy_model.setSortCaseSensitivity(case_sensitivity)

    def add_message(self, message):
        """
        Add a message to the model.
        
        Parameters
        ----------
        message : dict
            The message to add.
        """
        if message.command_id in self.commands_to_ignore:
            return
        self.model.insertRow(0)
        self.model.setData(self.model.index(0, 0), str(message.timestamp))
        self.model.setData(self.model.index(0, 1), str(message.exit_code))
        self.model.setData(self.model.index(0, 2), str(message.command_id))
        self.model.setData(self.model.index(0, 3), str(message.command))
        self.model.setData(self.model.index(0, 4), str(message.msg))

    def _create_model(self):
        model = QStandardItemModel(0, 5, self)
        model.setHeaderData(0, Qt.Horizontal, "Time")
        model.setHeaderData(1, Qt.Horizontal, "Exit-code")
        model.setHeaderData(2, Qt.Horizontal, "Id")
        model.setHeaderData(3, Qt.Horizontal, "Command")
        model.setHeaderData(4, Qt.Horizontal, "Message")
        return model