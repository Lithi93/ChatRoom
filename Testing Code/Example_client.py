import socket
import threading
from datetime import datetime

"""
source for the example: https://www.neuralnine.com/tcp-chat-in-python/
"""


# Listening to Server and Sending Nickname
def receive():
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occurred!")
            client.close()
            break


# Sending Messages To Server
def write():
    exit_condition: tuple = ("exit", "close")

    while True:
        m = input()

        if m in exit_condition:
            break

        message = f'<{datetime.now().time().strftime("%H:%M:%S")}>[{nickname}]; {m}'
        client.send(message.encode('utf-8'))


if __name__ == '__main__':
    # Choosing Nickname
    nickname = input("Choose your nickname: ")

    # Connecting To Server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('127.0.0.1', 55555))
    except ConnectionRefusedError:
        print('\n> NOTICE: connection refused, server might not be ON or IP address was not correct.')
    else:
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=receive, daemon=True)
        receive_thread.start()

        write()  # start write loop

        # write_thread = threading.Thread(target=write)
        # write_thread.start()

