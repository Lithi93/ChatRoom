import socket
import threading

"""
source for the example: https://www.neuralnine.com/tcp-chat-in-python/
"""


# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)


# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message)
            print(message.decode('ascii'))  # shows message on the server
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]

            msg = f"{nickname} left the chat!".encode('ascii')
            broadcast(msg)
            print(msg)  # shows message on the server

            nicknames.remove(nickname)
            break


# Receiving / Listening Function
def receive():
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,), daemon=True)
        thread.start()


if __name__ == '__main__':
    # Connection Data
    host = '127.0.0.1'
    port = 55555

    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    # Lists For Clients and Their Nicknames
    clients = []
    nicknames = []

    print("> Server running!")
    # how to kill thread with flag https://stackoverflow.com/questions/18018033/how-to-stop-a-looping-thread-in-python
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()

    # terminal loop
    while True:
        user_input = input('< ').strip().lower()

        if user_input == "show clients":
            client_count = len(nicknames)

            if not client_count:
                print(f'> No clients!')
                continue

            for i in range(client_count):
                print(f"user name: {nicknames[i]}, client: {clients[i]}")

        elif user_input in ["exit", "close"]:
            break
        elif user_input == "":
            continue
        else:
            print(f'Command {user_input} not recognized!')
