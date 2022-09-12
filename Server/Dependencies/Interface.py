

class TerminalUI:
    # class permanent immutable variables here!

    def __init__(self):
        # Class object intense variables here!

        self.commands: dict = {  # Example //// "command call name": (func(), "description"),
            "?": (self.get_commands, "Displays all commands"),
            "start": (self.start_server, "Starts the server"),
            "close": (None, "Closes application"),
            "exit": (None, "Closes application"),
        }

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

    # ----------------------------------------
    # server private functions
    # ----------------------------------------

    # ----------------------------------------
    # command functions
    # ----------------------------------------

    def start_server(self):
        """starts and initializes server"""
        pass

    def stop_server(self):
        """stops server"""
        pass

    def show_connected_clients(self):
        """shows all currently connected clients"""
        pass

