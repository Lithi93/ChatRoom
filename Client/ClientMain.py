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

    app = QtWidgets.QApplication(sys.argv)
    window = ClientUI()
    app.exec_()
