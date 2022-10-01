import os
import socket
import time
from datetime import datetime

# PyQt5
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QTextEdit, QPushButton, QListWidgetItem, QToolButton, QFontComboBox, QSpinBox, QColorDialog
from PyQt5.QtCore import QTimer

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
        self.host_ip: str = '127.0.0.1'
        self.host_port: int = 55555

        self.local_echo = True  # if send messages will be echoed in the chatBox

        # update chatBox every second
        self.chat_update_intv = QTimer()
        self.chat_update_intv.timeout.connect(self.update_box)

        # menus : QAction
        self.actionSettings.triggered.connect(self.get_settings)
        self.actionConnect.triggered.connect(self._start_connection)
        self.actionLocal_echo.triggered.connect(self.toggle_local_echo)
        self.actionClear.triggered.connect(self.ChatBox.clear)
        self.actionFont.triggered.connect(self.get_font_options)

        # minimize button
        self.minimizeToolButton: QToolButton
        self.minimizeToolButton.clicked.connect(self.hide_and_show_participants)

        # font and font size options
        self.font_family: str = 'Segoe UI'
        self.font_size: int = 8
        self.text_color: str = '#000000'

        # read current setting from host_setting.dat file
        self.read_settings()

        self.show()  # Show the GUI

    # ---------------
    # KeyPressListener
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
            msg = 'NOTICE: ip, port or nickname was missing. Could not connect. See settings menu.'
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
            self.chat_update_intv.start(1)  # start
            self.connect_status('Connected')

    def _send_user_message(self):
        """sends user message to server"""
        msg = self.SendBox.text()

        if self.client is not None and self.client.receive_thread.is_alive():
            self.client.write(msg)

        # if local echo is ON echo sent message in the ChatBox
        if self.local_echo:
            local = self._text("local", "#B53737", font_family=self.font_family, font_size=self.font_size)
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
        """updates chatBox with the newest message from the server and local. Also updates the participant list"""
        messages = self.client.get_buffer()
        for row in messages:
            if not row:
                continue
            self._add_msg(row, True)

        # update participant list
        try:
            participants: list = self.client.get_names()
        except ValueError:
            pass
        else:
            if participants is not None and participants:
                if self.get_list_items(self.ParticipantsList)[1:] != participants:
                    self.ParticipantsList.clear()
                    self.ParticipantsList.addItem('Participants in chatroom')
                    self.ParticipantsList.addItems(participants)

        if not self.client.receive_thread.is_alive():
            self.chat_update_intv.stop()  # start
            self.connect_status('Not connected')

    def _add_msg(self, msg: str, timestamp=False):
        """
        adds message to the chatBox.
        :param msg: str, message to ChatBox
        :param timestamp: bool, default false. Adds timestamp to message.
        """
        chat_box: QTextEdit = self.ChatBox
        sent_msg = msg.split('\n')

        for i, row in enumerate(sent_msg):
            if i == 0:  # add timestamp to only first row of multiline message
                if timestamp:
                    t = datetime.now().time().strftime("%H:%M:%S")  # timestamp
                    colored_text = self._text(f'[{t}]', '#6a6a6a', font_family=self.font_family, font_size=self.font_size)  # colorise
                    rest = self._text(f'{colored_text}{row}', self.text_color, font_family=self.font_family, font_size=self.font_size)  # colorise
                    row = rest
            else:
                rest = self._text(f'{" " * 17}{row}', self.text_color, font_family=self.font_family, font_size=self.font_size)  # colorise
                row = f'{rest}'

            chat_box.append(row)

    @staticmethod
    def _text(text: str, color: str, font_family: str, font_size=8, font_weight=600) -> str:
        """
        colors input text of QTextEdit with inputted color.
        :param text: str, colored text
        :param color: str, hex code of the color.
        :param font_size: int, font size.
        :param font_weight: int, font weight.
        :return span with font-size, font-weight and color
        """

        edited_text = f"<span style=\" font-family: {font_family}; font-size:{font_size}pt; font-weight:{font_weight}; color:{color}; white-space:pre;\" >"
        edited_text += f'{text}</span>'

        return edited_text

    @staticmethod
    def get_list_items(lw):
        """gets list items as text from QListWidgetItem"""
        items = []
        for x in range(lw.count()):
            item: QListWidgetItem = lw.item(x)
            items.append(item.text())
        return items

    # ---------------
    # Settings methods
    # ---------------

    def read_settings(self):
        """reads settings file from the user setup file to find nickname, host_ip and host_port"""
        path = host_settings_path

        # if setup folder is missing create it
        if not os.path.isdir('Setup'):
            os.makedirs('Setup')

        try:
            with open(path, 'r') as f:
                setup_file = f.readlines()
        except FileNotFoundError:
            return

        params: dict = {
            'IP': self.host_ip,
            'Port': self.host_port,
            'Nick': self.nickname,
            'Font-family': self.font_family,
            'Font-size': self.font_size,
            'Font-color': self.text_color,
        }

        integers = ['Port', 'Font-size']

        # get ip, port and nickname from setup file
        for row in setup_file:
            if ';' in row:
                continue

            # parse header and value
            header, value = row.split('=')
            header: str = header.replace('[', '').replace(']', '')
            value = value.strip()

            # change default value to value read from setup file
            if header in params.keys():

                # turn all setup value in the integers list to int values
                if header in integers:
                    try:
                        value = int(value)
                    except ValueError:
                        continue

                params[header] = value

        # set read values
        self.host_ip = params['IP']
        self.host_port = params['Port']
        self.nickname = params['Nick']
        self.font_family = params['Font-family']
        self.font_size = params['Font-size']
        self.text_color = params['Font-color']

    @staticmethod
    def write_settings(host_ip: str, host_port: int, nickname: str, font_family: str, font_size: int, font_color: str):
        """writes settings file to setup folder"""
        path = host_settings_path

        # if setup folder is missing create it
        if not os.path.isdir('Setup'):
            os.makedirs('Setup')

        # setup file
        with open(path, 'w') as f:
            f.write(f'[Nick]={nickname}\n')
            f.write(f'[Font-family]={font_family}\n')
            f.write(f'[Font-size]={font_size}\n')
            f.write(f'[Font-color]={font_color}\n')
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
    # Window dialogues
    # ---------------

    def get_settings(self):
        """gets user settings from user dialogue"""
        sd = SettingsWindow()
        sd.set_current(self.nickname, self.host_ip, str(self.host_port))  # set current value to the inputs
        event = sd.exec_()

        if event:
            self.nickname = sd.nickname
            self.host_ip = sd.ip
            self.host_port = sd.port

            self.write_settings(self.host_ip, self.host_port, self.nickname, self.font_family, self.font_size, self.text_color)

    def get_font_options(self):
        """gets selected font options"""
        sd = FontOptions()
        sd.set_current(self.font_family, self.font_size)  # set current value to the inputs
        event = sd.exec_()

        if event:
            self.font_family = sd.font_family
            self.font_size = sd.font_size
            self.text_color = sd.text_color

            self.write_settings(self.host_ip, self.host_port, self.nickname, self.font_family, self.font_size, self.text_color)

    # ---------------
    # other actions
    # ---------------

    def hide_and_show_participants(self):
        """hides and shows participants list"""
        if self.ParticipantsList.isHidden():
            self.ParticipantsList.show()
            self.minimizeToolButton.setText('-')
        else:
            self.ParticipantsList.hide()
            self.minimizeToolButton.setText('+')


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


