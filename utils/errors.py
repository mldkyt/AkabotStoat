
class CommandError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"Command Error: {self.message}"

class CommandParseError(CommandError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"Command Parsing Error: {self.message}"
