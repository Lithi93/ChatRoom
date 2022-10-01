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

        # message buffer
        self.buffer = []  # contains all received messages until the buffer is emptied (in get_buffer())

        # chatroom names
        self._names = []  # all participant names in the current chatroom

        # query types that client can store
        self.queries = {
            '<names>': self._store_names,
        }

    # ------------------------
    # gets
    # ------------------------

    def get_names(self):
        """returns participant names"""
        return self._names

    # ------------------------
    # Basic communication
    # ------------------------

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
                    # if received message is query
                    if '<query>;' in message:
                        self._receive_query(message)
                        continue

                    # if server has disconnected the client. If this part is removed the client _receive thread won't shutdown when server disconnects it
                    if '<ShutDown>;' in message:
                        break

                    if message:
                        self.buffer.append(message)  # append to buffer message
            except Exception as e:
                # Close Connection When Error
                print(f"An error occurred! - {e}")
                self._client_socket.close()
                break
        return

    def get_buffer(self) -> list:
        """returns all messages from the buffer"""
        buffer = self.buffer.copy()  # copy buffer content
        self.buffer.clear()  # clear buffer
        self.received_messages += buffer  # add messages to received messages
        return buffer  # return buffer

    # Sending Messages To Server
    def write(self, m: str):
        """
        sends message to the server.
        :param m: str, sent message.
        """
        message = f'<{datetime.now().time().strftime("%H:%M:%S")}>[{self.nickname}]; {m}'
        self._client_socket.send(message.encode('utf-8'))

    # ------------------------
    # receive queries
    # ------------------------

    def _receive_query(self, message: str):
        """receives query from server"""
        query, query_type, data = message.split(';')
        query_type = query_type.strip()
        data = data.strip()

        if query_type in self.queries.keys():
            method = self.queries[query_type]
            method(data)

    # ------------------------
    # store queries
    # ------------------------

    def _store_names(self, *argv):
        """stores current chatroom participant names"""
        names: str = argv[0]  # get names

        # remove chars from the names
        for char in ['[', ']', "\'", " "]:
            names = names.replace(char, '')

        self._names = names.split(',')  # store all names
