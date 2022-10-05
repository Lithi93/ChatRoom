from cryptography.fernet import Fernet
from hashlib import scrypt
from os import urandom
from base64 import urlsafe_b64encode


def encrypt_msg(msg: str, fernet: Fernet):
    """encrypts message"""
    return fernet.encrypt(msg.encode())


def decrypt_msg(msg: bytes, fernet: Fernet):
    """encrypts message"""
    return fernet.decrypt(msg).decode()


def generate_key(password: str) -> Fernet:
    """generates key for encryption and decryption"""

    # salt = urandom(16)
    salt = b'123123123123'
    key = scrypt(password.encode('utf-8'), salt=salt, n=16384, r=8, p=1, dklen=32)
    key_encoded = urlsafe_b64encode(key)

    print('password: ', password)
    print('password key: ', key)
    print('password key encoded: ', key_encoded)

    # Instance the Fernet class with the key
    fernet = Fernet(key_encoded)

    return fernet


if __name__ == '__main__':
    message = ['messages', 'are', 'here']
    encrypt_messages = [b'gAAAAABjPY1mQTG_Bte8DWfeBYuIfp9VzqGw1CLj0nBsBhRJWNY48j_8UzUHtmpRoM9VHj56FxOFT4DMjKlDUgwygcLTf9zCvQ==',
                        b'gAAAAABjPY1mP0B4RIitBnWq9EK34YdAMwKN5XjyEMTnYBP0hAwPuE03BHZmkCmdFxjLinUnStz9whzwFEEXeU49hv5glLSZzw==',
                        b'gAAAAABjPY1mO3uUH7_YcXagCT9K_4fW53l6j7B-HPk_5HpUy4t8IAuw0WErcioKtICbOAfp3wArx9U_DdqULP1jP5duG1LlSg==']

    p = 'xxxx'

    fernet = generate_key(p)

    for msg in encrypt_messages:
        # encrypted_msg = encrypt_msg(msg, fernet)
        decrypted_msg = decrypt_msg(msg, fernet)

        print(f'\nOriginal msg: {msg}')
        # print(f'Encrypted msg: {encrypted_msg}')
        print(f'Decrypted msg: {decrypted_msg}')
