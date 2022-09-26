import os
import sys

# PyQt5
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QAction, QDialogButtonBox, QLineEdit

# MyLibs
from Dependencies.ClientSideUser import Client
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

        self.local_echo = False  # if send messages will be echoed in the chatBox

        # buttons

        # menus
        self.actionSettings: QAction
        self.actionSettings.triggered.connect(self.get_settings)

        # read current setting from host_setting.dat file
        self.read_settings()

        self.show()  # Show the GUI

    # ---------------
    # Client control
    # ---------------

    def start_connection(self):
        """starts connection to the host"""
        # check that nickname, host ip and port is set before trying to connect
        pass

    def send_user_message(self):
        """sends user message to server"""
        pass

    def update_box(self):
        """updates chatBox with messages send from the server"""
        pass

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
