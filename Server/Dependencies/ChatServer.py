import socket
import threading
import time

from Dependencies.ServerSideUser import Client
from Dependencies.ChatRooms import ChatRoom
from Dependencies.UserLogin import Login


class ChatRoomServer:
    def __init__(self, host_ip: str, port: int):
        # Connection Data
        self._host = host_ip
        self._port = port

        # Starting Server
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((host_ip, port))
        self._server.listen()

        self._clients: list[Client] = []  # contains client objects
        self._chatrooms: dict[str:ChatRoom] = {}  # contains chatroom objects {chatroom_name: chatroom_object}
        self._room_names: list = []  # all the chatroom names

        # initialize login object. Handles all login event and creating new accounts
        self.login = Login()

        # start listening new connections
        self.receive_thread = threading.Thread(target=self._receive, args=(), daemon=True)
        self.receive_thread.start()

        # check
        self.check_interval = 5  # seconds
        self.status_thread = threading.Thread(target=self._client_status, args=(self.check_interval, ), daemon=True)
        self.status_thread.start()

        self.create_chatroom('Default')  # create default chatroom
        self.create_chatroom('Default2')  # create default2 chatroom

        print('> Server is running!!')

    # ------------------------------
    # server control
    # ------------------------------

    def exiting(self):
        # stop receiving new clients
        self.receive_thread.do_run = False

        # shutdown all client connections
        for client_object in self._clients:
            client_object.client_socket.close()

        # close server
        self._server.close()
        print(f'> Server {self._host} at port: {self._port}. Shutdown!')

        del self

    def _client_status(self, interval: int):
        """checks if client is alive or not and removes it if it's not alive"""
        t = threading.current_thread()
        while getattr(t, "do_run", True):
            time.sleep(interval)  # check interval

            for i in range(len(self._clients)):
                try:
                    client = self._clients[i]  # get client
                except IndexError:
                    print('NOTICE: Index error while checking if client was alive')
                    break

                # if client is not alive remove it
                if not client.handle_thread.is_alive():

                    # check if client is in chatroom and remove it from there
                    for name, chatroom in self._chatrooms.items():
                        chatroom.remove_participant(client.user_ID)

                    # remove user from server
                    self._clients.pop(i)

    def listen_room(self, name: str):
        """starts listening selected chatroom"""
        chatroom = self._chatrooms[name]
        chatroom.server_listening = True  # start listening

        # turn off other chatroom listening
        for room in self._chatrooms.values():
            # skip room that server is just now starting to listen
            if room.name == chatroom.name:
                continue

            room.server_listening = False  # stop listening

        print(f'> Server is now listening room {chatroom.name}')

    def stop_listen(self):
        """stops listening rooms"""
        for room in self._chatrooms.values():
            room.server_listening = False  # stop listening

    # ------------------------------
    # chatroom control
    # ------------------------------

    def get_chatrooms(self):
        """returns all chatroom names in the server, and displays them along with user in the rooms"""
        print(f'Server: {self._host}, port: {self._port} Chatrooms:')
        for name, chatroom in self._chatrooms.items():
            chatroom.get_participants_details()

    def get_chatroom_names(self):
        """returns chatroom names"""
        return list(self._chatrooms.keys())

    def create_chatroom(self, name: str):
        """makes chatroom to server"""
        chatroom = ChatRoom(name)
        self._chatrooms[name] = chatroom
        self._room_names.append(name)

    def remove_chatroom(self, name: str):
        """removes chatroom and returns all the client in it to lobby"""

        # get and remove instances of the chatroom
        chatroom = self._chatrooms.pop(name)
        self._room_names.remove(chatroom.name)

        # remove all client from the chatroom and inform that they have been moved to lobby
        participant_uuid = chatroom.get_participant_uuid()
        for id in participant_uuid:
            client = chatroom.remove_participant(id, info=False)  # do not info client that other clients left the room
            client.current_room = ''  # is user is forcible remove default the current room
            client.send_message(f'<server>: Chatroom "{chatroom.name}" was closed, you have been returned to the lobby.')  # inform user that he has been moved to the lobby

    def join_chatroom(self, client_uuid: int, old_room: str, new_room: str):
        """lets client change / join to available chatroom"""

        # find client chatroom that needs to be changed if old_room is not ''
        # remove client from old room and broadcast that client has left the room.
        if old_room:
            old_chatroom: ChatRoom = self._chatrooms[old_room]
            client = old_chatroom.remove_participant(client_uuid)
        else:
            client = [client for client in self._clients if client_uuid == client.user_ID]  # gets client with uuid, should only return one client

            # This part should never happen, but I added this here so inform if it would happen
            if len(client) >= 2:
                print(f'CRITICAL ERROR: two of the same user UUID was found! {[c.user_ID for c in client]}')
                return

            client = client[0]  # get the client out of the list

        # add client to new room and broadcast "client has entered to the room"
        new_chatroom: ChatRoom = self._chatrooms[new_room]
        client.current_room = new_chatroom.name  # user is currently in this room
        new_chatroom.add_participant(client)

    # ------------------------------
    # client control
    # ------------------------------

    # Receive new client
    def _receive(self):
        t = threading.current_thread()
        while getattr(t, "do_run", True):

            # Accept Connection
            try:
                client, address = self._server.accept()
            except Exception as e:
                continue

            print(f"Connected with {address}")

            # Request And Store Nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            # only accept one of all each nickname
            other_names = [client.name for client in self._clients]
            if nickname in other_names:
                client.send('NOTICE: User name already taken.'.encode('utf-8'))
                client.close()
                continue

            # TODO login user or create new one
            # self.login.setup_user()

            # create client object and append it to the clients list
            client_object = Client(nickname, client, address, self._room_names, self.join_chatroom)  # chatroom list is shared with all clients!
            self._clients.append(client_object)

            # display nickname to server and send user conformation that server connection has been made
            print(f"Nickname is {nickname}")
            client_object.send_message('Connected to server!\nWelcome to the lobby. You can see all the commands with \\? command')

    def get_clients(self):
        """returns all connected clients"""
        return self._clients

    def remove_client(self, user_id: int):
        """removes user from the server"""
        for i in range(len(self._clients)):
            client = self._clients[i]
            if client.user_ID == user_id:
                client.send_message('You have been kicked from the server!')
                time.sleep(1)  # wait second

                client.client_socket.close()  # close client connection

                # check if client is in chatroom and remove it from there
                for name, chatroom in self._chatrooms.items():
                    chatroom.remove_participant(client.user_ID)

                # remove user from server
                self._clients.pop(i)
