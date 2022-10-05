import socket
import threading
from datetime import datetime
from cryptography.fernet import Fernet
from hashlib import scrypt
from base64 import urlsafe_b64encode


"""
source for the example: https://www.neuralnine.com/tcp-chat-in-python/
"""


class Client:
    def __init__(self, nickname: str, host_ip: str, port: int, client_socket: socket.socket, password: str):
        # Connecting To Server
        self._client_socket = client_socket
        self.receive_thread = None
        self.host_ip = host_ip
        self.host_port = port
        self.nickname = nickname
        self.password = password

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

        # salt that was received from server, and fernet created from it
        self.salt = None
        self.fernet: Fernet = None

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

                    # if received message contains salt from server
                    if '<SALT>;' in message:
                        self._get_salted(message)
                        continue

                    # if server has disconnected the client. If this part is removed the client _receive thread won't shutdown when server disconnects it
                    if '<ShutDown>;' in message:
                        break

                    if message:
                        # if message is tagged as encrypted
                        if self.fernet is not None:
                            if '<ENCRYPTED>;' in message:
                                message = self._decrypt_message(message)

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
    def write(self, m: str, encrypt=True):
        """
        sends message to the server.
        :param m: str, sent message.
        :param encrypt: bool, if true the message is encrypted before sending.
        """
        message = f'<{datetime.now().time().strftime("%H:%M:%S")}>[{self.nickname}]; {m}'

        if encrypt:
            encrypted_msg = self.fernet.encrypt(message.encode())
            message = f'<ENCRYPTED>;{encrypted_msg}'

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

    def _decrypt_message(self, message: str):
        """decrypts message if encrypted"""

        # parse encrypted message
        header, encrypted_msg = message.split(";b'")
        encrypted_msg = encrypted_msg[:-1]

        try:
            decrypted_msg = self.fernet.decrypt(encrypted_msg.encode('utf-8')).decode()
        except:
            decrypted_msg = f'Message could not be decrypted!'

        return decrypted_msg

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

    def _get_salted(self, salt: str):
        """receives server salt, all salt are different per server session"""

        # parse salt from message and store it
        header, bin_salt = salt.split(";b")
        self.salt = bin_salt[1:-1].encode('utf-8')
        self.generate_key()

    def generate_key(self, new_key=None):
        """generate key from salt and password"""

        # if new key is generated
        if new_key is not None:
            self.password = new_key

        key = scrypt(self.password.encode('utf-8'), salt=self.salt, n=16384, r=8, p=1, dklen=32)
        key_encoded = urlsafe_b64encode(key)
        self.fernet = Fernet(key_encoded)
