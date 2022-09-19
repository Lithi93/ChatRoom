import socket
import threading
import time
from datetime import datetime

from Server.Dependencies.User import Client


class ChatRoom:
    def __init__(self, name: str):
        self.name: str = name  # name of the chatroom
        self._clients: list[Client] = []  # connected clients in the chatroom
        self.chat_log: list[str] = []  # contains all messages sent in the chatroom
        self._server_listening = False

        # while chatroom is active be ready to receive messages
        self.active = True
        self.incoming = threading.Thread(target=self._incoming_messages, daemon=True)
        self.incoming.start()

    # ------------------
    # message handling
    # ------------------

    def _incoming_messages(self):
        """checks clients for new messages"""
        while self.active:
            time.sleep(0.001)  # delay for the message update

            new_messages = []  # TODO <- these might be needed to be sorted depending on the timestamp in them
            for client in self._clients:
                messages = client.get_message()  # get current message buffer from the client
                if messages:
                    new_messages += messages

            # broadcast all new messages
            for msg in new_messages:
                self.broadcast(msg)

    def broadcast(self, message: str, excluded=None):
        """broadcasts messages in the room"""

        if excluded is None:
            excluded = []

        # broadcast message to all users in the chatroom
        for client in self._clients:
            # skip client that are excluded
            if client.user_ID in excluded:
                continue

            client.send_message(message)

        # shows message on the server if the server is listening
        if self._server_listening:
            print(message)

        self.chat_log.append(message)  # record message

    def send_to_participant(self, participant_name: str, message: str):
        """send message to client connected to the chatroom"""
        for client in self._clients:
            if client.name == participant_name:
                # send private message to the selected client. Private messages are not recorded by the server!
                client.client_socket.send(message)
                break

    # ------------------
    # participant handling
    # ------------------

    def add_participant(self, client: Client):
        """adds client to chatroom"""
        self._clients.append(client)

        msg = f'{client.name} joined to the Chatroom!'
        self.broadcast(msg)

    def remove_participant(self, client_uuid: int) -> Client or None:
        """remove client from chatroom and returns it, if client did not exist return None"""
        for clients in self._clients:
            if clients.user_ID == client_uuid:
                client = clients
                break
        else:
            return None  # if no client found

        msg = f'<{datetime.now()}> {client.name} left to the Chatroom!'
        self.broadcast(msg, excluded=[client.user_ID])

        return client

    def get_participants(self):
        """returns all participants as string"""
        print(f'Chatroom: {self.name}')
        for client in self._clients:
            msg = f'Client: {client.name} from: {client.address}'
            print(msg)
