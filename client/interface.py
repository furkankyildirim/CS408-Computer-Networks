import json
from threading import Thread
from tkinter import Tk, Label, Entry, Button, messagebox, Text
from typing import Union, Dict, Any

from controller import ClientController


class ClientInterface:
    def __init__(self):
        self.controller: Union[ClientController, None] = None

        self.root = Tk()
        self.root.title("Quiz Game Client")
        self.root.geometry("600x400")

        self.root.resizable(False, False)
        self.log_count = 1
        self.is_end = False
        self.start_client_layout()

        self.root.mainloop()
        self.connection_thread.join()
        print("Client closed")
        self.game_thread.join()
        self.controller.close()

    def start_client_layout(self) -> None:
        """
        Set start client layout
        :return:
        """
        # write welcome message
        welcome_message = Label(self.root, text="Welcome to the Quiz Game Client", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.25, anchor="center")

        # get host and port number from user under the welcome message
        host_label = Label(self.root, text="Host Address:", font=("Arial", 12))
        host_label.place(relx=0.25, rely=0.4, anchor="center")

        self.host_entry = Entry(self.root, width=38)
        self.host_entry.insert(0, "localhost")
        self.host_entry.place(relx=0.65, rely=0.4, anchor="center")

        port_number_label = Label(self.root, text="Port Number: ", font=("Arial", 12))
        port_number_label.place(relx=0.25, rely=0.5, anchor="center")

        self.port_number_entry = Entry(self.root, width=38)
        self.port_number_entry.insert(0, "5000")
        self.port_number_entry.place(relx=0.65, rely=0.5, anchor="center")

        self.name_label = Label(self.root, text="Name:", font=("Arial", 12))
        self.name_label.place(relx=0.25, rely=0.6, anchor="e")

        self.name_entry = Entry(self.root, width=38)
        self.name_entry.place(relx=0.65, rely=0.6, anchor="center")

        # start client button
        self.start_client_button = Button(self.root, text="Start Client", font=("Arial", 12),
                                          command=self.start_client)
        self.start_client_button.place(relx=0.5, rely=0.8, anchor="center")

    def start_client(self):
        """
        Start client after button clicked
        :return:
        """
        # add loading image under the start button
        loading_image = Label(self.root, text="Loading...", font=("Arial", 12))
        loading_image.place(relx=0.5, rely=0.9, anchor="center")

        # lock the start client button
        self.start_client_button.config(state="disabled")

        try:
            # get host and port number from user
            self.host = self.host_entry.get()
            self.port = int(self.port_number_entry.get())
            self.name = self.name_entry.get()

            # create controller and start client
            self.controller = ClientController(self.host, self.port, self.name)
            message = self.controller.connect()

            # raise error if connection failed
            if message != "Connected":
                messagebox.showerror("Error", message)
                loading_image.destroy()
                self.start_client_button.config(state="normal")
                self.host_entry.delete(0, "end")
                self.port_number_entry.delete(0, "end")
                self.name_entry.delete(0, "end")
                return

        except ValueError:
            # if port number is not integer
            messagebox.showerror("Error", "Port number must be integer")
            loading_image.destroy()
            self.start_client_button.config(state="normal")
            self.host_entry.delete(0, "end")
            self.port_number_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            return

        except Exception as e:
            # if any other error occurred
            messagebox.showerror("Error", e.args[0])
            loading_image.destroy()
            self.start_client_button.config(state="normal")
            self.host_entry.delete(0, "end")
            self.port_number_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            return

        # remove all widgets from the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # set client layout
        self.client_layout()

    def client_layout(self):
        # set geometry
        self.root.geometry("750x500")

        # write welcome message
        welcome_message = Label(self.root, text="Quiz Game Player", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.15, anchor="center")

        # set rich text box for see logs
        scores_label = Label(self.root, text="Scores:")
        scores_label.place(relx=0.375, rely=0.1975, relwidth=0.4)

        self.scores = Text(self.root, width=80, height=20)
        self.scores.place(relx=0.55, rely=0.25, relwidth=0.4, relheight=0.5)

        self.scores.insert('end', f'Scores will be shown after the first question is answered')
        self.scores.config(state='disabled')

        # show waiting other players message
        self.waiting_message = Label(self.root, text="Waiting for other players", font=("Arial", 12))
        self.waiting_message.place(relx=0.275, rely=0.5, anchor="center")

        # start game
        self.game_thread = Thread(target=self.game)
        self.game_thread.start()

    def game(self):
        """
        Start game
        :return:
        """

        # check server status
        self.connection_thread = Thread(target=self.check_connection)
        self.connection_thread.start()

        # start game
        while not self.controller.is_terminated:

            self.waiting_message.config(text="Waiting for other players enter the game")
            is_start = self.controller.receive_message()

            if is_start == "start":
                # remove waiting message and set question layout
                self.scores.config(state='normal')
                self.scores.delete('1.0', 'end')
                self.scores.insert('end', f'Scores will be shown after the first question is answered')
                self.scores.config(state='disabled')

                self.waiting_message.config(text="")
                self.question_label = Label(self.root)
                self.question_label.place(relx=0.25, rely=0.1975, anchor="center")

                self.answer_entry = Entry(self.root, width=38)
                self.answer_entry.place(relx=0.25, rely=0.25, anchor="center")

                self.answer_button = Button(self.root, text="Answer", command=self.send_answer)
                self.answer_button.place(relx=0.275, rely=0.4, anchor="center")

                self.is_end = False
                question_count = 1

                while not self.is_end:
                    # get question from server
                    question = self.controller.receive_message()

                    # set waiting message
                    self.waiting_message.config(text="")

                    # set question
                    self.question_label.config(text=f'Question {question_count}: {question}')

                    # get message from server
                    message = self.controller.receive_message()
                    if message == "only_one_player":
                        # if there is only one player in the game
                        messagebox.showinfo("Error", "There is only one player in the game. You win")
                        self.question_label.destroy()
                        self.answer_button.destroy()
                        self.answer_entry.destroy()

                        # wait restart message
                        self.wait_restart_message()

                    else:
                        result = json.loads(message)

                        # set scores
                        self.show_results(result)

                        # check if game is end
                        if result['is_end']:
                            self.is_end = True

                            messagebox.showinfo("Game is end", "Game is end")
                            self.question_label.destroy()
                            self.answer_button.destroy()
                            self.answer_entry.destroy()

                            # wait restart message
                            self.wait_restart_message()

                    # increase question count
                    question_count += 1

                    # clear answer entry
                    if not self.is_end:
                        self.answer_entry.delete(0, "end")

    def send_answer(self):
        """
        Send answer to server
        :return:
        """
        answer = self.answer_entry.get()
        self.controller.send_message(answer)

        # set waiting message
        self.waiting_message.config(text="Waiting for other players answer")

    def show_results(self, response: Dict[str, Any]):
        """
        Show scores in rich text box and messagebox
        :param response: response from server

        :return:
        """
        self.scores.config(state='normal')
        self.scores.delete('1.0', 'end')
        for name, score in response['scores'].items():
            self.scores.insert('end', f'{name}: {score} points \n')
        self.scores.config(state='disabled')

        messagebox.showinfo("Result", f"{response['message']} \n Correct answer: {response['answer']}")

    def check_connection(self):
        """
        Check connection with server
        :return:
        """
        while not self.is_end:
            if not self.controller.is_connected:
                messagebox.showerror("Error", "Connection is lost")
                self.is_end = True
                self.waiting_message.config(text="Connection lost")
                self.question_label.destroy()
                self.answer_button.destroy()
                self.answer_entry.destroy()
                return

    def wait_restart_message(self):
        """
        Wait restart message from server
        :return:
        """
        self.waiting_message.config(text="Waits server message")
        message = self.controller.receive_message()

        if message != "restart":
            self.controller.is_terminated = True
            self.waiting_message.config(text="Game is end")

            # add close button
            self.close_button = Button(self.root, text="Close", command=self.root.destroy)
            self.close_button.place(relx=0.5, rely=0.9, anchor="center")
            # break


if __name__ == "__main__":
    ClientInterface()
