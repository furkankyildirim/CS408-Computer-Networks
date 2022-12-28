from tkinter import Tk, Frame, Label, Button


class MessageBox(Tk):

    def __init__(self, title, message, command):
        super().__init__()
        self.details_expanded = False
        self.title(title)
        self.geometry('350x75')
        self.minsize(350, 75)
        self.maxsize(425, 250)
        self.resizable(False, False)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        def action() -> None:
            """
            Action
            :return: None
            """
            self.destroy()
            command()

        button_frame = Frame(self)
        button_frame.grid(row=0, column=0, sticky='nsew')
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        text_frame = Frame(self)
        text_frame.grid(row=1, column=0, padx=(7, 7), pady=(7, 7), sticky='nsew')
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        Label(button_frame, text=message).grid(row=0, column=0, columnspan=3, pady=(7, 7), padx=(7, 7), sticky='w')
        Button(button_frame, text='No', command=self.destroy).grid(row=1, column=1, sticky='e')
        Button(button_frame, text='Yes', command=action).grid(row=1, column=2, padx=(7, 7), sticky='e')

        self.mainloop()
