import socket
import client_handler
from database import *
from encryption import *


class Server(object):
    """The server class is responsible for exchanging encryption keys with the client,
     sending communications ports, and creating the thread for each client that connects. """

    def __init__(self):
        self.sock = socket.socket()
        self.port = 8077
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(100)
        self.rsa = None
        self.aes = None
        self.message = ""

    def receive_decrypted_message_tcp(self, buffer_size, client_socket):
        """receive a message"""
        message = client_socket.recv(buffer_size)
        return self.aes.decrypt_aes(message)

    def send_encrypted_message_tcp(self, message, client_socket):
        """send a message"""
        self.message = client_socket.encrypt_aes(message)
        client_socket.send(self.message)

    def encryption_exchange_keys(self, client_socket):
        """
        exchange encryption keys with the client
        :param client_socket:
        :return:
        """
        self.rsa.create_private_key()
        self.rsa.create_public_key()
        client_socket.send(self.rsa.get_public_key())
        msg = client_socket.recv(1024)
        self.aes.set_key(self.rsa.decode(msg))


def main():
    """server main - handle the connection with the client and start a client handler thread when client is accept"""
    server = Server()  # create server object
    v_port = 20001
    a_port = 20002
    zmq_port = 20003
    database = Database()  # create database
    while True:
        client_socket, address = server.sock.accept()  # accept the client who connect
        server.rsa = RSACrypt()
        server.aes = AESEncryption()
        server.encryption_exchange_keys(client_socket)  # exchange encryption keys with the client
        msg = str(v_port) + "*" + str(a_port) + "*" + str(zmq_port)
        client_socket.send(msg.encode())  # sending communications ports for connection with the client handler
        msg = client_socket.recv(1024).decode()
        if msg == "first":
            first_time = True
        else:
            first_time = False
        client_hand = client_handler.ClientHandler(client_socket, v_port, a_port, zmq_port, database, server.aes,
                                                   first_time)
        client_hand.start()  # starts the client handler thread
        v_port += 3
        a_port += 3
        zmq_port += 3


if __name__ == "__main__":
    main()
