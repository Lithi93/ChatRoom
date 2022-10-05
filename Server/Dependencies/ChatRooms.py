import socket
import threading
import time
from datetime import datetime

from Dependencies.ServerSideUser import Client


class ChatRoom:
    def __init__(self, name: str):
        self.name: str = name  # name of the chatroom
        self._clients: list[Client] = []  # connected clients in the chatroom
        self.chat_log: list[str] = []  # contains all messages sent in the chatroom
        self.server_listening = False  # set to True to start listening this room

        # while chatroom is active be ready to receive messages
        self.active = True
        self.incoming = threading.Thread(target=self._incoming_messages, daemon=True)
        self.incoming.start()

        # client queries
        self.queries = {
            '\\participants': self.in_the_room,
        }

        # contains forbidden sentences from user that are struck from messages
        self.forbidden = [
            '<ShutDown>;',
            '<SALT>;',
            '<query>;',
        ]

    # ------------------
    # message handling
    # ------------------

    def _incoming_messages(self):
        """checks clients for new messages"""
        while self.active:
            time.sleep(0.001)  # delay for the message update

            new_messages = []  # TODO <- these might be needed to be sorted depending on the timestamp in them
            for client in self._clients:
                messages: list[str] = client.get_message()  # get current message buffer from the client

                if messages:
                    # check if message is a query
                    if self.if_query(messages):
                        self.do_query(client, messages)
                        continue

                    new_messages += messages

            # broadcast all new messages
            for msg in new_messages:
                self.broadcast(msg)

    def broadcast(self, message: str, excluded=None):
        """broadcasts messages in the room"""

        # if excluded user
        if excluded is None:
            excluded = []

        # if forbidden message in message don't send it.
        # TODO this is a for attack that user might use, sentences in forbidden are used to control / inform client side of the code.
        for f in self.forbidden:
            if f in message:
                return

        # broadcast message to all users in the chatroom
        for client in self._clients:
            # skip client that are excluded
            if client.user_ID in excluded:
                continue

            if client.handle_thread.is_alive():
                client.send_message(message)

        # shows message on the server if the server is listening
        if self.server_listening:
            print(message)

        self.chat_log.append(message)  # record message

    def send_to_participant(self, participant_name: str, message: str):
        """send message to client connected to the chatroom"""
        for client in self._clients:
            if client.name == participant_name:
                # send private message to the selected client. Private messages are not recorded by the server!
                client.client_socket.send(message)
                break

    # ----------------
    # client queries
    # ----------------

    @classmethod
    def if_query(cls, message: list) -> bool:
        """checks if sent message is query"""
        _, query = message[0].split(';', 1)
        if '\\' == query.strip()[0]:
            return True
        return False

    def do_query(self, client: Client, message: list):
        """does query and sends it to the client"""
        _, query = message[0].split(';', 1)
        query = query.strip()

        # check if query exists
        if query in self.queries.keys():
            method = self.queries[query]
            method(client)  # query always take in client!!
        else:
            client.send_message('Server: no such query exist!')

    def in_the_room(self, client: Client):
        """send user all client names in the current chatroom"""
        client_names = [client.name for client in self._clients]
        client.send_message(f'<query>; <names>; {client_names}')  # <query>; <type>; data

    # ------------------
    # participant handling
    # ------------------

    def add_participant(self, client: Client):
        """adds client to chatroom"""
        self._clients.append(client)

        msg = f'{client.name} joined to the Chatroom "{self.name}"!'
        self.broadcast(msg)

        # send new participant list to all clients
        for client in self._clients:
            self.in_the_room(client)

    def remove_participant(self, client_uuid: int, info=True) -> Client or None:
        """
        remove client from chatroom and returns it, if client did not exist return None.
        :param client_uuid: int, clients ID
        :param info: bool, default True. Informs chatroom if someone left the room.
        """

        for i in range(len(self._clients)):
            client = self._clients[i]
            if client.user_ID == client_uuid:
                found_client = self._clients.pop(i)
                break
        else:
            return None  # if no client found

        if info:
            # inform other users in the chatroom that this user has left the room
            msg = f'<{datetime.now()}> {found_client.name} left to the Chatroom!'
            self.broadcast(msg, excluded=[found_client.user_ID])

        # send new participant list to all clients
        for client in self._clients:
            self.in_the_room(client)

        return found_client

    def get_participant_uuid(self):
        """returns all participant uuids"""
        return [client.user_ID for client in self._clients]

    def get_clients(self):
        """returns client_objects in the chatroom"""
        return self._clients

    def get_participants_details(self):
        """returns all participants as string"""
        print(f'Chatroom: {self.name}')
        for client in self._clients:
            msg = f'Client: {client.name} from: {client.address}'
            print(msg)
