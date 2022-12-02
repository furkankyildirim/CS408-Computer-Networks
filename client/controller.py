import json
from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple, Dict, List, Union, Any


class ClientController:
    def __init__(self, host: str, port: int, name: str) -> None:
        """
        Initialize client controller
        :param host: Host to connect
        :param port: port number
        :param name: name of client
        """
        self.server: Union[socket, None] = None
        self.host: str = host
        self.port: int = port
        self.name: str = name

    def connect(self) -> str:
        """
        Connect to server
        :return: True if connected, False otherwise
        """
        try:
            self.server = socket(AF_INET, SOCK_STREAM)
            self.server.connect((self.host, self.port))

            # send name to server
            self.server.send(self.name.encode())

            # receive message from server
            message = self.server.recv(1024).decode()

            # if message is connected then return
            return message

        except Exception as e:
            if type(e) == ConnectionRefusedError:  # if connection refused
                return 'Connection refused'
            elif type(e) == TimeoutError:          # if connection timeout
                return 'Connection timeout'
            else:
                return 'Unknown error'

    def close(self) -> None:
        """
        Close server
        :return: None
        """
        self.server.close()

    def receive_message(self) -> str:
        """
        Receive message from server
        :return: message
        """
        return self.server.recv(1024).decode()

    def send_message(self, message: str) -> None:
        """
        Send message to server
        :param message: message
        :return: None
        """
        self.server.send(message.encode())

    @property
    def is_connected(self):
        """
        Check connection
        :return: True if connected, False otherwise
        """
        try:
            self.server.send(''.encode())
            return True
        except Exception:
            print('Disconnected')
            return False
