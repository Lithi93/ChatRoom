import socket

# MyLibs
from Dependencies.ChatServer import ChatRoomServer


class TerminalUI:
    # class permanent immutable variables here!

    def __init__(self):
        # Class object instance variables here!

        self.local_host = True
        self.port = 55555

        self.commands: dict = {  # Example //// "command call name": (func(), "description"),
            "?": (self.get_commands, "Displays all commands"),
            "start": (self.start_server, "Starts the server"),
            "stop": (self.stop_server, "Stops the server"),
            "clients": (self.show_connected_clients, "Shows all connected clients"),
            "kick": (self.kick_client, "Kick client from the server"),
            "new room": (self.create_chatroom, "Creates new chatroom to server"),
            "remove room": (self.remove_chatroom, "Removes chatroom from server"),
            "listen room": (self.listen_chatroom, "Listen the chatroom in the server"),
            "stop listen": (self.stop_listening, "Stops listening rooms"),
            "close": (None, "Closes application"),
            "exit": (None, "Closes application"),
        }

        self.connected_server: list[ChatRoomServer] = []  # opened servers exists here, we only create one per instance so list in this case is pointless.

    # ----------------------------------------
    # Basic UI functions
    # ----------------------------------------

    def run(self):
        """starts interactive terminal loop"""
        print('--Server Terminal--')
        print('> Type ? to display all available commands')
        while True:
            user_input = input('< ').strip().lower()  # collect users input

            # if command exists in the keys execute it
            if user_input in self.commands.keys():
                f, _ = self.commands[user_input]

                if f is not None:
                    f()  # execute function
                else:
                    # closes application
                    break
            # if empty input given continue
            elif "" == user_input:
                continue
            # remind user with all commands prompt
            else:
                print(f'> Commands "{user_input}" not recognized. Try "?" to get full command list.')

    def get_commands(self):
        """prints outs all commands and their meaning"""
        print("Commands list:")
        for command, items in self.commands.items():
            _, info = items

            print(f'\t{command} - "{info}"')

    def get_server(self, index: int):
        """returns server from the server list, if no servers returns None"""
        try:
            server = self.connected_server[index]
        except IndexError:
            print('> Server was not running!')
            server = None

        return server

    # ----------------------------------------
    # server private functions
    # ----------------------------------------

    # ----------------------------------------
    # command functions
    # ----------------------------------------

    def start_server(self):
        """starts and initializes server"""
        my_port: int = self.port  # port number

        if self.local_host:
            my_ip: str = '127.0.0.1'  # localhost for testing
        else:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            my_ip: str = local_ip  # get local IP automatically

        # create new server
        print(f'server at IP: {my_ip}, Port: {my_port}')
        server = ChatRoomServer(my_ip, my_port)
        self.connected_server.append(server)

    def stop_server(self):
        """stops server"""
        index = 0
        server = self.get_server(index)

        if server is None:
            return

        server.exiting()  # stop server
        self.connected_server.pop(index)  # remove it from references

    def listen_chatroom(self):
        """starts listening chatroom"""
        server = self.get_server(0)

        # print all current chatroom names
        print('Chat-rooms:')
        for name in server.get_chatroom_names():
            print(f'\t{name}')

        while True:
            # get name of the chatroom
            name = str(input('Chatroom name?: ')).strip()

            # return from loop if user selects these
            if name in ['exit', 'close']:
                print('> New chatroom was not created!')
                return

            # confirm name input
            done = str(input(f'Name "{name}" selected. Continue? [Y]: ')).strip().lower()

            # if confirmed break out
            if done == 'y':
                break

        server.listen_room(name)

    def stop_listening(self):
        """stops listening rooms"""
        server = self.get_server(0)
        server.stop_listen()
        print('> Stopped listening rooms!')

    def create_chatroom(self):
        """creates new chatroom to the server"""
        server = self.get_server(0)

        # print all current chatroom names
        print('Chat-rooms:')
        for name in server.get_chatroom_names():
            print(f'\t{name}')

        while True:
            # get name for the new chatroom
            name = str(input('Chatroom name?: ')).strip()

            # return from loop if user selects these
            if name in ['exit', 'close']:
                print('> New chatroom was not created!')
                return

            # check if chatroom names exists
            if name in server.get_chatroom_names():
                print(f'> No chatroom duplicates allowed!')
                continue

            # confirm name input
            done = str(input(f'Chatroom name "{name}". Continue? [Y]: ')).strip().lower()

            # if confirmed break out
            if done == 'y':
                name = f'\\{name}'
                break

        # create new chatroom
        server.create_chatroom(name)
        print(f'> New chatroom "{name}" created!')

    def remove_chatroom(self):
        """remove chatroom from the server"""
        server = self.get_server(0)

        # print all current chatroom names
        print('Chat-rooms:')
        for name in server.get_chatroom_names():
            print(f'\t{name}')

        while True:
            # get name of the chatroom
            name = str(input('Chatroom name?: ')).strip()

            # return from loop if user selects these
            if name in ['exit', 'close']:
                print('> Chatroom was not removed!')
                return

            # check if chatroom names exists
            if name not in server.get_chatroom_names():
                print(f'> No chatroom named "{name}"!')
                continue

            # confirm name input
            done = str(input(f'Chatroom "{name}" selected. Continue? [Y]: ')).strip().lower()

            # if confirmed break out
            if done == 'y':
                break

        server.remove_chatroom(name=name)
        print(f'> Chatroom "{name}" was removed!')

    def kick_client(self):
        """kicks client from server"""
        server = self.get_server(0)
        status = self.show_connected_clients()

        # if no clients do not continue
        if not status:
            return

        try:
            user_id = int(input('User ID <? '))
        except ValueError:
            print('> Only use numbers!')
        else:
            server.remove_client(user_id)

    def show_connected_clients(self) -> bool:
        """shows all currently connected clients"""
        server = self.get_server(0)

        # check if there is servers and if there is connected clients
        if server is None:
            return False
        elif not server.get_clients():
            print('> No connected clients!')
            return False

        # print out all connected clients
        print('Connected clients:')
        for client in server.get_clients():
            print(f'\tName: {client.name}, From: {client.address}, When: {client.since}, Chatroom: {client.current_room}, Status: {client.handle_thread.is_alive()}, client ID: {client.user_ID}')

        return True
