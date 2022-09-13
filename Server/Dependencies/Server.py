import socket
import threading
import time


class ChatRoomServer:
    def __init__(self, host_ip: str, port: int):
        # Connection Data
        self._host = host_ip
        self._port = port

        # Starting Server
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((host_ip, port))
        self._server.listen()

        # Lists for Clients and their Nicknames
        self._clients = []
        self._nicknames = []

        # start listening new connections
        self.receive_thread = threading.Thread(target=self._receive, args=(), daemon=True)
        self.receive_thread.start()

        print('> Server is running!!')

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
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            self._nicknames.append(nickname)
            self._clients.append(client)

            # Print And Broadcast Nickname
            print(f"Nickname is {nickname}")
            self._broadcast(f"{nickname} joined!".encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=self._handle, args=(client,), daemon=True)
            thread.start()

    # Sending Messages To All Connected Clients
    def _broadcast(self, message):
        for client in self._clients:
            client.send(message)

    # Handling Messages From Clients
    def _handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                self._broadcast(message)
                print(message.decode('ascii'))  # shows message on the server
            except:
                # Removing And Closing Clients
                index = self._clients.index(client)
                self._clients.remove(client)
                client.close()
                nickname = self._nicknames[index]

                msg = f"{nickname} left the chat!".encode('ascii')
                self._broadcast(msg)
                print(msg)  # shows message on the server

                self._nicknames.remove(nickname)
                break

    def get_client_names(self):
        """returns all connected client names"""
        return self._nicknames

    def exiting(self):
        # stop receiving new clients
        self.receive_thread.do_run = False

        # shutdown all client connections
        for client in self._clients:
            client.close()

        # close server
        self._server.close()
        print(f'> Server {self._host} at port: {self._port}. Shutdown!')

        del self
