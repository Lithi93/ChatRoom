import os
import sys
import socket
import threading
import time
from datetime import datetime
import keyboard

# PyQt5
from PyQt5 import QtWidgets, uic, Qt
from PyQt5.QtWidgets import QDialog, QAction, QDialogButtonBox, QLineEdit, QTextEdit, QPushButton
from PyQt5.QtCore import pyqtSignal

# MyLibs
from Client.Dependencies.ClientSideUser import Client
host_settings_path = 'Setup\\host_setting.dat'  # host settings file location


class ClientUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(ClientUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('Dependencies/UI_files/ChatWindow.ui', self)  # Load the .ui file

        # variables and objects
        self.client: Client = None  # default as None
        self.nickname: str = ''
        self.host_ip: str = ''
        self.host_port: int = 0

        self.local_echo = True  # if send messages will be echoed in the chatBox

        # menus : QAction
        self.actionSettings.triggered.connect(self.get_settings)
        self.actionConnect.triggered.connect(self._start_connection)
        self.actionLocal_echo.triggered.connect(self.toggle_local_echo)

        # read current setting from host_setting.dat file
        self.read_settings()

        self.show()  # Show the GUI

    # ---------------
    # Key Press listener
    # ---------------

    def keyPressEvent(self, event):
        """listen key presses and execute function according to it"""
        if event.key() == 16777220:  # enter pressed
            self._send_user_message()  # send user message

    # ---------------
    # Client control
    # ---------------

    def _start_connection(self):
        """starts connection to the host"""
        # check that nickname, host ip and port is set before trying to connect
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not self.host_ip or not self.host_port or not self.nickname:
            msg = '> NOTICE: ip, port or nickname was missing. Could not connect.'
            self._add_msg(msg, True)
            return

        try:
            client_socket.connect((self.host_ip, self.host_port))
        except ConnectionRefusedError:
            msg = f'NOTICE: connection refused'
            self._add_msg(msg, True)
        except TimeoutError:
            msg = f'NOTICE: server might not be ON or IP address was not correct.'
            self._add_msg(msg, True)
        else:
            self.client = Client(self.nickname, self.host_ip, self.host_port, client_socket)  # create client object
            self.connect_status('Connected')

    def _send_user_message(self):
        """sends user message to server"""
        msg = self.SendBox.text()

        if self.client is not None and self.client.receive_thread.is_alive():
            self.client.write(msg)

        # if local echo is ON echo sent message in the ChatBox
        if self.local_echo:
            local = self._color_text("local", "#B53737")
            self._add_msg(f'{local}: {msg}', True)

        self.SendBox.clear()

    # ---------------
    # Connection status
    # ---------------

    def connect_status(self, status: str):
        """sets new status to label connection"""
        self.label_connection.setText(f'Connection status: {status}')

    # ---------------
    # show to user messages
    # ---------------

    def update_box(self):
        """updates chatBox with the newest message from the server and local"""
        pass

    def _add_msg(self, msg: str, timestamp=False):
        """
        adds message to the chatBox.
        :param msg: str, message to ChatBox
        :param timestamp: bool, default false. Adds timestamp to message.
        """
        chat_box: QTextEdit = self.ChatBox
        sent_msg = msg

        if timestamp:
            time = datetime.now().time().strftime("%H:%M:%S")  # timestamp
            colored_text = self._color_text(time, '#6a6a6a')  # colorise
            sent_msg = f'[{colored_text}] {msg}'

        chat_box.append(sent_msg)

    @staticmethod
    def _color_text(text: str, color: str, font_size=8, font_weight=600) -> str:
        """
        colors input text of QTextEdit with inputted color.
        :param text: str, colored text
        :param color: str, hex code of the color.
        :param font_size: int, font size.
        :param font_weight: int, font weight.
        :return span with font-size, font-weight and color
        """

        edited_text = f"<span style=\" font-size:{font_size}pt; font-weight:{font_weight}; color:{color};\" >"
        edited_text += f'{text}</span>'

        return edited_text

    # ---------------
    # Settings methods
    # ---------------

    def read_settings(self):
        """reads settings file from the user setup file to find nickname, host_ip and host_port"""
        path = host_settings_path

        # if setup folder is missing create it
        if not os.path.isdir('Setup'):
            os.makedirs('Setup')

        # read file
        host_ip = None
        host_port = None
        nickname = None

        try:
            with open(path, 'r') as f:
                setup_file = f.readlines()
        except FileNotFoundError:
            return host_ip, host_port

        # get ip, port and nickname from setup file
        for row in setup_file:
            if ';' in row:
                continue

            header, value = row.split('=')

            if 'IP' in header:
                host_ip = str(value[:-1])
            elif 'Port' in header:
                try:
                    host_port = int(value[:-1])
                except ValueError:
                    continue
            elif 'Nick' in header:
                nickname = str(value[:-1])

        self.nickname = nickname
        self.host_ip = host_ip
        self.host_port = host_port

    @staticmethod
    def write_settings(host_ip: str, host_port: int, nickname: str):
        """writes settings file to setup folder"""
        path = host_settings_path

        # if setup folder is missing create it
        if not os.path.isdir('Setup'):
            os.makedirs('Setup')

        # setup file
        with open(path, 'w') as f:
            f.write(f'[Nick]={nickname}\n')
            f.write(f'[IP]={host_ip}\n')
            f.write(f'[Port]={host_port}\n')
            f.write(';\n')

    def toggle_local_echo(self):
        """toggles local echo"""
        if self.actionLocal_echo.isChecked():
            self.local_echo = True
        else:
            self.local_echo = False

    # ---------------
    # Settings Window dialogue
    # ---------------

    def get_settings(self):
        """gets user settings from user dialogue"""
        sd = SettingsWindow()
        sd.set_current(self.nickname, self.host_ip, str(self.host_port))  # set current value to the inputs
        event = sd.exec_()

        # print(f'{sd.nickname=}, {sd.ip=}, {sd.port=}')  # debug

        if event:
            self.nickname = sd.nickname
            self.host_ip = sd.ip
            self.host_port = sd.port


class SettingsWindow(QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        uic.loadUi('Dependencies/UI_files/SettingsWindow.ui', self)  # Load the .ui file

        # variables and objects
        self.nickname: str = ''
        self.ip: str = ''
        self.port: int = 0

        # used line edits
        self.name_lineEdit: QLineEdit
        self.ip_lineEdit: QLineEdit
        self.port_lineEdit: QLineEdit

        # buttons
        self.buttonBox: QDialogButtonBox
        self.buttonBox.accepted.connect(self._get_values)
        self.buttonBox.rejected.connect(self.reject)

        self.show()  # Show the GUI

    def _get_values(self):
        """get values from user input"""
        self.nickname = self.name_lineEdit.text()
        self.ip = self.ip_lineEdit.text()
        self.port = int(self.port_lineEdit.text())

        self.accept()  # accept values

    def set_current(self, name: str, ip: str, port: str):
        """sets current value to the QLineEdits"""
        self.name_lineEdit.setText(name)
        self.ip_lineEdit.setText(ip)
        self.port_lineEdit.setText(port)
