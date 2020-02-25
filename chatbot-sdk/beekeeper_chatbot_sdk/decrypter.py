from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes

IV = '0123456789012345'.encode('utf-8')


class Decrypter:
    def __init__(self, key):
        self.key = key
        self.cipher = Cipher(algorithms.AES(self.key), mode=modes.CBC(IV), backend=default_backend())
        self.padding = padding.PKCS7(algorithms.AES.block_size)

    def decrypt(self, message):
        decryptor = self.cipher.decryptor()
        unpadder = self.padding.unpadder()
        return unpadder.update(decryptor.update(message) + decryptor.finalize()) + unpadder.finalize()


