from socket import socket
from typing import Tuple


class Player:
    def __init__(self, name: str, client: socket, address: Tuple[str, int]):
        self.name = name
        self.client = client
        self.address = address

        self.total = 0
        self.score = 0
        self.answer = None

    def __str__(self):
        return self.name

    def send(self, message: str) -> None:
        """
        Send a message to the client
        :param message:
        :return: None
        """
        self.client.send(message.encode())

    def receive(self) -> str:
        """
        Receive a message from the client
        :return: received message
        """
        return self.client.recv(1024).decode()

    def close(self) -> None:
        """
        Close the connection with the client
        :return: None
        """
        self.client.close()