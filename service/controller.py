from typing import Tuple, Dict, List, Union, Any
from socket import socket, AF_INET, SOCK_STREAM, timeout
from json import dumps
from threading import Thread
import random

from player_model import Player


class ServiceController:
    def __init__(self, port: int, question_count: int):
        """
        Initialize the service controller
        :param port: Port to listen
        :param question_count: number of questions to ask
        """
        # set global variables
        self.server: Union[socket, None] = None
        self.port: int = port
        self.total_question_count: int = question_count
        self.asked_question_count: int = 0

        # set players and questions dictionary
        self.players: List[str: Player] = {}
        self.questions: Dict[str: int] = {}

        self._is_terminated = False  # set is_terminated to True to terminate the game
        self._is_started = False  # set is_started to True to start the game

    def connect(self) -> None:
        """
        Connect to server
        :return: None
        """
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('localhost', self.port))
        self.server.listen(5)
        print('Server is listening')

    def close(self) -> None:
        """
        Close server
        :return: None
        """
        self.server.close()
        print('Server closed')

    def wait_clients(self, layout) -> bool:
        """
        Wait for clients to connect
        :param layout: layout of the game
        :return: True if clients connected, False otherwise
        """

        layout.add_log('Waiting for clients to connect...')

        try:
            # set timeout for server
            self.server.settimeout(1)

            # wait for clients to connect
            while not self._is_started:

                # check if server stop waiting for clients
                try:
                    client, address = self.server.accept()
                except timeout:
                    continue

                name = client.recv(1024).decode()

                # send message to client if name is empty
                if name == '':
                    layout.add_log(f'Client {address} connected with empty name')
                    client.send('Name cannot be empty'.encode())
                    client.close()
                    continue

                # send message to client if name is already taken
                if name in self.players:
                    layout.add_log(f'Client {address} connected with taken name')
                    client.send('Name already exists'.encode())
                    client.close()
                    continue

                # add client to players dictionary
                player = Player(name=name, client=client, address=address)
                self.players[name] = player

                # send message to client
                player.send('Connected')

                layout.add_log(f'Client {address} connected with name {name}')

            # remove timeout from server
            self.server.settimeout(None)
            return True

        except Exception as e:
            print(e)
            self.server.close()
            return False

    def read_questions(self) -> None:
        """
        Read questions from file
        :return: None
        """
        with open('questions.txt', 'r') as file:
            # read question and answer from file line by line and add them to questions dictionary
            lines = file.readlines()
            for line in range(0, len(lines), 2):
                self.questions[lines[line].strip()] = int(lines[line + 1].strip())

        file.close()  # close file

    def select_question(self) -> Tuple[str, int]:
        """
        Select question randomly
        :return: question and answer
        """
        # add questions if questions dictionary is empty
        if not self.questions:
            self.read_questions()

        # select question randomly
        question = random.choice(list(self.questions.keys()))
        answer = self.questions[question]

        # remove question from questions dictionary
        self.questions.pop(question)

        return question, answer

    def send_message_to_clients(self, message: str) -> None:
        """
        Send message to clients in the same time
        :param message: message to send
        :return: None
        """
        # send question to clients
        for player in self.players:
            self.players[player].send(message)

    def wait_for_answer_from_clients(self) -> None:
        """
        Wait for answer from clients
        :return: None
        """
        # create threads for clients
        threads = []
        for player in self.players:
            thread = Thread(target=self.wait_for_answer_from_client, args=(self.players[player],))
            thread.start()
            threads.append(thread)

        # wait for threads to finish
        for thread in threads:
            thread.join()

    @staticmethod
    def wait_for_answer_from_client(player: Player) -> None:
        """
        Wait for answer from client
        :param player: player object
        :return: None
        """
        # receive answer from client
        while True:
            response = player.receive()
            if response != '':
                player.answer = int(response)
                return

    def compare_answers(self, layout, answer: int) -> None:
        """
        Compare answers select winner player who choose the closest answer
        :param answer: correct answer
        :return: None
        """
        winner: List[Player] = []

        for player in self.players:
            self.players[player].score = 0  # delete previous score

            # select winner player(s)
            if not winner:
                winner.append(self.players[player])
            elif abs(self.players[player].answer - answer) < abs(winner[0].answer - answer):
                winner = [self.players[player]]
            elif abs(self.players[player].answer - answer) == abs(winner[0].answer - answer):
                winner.append(self.players[player])
            else:
                pass

        # add score to winner player
        for player in winner:
            player.score = 1 / len(winner)
            player.total += player.score

            log_text = f'{player.name} answered {player.answer} and got {player.score} point(s)'
            layout.add_log(log_text)

    def send_results_to_clients(self, answer: int) -> None:
        """
        Send results to clients
        :param answer: correct answer
        :return: None
        """

        # increase asked question count
        self.increase_asked_question_count()

        # sort players by total score
        self.sort_players()

        # send results to clients
        for player in self.players:
            # create result message
            response: Dict[str: Any] = {}

            # set result message for player
            if self.players[player].score == 1:
                response["message"] = f'You won this round with {self.players[player].answer}.'
            elif self.players[player].score > 0:
                response["message"] = f'You tied with {self.players[player].answer}.'
            else:
                response["message"] = f'You lost this round with {self.players[player].answer}.'

            # set correct answer and total scores for player
            response["scores"] = {player: self.players[player].total for player in self.players}
            response["answer"] = answer
            response["is_end"] = self.asked_question_count == self.total_question_count

            # send result message to player
            self.players[player].send(dumps(response))

        # close sockets if asked question count is equal to total question count
        if self.asked_question_count == self.total_question_count:
            self.server.close()

    def sort_players(self) -> None:
        """
        Sort players by total score
        :return: None
        """
        sorted(self.players, key=lambda player: self.players[player].total, reverse=True)

    def increase_asked_question_count(self) -> None:
        """
        Increase asked question count
        :return: None
        """
        self.asked_question_count += 1
