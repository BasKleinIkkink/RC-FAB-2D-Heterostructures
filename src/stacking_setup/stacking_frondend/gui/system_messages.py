from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import datetime
import threading as tr


class Message:
    """Class used to send status messages between the frond and backend."""

    def __init__(self, exit_code, command, msg, *args, **kwargs):
        self._exit_code = exit_code
        self._command = command
        self._msg = msg
        self._args = args
        self._kwargs = kwargs
        self._timestamp = datetime.datetime.now()

    @property
    def exit_code(self):
        return self._exit_code

    @property
    def msg(self):
        return self._msg

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def command(self):
        return self._command

    def __str__(self):
        return self._msg

    def items(self):
        return {'exit_code': self._exit_code,
                'command': self._command,
                'msg': self._msg,
                'args': self._args,
                'kwargs': self._kwargs,
                'timestamp': self._timestamp}

    def keys(self):
        return self.items().keys()

    def values(self):
        return self.items().values()


class SystemMessagesWidget(QGroupBox):
    name = "System Messages"

    def __init__(self, parent=None):
        super().__init__(self.name, parent)

        self.setup_widget()
    
    def setup_widget(self):
        """Set up the widget."""
        # Set the group box title
        self.setTitle("System Messages")
        self.verticle_layout = QVBoxLayout(self)

        self.setFixedSize(800, 840)
        
        # Add the save and reset buttons
        self.buttonFrame = QFrame(self)
        self.buttonFrameLayout = QHBoxLayout(self.buttonFrame)
        self.saveButton = QPushButton(self.buttonFrame)
        self.saveButton.setText("Save")
        self.resetButton = QPushButton(self.buttonFrame)
        self.resetButton.setText("Reset")
        self.buttonFrameLayout.addWidget(self.saveButton)
        self.buttonFrameLayout.addWidget(self.resetButton)
        self.verticle_layout.addWidget(self.buttonFrame)

        # Add the horizontal divider
        self.horizontal_div = QFrame(self)
        self.horizontal_div.setFrameShape(QFrame.HLine)
        self.horizontal_div.setFrameShadow(QFrame.Sunken)
        self.verticle_layout.addWidget(self.horizontal_div)

        # Add the table model
        self._add_table_model()        

    def _add_table_model(self):
        self.table_model = MessageWidget(self)
        self.verticle_layout.addWidget(self.table_model)


