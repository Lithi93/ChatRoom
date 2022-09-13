
# MyLibs
from Server.Dependencies.Server import ChatRoomServer


class TerminalUI:
    # class permanent immutable variables here!

    def __init__(self):
        # Class object intense variables here!

        self.commands: dict = {  # Example //// "command call name": (func(), "description"),
            "?": (self.get_commands, "Displays all commands"),
            "start": (self.start_server, "Starts the server"),
            "stop": (self.stop_server, "Stops the server"),
            "clients": (self.show_connected_clients, "Shows all connected clients"),
            "close": (None, "Closes application"),
            "exit": (None, "Closes application"),
        }

        self.connected_server: list[ChatRoomServer] = []  # opened server exists here

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

            # TODO make so that command and info part are straight in their columns
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
        server = ChatRoomServer('127.0.0.1', 55555)
        self.connected_server.append(server)

    def stop_server(self):
        """stops server"""
        index = 0
        server = self.get_server(index)

        if server is None:
            return

        server.exiting()  # stop server
        self.connected_server.pop(index)  # remove it from references

    def show_connected_clients(self):
        """shows all currently connected clients"""
        server = self.get_server(0)

        # check if there is servers and if there is connected clients
        if server is None:
            return
        elif not server.get_client_names():
            print('> No connected clients!')
            return

        # print out all connected clients
        print('Connected clients:')
        for client_name in server.get_client_names():
            print(f'\t{client_name}')
