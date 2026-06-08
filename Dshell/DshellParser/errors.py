class AstNodeError(Exception):
    """Base class for exceptions in this module."""
    pass

class ListNotEditableError(AstNodeError):

    def __init__(self):
        super().__init__("This list is not editable, you can't modify it !")