class MessageWidget(QTabWidget):
    # List of commands that is not displayed in the table (is still saved)
    _ignored_commands = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_model = self.TableModel(parent=parent)
        self.lock = tr.Lock()
        self.setup_widget()

    def setup_widget(self):
        # Create the All, Error and success tabs
        self.all_tab = QTableView()
        #self.error_tab = QTableView()
        #self.success_tab = QTableView()

        # Add the tabs to the widget
        self.addTab(self.all_tab, "All")
        #self.addTab(self.error_tab, "Error")
        #self.addTab(self.success_tab, "Success")

        # Populate the all tab

        # When clicked on the tab, the table will be populated with the messages
        # that match the tab name
        #self.currentChanged.connect(self.populate_table)

    # DATA INTERFACE
    def get_row(self, row):
        return self._table_model._data[row]

    def get_messages(self, exit_code=None, command=None):
        """Get the messages that match the given exit code and command."""
        if exit_code is None and command is None:
            return self._table_model._data
        elif exit_code is None:
            return [row for row in self._table_model._data if row[2] == command]
        elif command is None:
            return [row for row in self._table_model._data if row[1] == exit_code]
        else:
            return [row for row in self._table_model._data if row[1] == exit_code and row[2] == command]	

    # SIGNAL SLOTS
    @Slot()
    def populate_table(self):
        if self.currentIndex() == 0:
            self._populate_all_tab()
        elif self.currentIndex() == 1:
            self._populate_error_tab()
        elif self.currentIndex() == 2:
            self._populate_success_tab()

    def _populate_all_tab(self):
        """Populate the all tab."""
        # Populate the table with all the messages
        group = self.get_messages()

        # Remove the old tab
        self.addTab(self.all_tab, "All")


    def _populate_error_tab(self):
        """Populate the error tab."""
        # Populate the table with all the error messages
        #self._table_model._filtered_data = self.get_messages(exit_code=1)
        pass

    def _populate_success_tab(self):
        """Populate the success tab."""
        # Populate the table with all the success messages
        # self._table_model._filtered_data = self.get_messages(exit_code=0)
        pass

    @Slot()
    def add_message(self, message):
        """Add a message to the table."""
        # Createthe rows
        # Step 1: create the  row
        self._table_model.insertRows(0)

        # Step 2: set the data
        for i, col in enumerate(self._columns):
            ix = self._table_model.index(0, i, QModelIndex())
            self._table_model.setData(ix, message[col])

        # The screenshot for the QT example shows nicely formatted
        # multiline cells, but the actual application doesn't behave
        # quite so nicely, at least on Ubuntu. Here we resize the newly
        # created row so that multiline addresses look reasonable.
        table_view = self.currentWidget()
        table_view.resizeRowToContents(ix.row())

    class TableModel(QAbstractTableModel):

        def __init__(self, messages=None, parent=None):
            super().__init__(parent)
            self._columns = ["Timestamp", "Exit code", "Command", "Message"]
            self._n_columns = len(self._columns)
            self._data = []

            messages = [Message(1, "M304", "Invalid syntax")]
            if messages is not None:
                for msg in messages:
                    self._data.append({"Timestamp": msg.timestamp, "Exit-code": msg.exit_code, 
                                    "Command": msg.command, "Message": msg.msg})

        def rowCount(self, index=QModelIndex()):
            """ Returns the number of rows the model holds. """
            return len(self._data)

        def columnCount(self, index=QModelIndex()):
            """ Returns the number of columns the model holds. """
            return self._n_columns

        def data(self, index, role=Qt.DisplayRole):
            """ 
            Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
            """
            if not index.isValid():
                return None

            if not 0 <= index.row() < self.rowCount():
                return None

            if role == Qt.DisplayRole:
                timestamp, exit_code, command, msg, _, _ = self._data[index.row()]

                if index.column() == 0:
                    return timestamp
                elif index.column() == 1:
                    return exit_code
                elif index.column() == 2:
                    return command
                elif index.column() == 3:
                    return msg
            return None

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            """ Set the headers to be displayed. """
            if role != Qt.DisplayRole:
                return None

            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Timestamp"
                elif section == 1:
                    return "exit_code"
                elif section == 2:
                    return "Command"
                elif section == 3:
                    return "Message"
            return None

        def insertRows(self, position, rows=1, index=QModelIndex()):
            """ Insert a row into the model. """
            self.beginInsertRows(QModelIndex(), position, position + rows - 1)

            for row in range(rows):
                self._data.insert(position + row, {"Timestamp": "", "Exit-code": "", 
                                    "Command": "", "Message": ""})

            self.endInsertRows()
            return True

        def removeRows(self, position, rows=1, index=QModelIndex()):
            """ Remove a row from the model. """
            self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

            del self.addresses[position:position + rows]

            self.endRemoveRows()
            return True

        def setData(self, index, value, role=Qt.EditRole):
            """ Adjust the data (set it to <value>) depending on the given
                index and role.
            """
            if role != Qt.EditRole:
                return False

            if index.isValid() and 0 <= index.row() < len(self.addresses):
                message = self._data[index.row()]
                if index.column() == 0:
                    message["Timestamp"] = value
                elif index.column() == 1:
                    message["Exit-code"] = value
                elif index.column() == 2:
                    message["Command"] = value
                elif index.column() == 3:
                    message["Message"] = value
                else:
                    return False

                self.dataChanged.emit(index, index, 0)
                return True

            return False

        def flags(self, index):
            """ Set the item flags at the given index. Seems like we're
                implementing this function just to see how it's done, as we
                manually adjust each tableView to have NoEditTriggers.
            """
            if not index.isValid():
                return Qt.ItemIsEnabled
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsEditable)
