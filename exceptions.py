class Termination(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
class BackExc(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
class HabitExist(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
class NoEntityExist(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)