class FontOptions(QDialog):
    def __init__(self):
        super(FontOptions, self).__init__()
        uic.loadUi('Dependencies/UI_files/FontOptionsWindow.ui', self)  # Load the .ui file

        self.font_family: str = ''
        self.font_size: int = 0
        self.text_color: str = ''

        self.pushButton_picker: QPushButton
        self.pushButton_picker.clicked.connect(self.color_picker)

        # buttons
        self.buttonBox: QDialogButtonBox
        self.buttonBox.accepted.connect(self._get_values)
        self.buttonBox.rejected.connect(self.reject)

        self.show()  # Show the GUI

    def color_picker(self):
        """picks color selected by user"""
        color = QColorDialog.getColor()

        if color.isValid():
            self.text_color = color.name()

    def _get_values(self):
        """get values from user input"""
        self.fontComboBox: QFontComboBox
        self.spinBox_size: QSpinBox

        self.font_family = self.fontComboBox.currentFont().family()
        self.font_size = self.spinBox_size.value()

        self.accept()  # accept values

    def set_current(self, font_family: str, font_size: int):
        """sets current value to the QLineEdits"""
        self.fontComboBox: QFontComboBox
        self.spinBox_size: QSpinBox

        self.fontComboBox.setCurrentFont(QFont(font_family))
        self.spinBox_size.setValue(font_size)
