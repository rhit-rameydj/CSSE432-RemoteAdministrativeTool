from PyQt5 import sip

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QLineEdit
import sys

from AdministratorControlPanel import AdministratorControlPanel
from RATFunction.FileTransfer import FileTransfer
from RATFunction.Message import Message
from RATFunction.RemoteCamera import RemoteCamera
from RATFunction.RemoteDesktop import RemoteDesktop
from RATFunction.MyLogging import MyLogging
from RATFunction.RemoteExecution import RemoteExecution

from RemoteSystemMode import RemoteSystemMode

function_classes = [Message, RemoteDesktop, MyLogging, RemoteCamera, FileTransfer, RemoteExecution]


class SystemSelectionDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.widget = None

        # create a vertical layout for the dialog
        self.layout = QVBoxLayout()

        # add a label to the layout
        self.label = QLabel("Which system will you be running?")
        self.layout.addWidget(self.label)

        # add two buttons to the layout
        self.admin_button = QPushButton("Administrator")
        self.admin_button.clicked.connect(self.select_administrator)
        self.layout.addWidget(self.admin_button)

        self.remote_button = QPushButton("Remote System")
        self.remote_button.clicked.connect(self.select_remote_system)
        self.layout.addWidget(self.remote_button)

        # set the layout for the dialog
        self.setLayout(self.layout)

        # set the window title and size
        self.setWindowTitle("System Selection")
        self.setFixedSize(300, 150)

    def select_administrator(self):
        print("User selected: Administrator")
        self.hide()
        self.widget = AdministratorControlPanel(function_classes)
        self.widget.show()

    def select_remote_system(self):

        # Create a dialog to get user input
        dialog = QDialog(self)
        dialog.setWindowTitle('Password')

        # Create a label and text input field in the dialog
        label = QLabel('Set your client password:', dialog)
        input_field = QLineEdit(dialog)
        port_label = QLabel('Port:', dialog)
        port_input_field = QLineEdit(dialog)
        port_input_field.setText('8888')
        port_input_field.setValidator(QIntValidator())

        # Layout the label and text input field in the dialog
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addWidget(port_label)
        layout.addWidget(port_input_field)
        dialog.setLayout(layout)

        # Add OK and Cancel buttons to the dialog
        ok_button = QPushButton('OK', dialog)
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton('Cancel', dialog)
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        # Display the dialog and wait for user input
        if dialog.exec_() == QDialog.Rejected:
            return

        password = input_field.text()
        port = int(port_input_field.text())
        self.widget = RemoteSystemMode(function_classes, password, port)
        self.widget.show()
        self.hide()


if __name__ == "__main__":

    # create an instance of the dialog and show it
    app = QApplication(sys.argv)
    dialog = SystemSelectionDialog()
    dialog.show()

    # start the application event loop
    sys.exit(app.exec_())
