class ValidationError(BaseException):
    def __init__(self, message, suggestions=None):
        self.message = message
        self.suggestions = suggestions
