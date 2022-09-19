import socket
import uuid
import threading
from datetime import datetime, timedelta

from typing import TYPE_CHECKING
if TYPE_CHECKING:  # to avoid circular import error
    from Server.Dependencies.ChatRooms import ChatRoom


# field(init=False)

"""
once user is connected to the chatroom by the user action it should send the messages to that chatroom.
"""


class Client:
    def __init__(self, name: str, sock: socket.socket, address: str, chatroom_name: list, change_method):
        self.name: str = name
        self.client_socket: socket.socket = sock
        self.address: str = address
        self.chatroom_names: list = chatroom_name
        self.change_method: () = change_method  # allows us to change chatroom by user command

        self.current_room = ''  # name of the current room
        self.user_ID: int = int(uuid.uuid1())  # generate random ID for the user
        self.since = datetime.now()  # when user connected

        # all client commands
        self._commands = {
            '\\join': self.room_change,
        }

        # contains all messages from client that has not been sent yet
        self._current_buffer = []

        # handel client communication of thread
        self.handle_thread = threading.Thread(target=self._handle, daemon=True)
        self.handle_thread.start()

    # ---------------------
    # Client handle
    # ---------------------

    def get_incoming_msg(self) -> (bytes, str, str):
        """
        returns incoming message
        (Raw, time_sender, message)
        """
        packet = self.client_socket.recv(1024)  # receive message from the user
        time_sender, msg = packet.decode('utf-8').split(';')  # message looks like this <16:44:00>[JV]; lol
        msg = msg.strip()  # remove white space

        return packet, time_sender, msg

    def _handle(self):
        """
        Handles messages from client and sends them to the connected chatroom.
        This method can also change the chatroom on user command
        """
        spam_limit = timedelta(seconds=0.5)
        offence_count = 0
        max_offences = 5

        while True:
            try:
                last_message = datetime.now()
                raw, _, msg = self.get_incoming_msg()
                msg_time = datetime.now()

                # give warning to user
                if offence_count > max_offences:
                    self.send_message('<Server>: Stop spamming you piece of shit!')

                # do not accept empty message
                if not msg:
                    continue

                # if user is spamming messages stop it
                if (msg_time - last_message) < spam_limit:
                    offence_count += 1
                    continue

                # execute client command if detected
                if msg in self._commands.keys():
                    try:
                        f = self._commands[msg]
                    except Exception as e:
                        print(f'Client command caused and issue - {e}')
                    else:
                        f()  # execute client command
                    continue

                offence_count = 0  # reset offences when user stops spamming
                self._message_buffer(raw.decode('utf-8'))
            except:
                # Removing And Closing Clients
                self.client_socket.close()

                msg = f"{self.name} left the chat!".encode('utf-8')
                print(msg)  # shows message on the server
                break

        del self

    # ---------------------
    # Chatroom messaging
    # ---------------------

    def _message_buffer(self, msg: str):
        """handles all messages user send from _handle"""
        self._current_buffer.append(msg)

    def get_message(self):
        """returns whole buffer and empties it"""
        msg = self._current_buffer.copy()
        self._current_buffer.clear()

        return msg

    def send_message(self, msg: str):
        """sends message to this client"""
        self.client_socket.send(msg.encode('utf-8'))

    # ---------------------
    # Client commands
    # ---------------------

    def room_change(self):
        """lets user change chatroom"""

        # send user all available chat rooms
        msg = 'Chatroom:\n'
        for room in self.chatroom_names:
            msg += f'\t{room}'
        self.send_message(msg)

        while True:
            _, _, msg = self.get_incoming_msg()

            # if room is selected change to that room
            if msg in self.chatroom_names:
                self.change_method(self.user_ID, self.current_room, msg)  # user ID, current room name, new room name
                break
            else:
                self.send_message(f'> No "{msg}" chatroom exists!')
