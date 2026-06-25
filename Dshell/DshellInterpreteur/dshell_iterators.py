from ..full_import import Any
from ..DshellParser.ast_nodes import IntNode, FloatNode, StrNode, ListNode, FileNode, FileStreamNode

class DshellIterator:
    """
    Used to transform anything into an iterable
    """

    def __init__(self, data):
        self.data = self._check_data(data)
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.data)

    def _check_data(self, data: Any):

        if not isinstance(data, (StrNode, ListNode, FloatNode, IntNode, FileNode, FileStreamNode, IntIterator)):
            raise Exception(f"{data} can't be in a loop !")

        if isinstance(data, FileNode):
            return data.stream()

        elif isinstance(data, (FloatNode, IntNode)):
            return IntIterator(IntNode(data))

        else:
            return data

class IntIterator:

    def __init__(self, max_iterator: IntNode,
                 min_iterator: IntNode = IntNode(0),
                 step: IntNode = IntNode(1)):

        self.max_iterator = max_iterator
        self.min_iterator = min_iterator
        self.step = step
        self.pointer = self.min_iterator

    def __iter__(self) -> "IntIterator":
        return self

    def __next__(self) -> IntNode:
        if self.pointer == self.max_iterator:
            self.pointer = self.min_iterator
            raise StopIteration

        current = self.pointer
        self.pointer += self.step
        return current

    def __repr__(self):
        return f"<INT_ITERATOR> - {self.min_iterator} to {self.max_iterator} with step {self.step}"