from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode
import pickle
import os


# Your input has to fit into a block of BLOCK_SIZE.
# To make sure the last block to encrypt fits in the block, you may need to pad the input.
# This padding must later be removed after decryption so a standard padding would help.
# The idea is to separate the padding into two concerns: interrupt and then pad.
# First you insert an interrupt character and then a padding character.
# On decryption, first you remove the padding character until you reach the interrupt character
# and then you remove the interrupt character


class RSACrypt:

    def __init__(self):
        self.private_key = ""  # Private key
        self.public_key = ""  # Public key
        self.key_length = 1024

    # ------------------------------------FUNCTIONS-------------------------------------------
    def create_private_key(self):
        """ Create and return private key. """
        self.private_key = RSA.generate(self.key_length)

    def create_public_key(self):
        """ Create public key using the private key. """
        if str(self.private_key) == "":
            self.create_private_key()
        self.public_key = self.private_key.publickey()

    def get_public_key(self):
        """ Return string of public key. """
        return self.pack(self.public_key)

    def encrypt(self, data):
        """ Receive data object , return encrypted data. """
        pack_data = self.pack(data)
        return self.public_key.encrypt(pack_data, 32)[0]  # Encrypt data using the public key.

    def decode(self, data):
        decrypt_data = self.private_key.decrypt(data)  # Decrypt data using private key.
        return self.unpack(decrypt_data)

    @staticmethod
    def unpack(data):
        """Receive base64 of pickled data, return original data. """
        return pickle.loads(b64decode(data))

    @staticmethod
    def pack(data):
        """ Receive data, return base64 of pickled data"""
        return b64encode(pickle.dumps(data))


class AESEncryption(object):

    def __init__(self):
        self.key = ''
        self.interrupt = '\u0001'
        self.pad = '\u0000'
        self.block_size = 16  # Define the block size (as AES is a block cipher encryption algorithm).

    def create_key(self):
        self.key = os.urandom(16)

    def set_key(self, key):
        self.key = key

    def add_padding(self, data):
        """ Pad data before encryption (with pad and interrupt). """
        new_data = data + self.interrupt
        new_data_len = len(new_data)
        remaining_len = self.block_size - new_data_len
        to_pad_len = remaining_len % self.block_size
        pad_string = self.pad * to_pad_len
        return new_data + pad_string

    def strip_padding(self, data):
        """ Strip data after decryption (with pad and interrupt). """
        return data.decode().rstrip(self.pad).rstrip(self.interrupt)

    def decrypt_with_aes(self, decrypt_cipher, encrypted_data):
        """ Decrypt the given encrypted data with the decryption cipher. """
        decoded_encrypted_data = b64decode(encrypted_data)
        decrypted_data = decrypt_cipher.decrypt(decoded_encrypted_data)
        return self.strip_padding(decrypted_data)

    def encrypt_with_aes(self, encrypt_cipher, plaintext_data):
        """ Encrypt the given data with the encryption cipher. """
        plaintext_padded = self.add_padding(plaintext_data)
        encrypted = encrypt_cipher.encrypt(plaintext_padded)
        return b64encode(encrypted)

    def encrypt_aes(self, data_to_encrypt):
        encryption_cipher = AES.new(self.key)  # Encryption & decryption cipher objects
        encrypted_data = self.encrypt_with_aes(encryption_cipher, data_to_encrypt)  # Encrypt data
        return encrypted_data

    def decrypt_aes(self, encrypted_data):
        try:
            decryption_cypher = AES.new(self.key)
            #  And let's decrypt our data
            decrypted_data = self.decrypt_with_aes(decryption_cypher, encrypted_data)
            return decrypted_data

        # Catch any general exception
        except Exception as err:
            print("error")
            return None
