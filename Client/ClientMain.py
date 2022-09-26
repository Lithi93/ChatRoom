import os.path
import socket
import sys
import logging
from PyQt5 import QtWidgets

from Dependencies.Interface import ClientUI


# exception logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

"""

Make sw diagram before proceeding!!

"""

host_settings_path = 'Setup\\host_setting.dat'


def get_host_settings() -> (str, int, socket.socket):
    """determines host IP and port according to the users selection"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:

        # determine host_ip and port
        # if they are written in setup file read first from there and if the connection refuses ask the new IP and port
        host_ip, host_port = setup()

        if host_ip is None and host_port is None:
            while True:
                # get host ip and port
                host_ip = str(input('Host IP?: ').strip().lower())
                host_port = int(input('Host port?: ').strip().lower())

                # confirm selection
                print(f'Host IP: {host_ip}, Host port: {host_port}.')
                y = input('Continue [Y]?: ').strip().lower()

                if y == 'y':
                    # write new setup file
                    write_setup(host_ip, host_port)
                    break

        try:
            client_socket.connect((host_ip, host_port))
        except (ConnectionRefusedError, TimeoutError):
            print('\n> NOTICE: connection refused, server might not be ON or IP address was not correct.')
            y = input('Try again?[y]: ')

            if y != 'y':
                exit()
        else:
            return host_ip, host_port, client_socket


def write_setup(host_ip: str, host_port: int):
    """writes setup file of the host"""
    path = host_settings_path

    # if setup folder is missing create it
    if not os.path.isdir('Setup'):
        os.makedirs('Setup')

    # setup file
    with open(path, 'w') as f:
        f.write(f'[IP]={host_ip}\n')
        f.write(f'[Port]={host_port}\n')
        f.write(';\n')


def setup() -> (str, int) or (None, None):
    """if setup file read it"""
    path = host_settings_path

    # if setup folder is missing create it
    if not os.path.isdir('Setup'):
        os.makedirs('Setup')

    # read file
    setup_file = []
    host_ip = None
    host_port = None

    try:
        with open(path, 'r') as f:
            setup_file = f.readlines()
    except FileNotFoundError:
        return host_ip, host_port

    # get ip and port
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

    return host_ip, host_port


def get_nickname() -> str:
    """gets nickname from the user"""
    while True:
        # nickname
        nick = str(input('Your nickname?: ')).strip()

        # confirm selection
        y = input(f'Your nickname is {nick}. Continue [Y]?: ').strip().lower()

        if y == 'y':
            return nick


def exception_hook(exc_type, exc_value, exc_traceback):
    # ignore keyboard interruptions "ctrl + c"
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # log uncaught errors to file
    logging.basicConfig(filename="CrashLog.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == '__main__':
    sys.excepthook = exception_hook  # uncomment if no hook is needed. Running Pycharm on debugger mode disables hook.

    # ip, port, s = get_host_settings()  # get host details and create socket
    # name = get_nickname()  # get user nickname

    # starts connection with server
    # user = Client(name, ip, port, s)
    # user.write()

    app = QtWidgets.QApplication(sys.argv)
    window = ClientUI()
    app.exec_()
