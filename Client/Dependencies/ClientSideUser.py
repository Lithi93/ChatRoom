import socket
import threading
from datetime import datetime

"""
source for the example: https://www.neuralnine.com/tcp-chat-in-python/
"""


class Client:
    def __init__(self, nickname: str, host_ip: str, port: int, client_socket: socket.socket):
        # Connecting To Server
        self._client_socket = client_socket
        self.receive_thread = None
        self.host_ip = host_ip
        self.host_port = port
        self.nickname = nickname

        # Starting Threads For Listening And Writing
        self.receive_thread = threading.Thread(target=self._receive, daemon=True)
        self.receive_thread.start()

        # received messages
        self.received_messages = []  # contains all received message in received order
        self.received_messages_plus = []  # contains all received message plus local echoes

    # Listening to Server and Sending Nickname
    def _receive(self):
        t = threading.current_thread()
        while getattr(t, "do_run", True):
            try:
                # Receive Message From Server
                # If 'NICK' Send Nickname
                message = self._client_socket.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self._client_socket.send(self.nickname.encode('utf-8'))
                else:
                    self.received_messages.append(message)  # append message
            except:
                # Close Connection When Error
                print("An error occurred!")
                self._client_socket.close()
                break

    # Sending Messages To Server
    def write(self, m: str):
        """
        sends message to the server.
        :param m: str, sent message.
        """
        message = f'<{datetime.now().time().strftime("%H:%M:%S")}>[{self.nickname}]; {m}'
        self._client_socket.send(message.encode('utf-8'))
