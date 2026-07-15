from datetime import datetime


class Logger:

    def __init__(self):
        self.entries = []

    def log(self, message):

        now = datetime.now().strftime("%H:%M:%S")

        line = f"[{now}] {message}"

        print(line)

        self.entries.append(line)

    def clear(self):
        self.entries = []


logger = Logger()