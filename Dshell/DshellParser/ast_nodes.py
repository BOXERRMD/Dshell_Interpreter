from Dshell.full_import import (Any, randint, Optional, Union, Embed, Member, Role, PermissionOverwrite)
from ..DshellTokenizer.dshell_token_type import Token
from ..DshellInterpreteur.dshell_global_variables import MAX_STR_SIZE, MAX_LIST_SIZE

from sys import getsizeof

__all__ = [
    'ASTNode',
    'StrNode',
    'IntNode',
    'FloatNode',
    'BoolNode',
    'LengthNode',
    'StartNode',
    'ElseNode',
    'ElifNode',
    'IfNode',
    'LoopNode',
    'ArgsCommandNode',
    'CommandNode',
    'VarNode',
    'EndNode',
    'FieldEmbedNode',
    'ConstructEmbedNode',
    'EmbedNode',
    'SleepNode',
    'ListNode',
    'ConstructPermissionNode',
    'PermissionNode',
    'EvalGroupNode',
    'ParamNode',
    'CodeNode',
    'EvalNode',
    'ReturnNode',
    'UiButtonNode',
    'UiSelectNode',
    'OptionUiSelectNode',
    'ScanNode',
    'FileNode'
]


class ASTNode:
    """
    Base class for all AST nodes.
    """
    def __init__(self, line: int):
        self.line = line

    def __getattr__(self, item):
        raise AttributeError(f"'{type(self).__name__}' node has no attribute '{item}'")


class StrNode(str, ASTNode):

    def __new__(cls, value: str):
        return super().__new__(cls, value)

    def __len__(self):
        return super().__len__()

    def __sizeof__(self):
        return len(self)*getsizeof(str)

    def __add__(self, other: "StrNode"):
        if not isinstance(other, StrNode):
            raise Exception(f"Cannot add '{type(other).__name__}' type to StrNode !")
        if len(self) + len(other) > MAX_STR_SIZE:
            raise Exception(f"Str type cannot exceed {MAX_STR_SIZE} characters ! [+ operator]")
        return StrNode(super().__add__(other))

    def __mul__(self, other: int):
        if not isinstance(other, int):
            raise Exception(f"Cannot mul '{type(other).__name__}' type to StrNode !")
        if len(self) * other > MAX_STR_SIZE:
            raise Exception(f"Str type cannot exceed {MAX_STR_SIZE} characters ! [* operator]")
        return StrNode(super().__mul__(other))

    def __int__(self):
        try:
            return int(self)
        except ValueError:
            raise Exception(f"Cannot convert StrNode to int: '{self}' is not a valid integer string !")

    def __float__(self):
        try:
            return float(self)
        except ValueError:
            raise Exception(f"Cannot convert StrNode to float: '{self}' is not a valid float string !")

    def __getitem__(self, item: int):
        try:
            return StrNode(super().__getitem__(item))
        except IndexError:
            raise IndexError(f"StrNode index out of range: {item} for string of length {len(self)} !")

    def replace(self, old: "StrNode", new: "StrNode"):
        if not isinstance(old, StrNode) and not isinstance(new, StrNode):
            raise Exception(f"Cannot replace '{type(old).__name__}' type with '{type(new).__name__}' type !")
        if len(self) - self.count(old) * len(old) + self.count(old) * len(new) > MAX_STR_SIZE:
            raise Exception(f"Str type cannot exceed {MAX_STR_SIZE} characters ! [replace method]")
        return StrNode(super().replace(old, new))

    def __repr__(self):
        return f"<StrNode> - {super().__repr__()}"

class IntNode(int, ASTNode):
    def __new__(cls, value: int, base: int = 10):
        return super().__new__(cls, value, base=base)

    def __repr__(self):
        return f"<IntNode> - {super().__repr__()}"

class FloatNode(float, ASTNode):
    def __new__(cls, value: float):
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<FloatNode> - {super().__repr__()}"

class BoolNode(int, ASTNode):
    def __new__(cls, value: int):
        return super().__new__(cls, int(bool(value)))

    def __repr__(self):
        return f"<BoolNode> - {super().__repr__()}"

class StartNode(ASTNode):
    """
    Node representing the start of the AST.
    """

    def __init__(self, body: list, line: int):
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<StartNode> - {self.body}"

    def to_dict(self):
        """
        Convert the StartNode to a dictionary representation.
        :return: Dictionary representation of the StartNode.
        """
        return {
            "type": "StartNode",
            "body": [token.to_dict() for token in self.body]
        }

class ElseNode(ASTNode):
    """
    Node representing the 'else' part of an if statement.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the body of the else statement
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<Else> - {self.body}"

    def to_dict(self):
        """
        Convert the ElseNode to a dictionary representation.
        :return: Dictionary representation of the ElseNode.
        """
        return {
            "type": "ElseNode",
            "body": [token.to_dict() for token in self.body]
        }


class ElifNode(ASTNode):
    """
    Node representing an 'elif' part of an if statement.
    """

    def __init__(self, condition: list[Token], body: list[Token], parent: "IfNode", line: int):
        """
        :param condition: list of tokens representing the condition for the elif
        :param body: list of tokens representing the body of the elif
        :param parent: the if node that this elif belongs to
        """
        super().__init__(line)
        self.condition = condition
        self.body = body
        self.parent = parent

    def __repr__(self):
        return f"<Elif> - {self.condition} - {self.body}"

    def to_dict(self):
        """
        Convert the ElifNode to a dictionary representation.
        :return: Dictionary representation of the ElifNode.
        """
        return {
            "type": "ElifNode",
            "condition": [token.to_dict() for token in self.condition],
            "body": [token.to_dict() for token in self.body],
            "parent": self.parent.id  # Assuming parent is an IfNode, we store its ID
        }


class IfNode(ASTNode):
    """
    Node representing an 'if' statement, which can contain 'elif' and 'else' parts.
    """

    def __init__(self, condition: list[Token], body: list[Token], line: int,
                 elif_nodes: Optional[list[ElifNode]] = None, else_body: Optional[ElseNode] = None):
        """
        :param condition: list of tokens representing the condition for the if statement
        :param body: list of tokens representing the body of the if statement
        :param elif_nodes: optional list of ElifNode instances representing 'elif' parts
        :param else_body: optional ElseNode instance representing the 'else' part
        """
        super().__init__(line)
        self.condition = condition
        self.body = body
        self.elif_nodes = elif_nodes
        self.else_body = else_body
        self.id = randint(0, 1000000)  # Unique identifier for the IfNode instance

    def __repr__(self):
        return f"<If> - {self.condition} - {self.body} *- {self.elif_nodes} **- {self.else_body}"

    def to_dict(self):
        """
        Convert the IfNode to a dictionary representation.
        :return: Dictionary representation of the IfNode.
        """
        return {
            "type": "IfNode",
            "condition": [token.to_dict() for token in self.condition],
            "body": [token.to_dict() for token in self.body],
            "elif_nodes": [elif_node.to_dict() for elif_node in self.elif_nodes] if self.elif_nodes else None,
            "else_body": self.else_body.to_dict() if self.else_body else None,
            "id": self.id
        }


class LoopNode(ASTNode):
    """
    Node representing a loop structure in the AST.
    """

    def __init__(self, variable: "VarNode", body: list, line: int):
        """
        :param variable: VarNode representing the loop variable. This variable will be used to iterate over the body. Can contain a ListNode, string or integer.
        :param body: list of tokens representing the body of the loop
        """
        super().__init__(line)
        self.variable = variable
        self.body = body

    def __repr__(self):
        return f"<Loop> - {self.variable.name} -> {self.variable.body} *- {self.body}"

    def to_dict(self):
        """
        Convert the LoopNode to a dictionary representation.
        :return: Dictionary representation of the LoopNode.
        """
        return {
            "type": "LoopNode",
            "variable": self.variable.to_dict(),
            "body": [token.to_dict() for token in self.body]
        }


class ArgsCommandNode(ASTNode):
    """
    Node representing the arguments of a command in the AST.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the arguments of the command
        """
        super().__init__(line)
        self.body: list[Token] = body

    def __repr__(self):
        return f"<Args Command> - {self.body}"

    def to_dict(self):
        """
        Convert the ArgsCommandNode to a dictionary representation.
        :return: Dictionary representation of the ArgsCommandNode.
        """
        return {
            "type": "ArgsCommandNode",
            "body": [token.to_dict() for token in self.body]
        }

class ScanNode(ASTNode):
    """
    Node representing a scan message in the AST
    """
    def __init__(self, body: ArgsCommandNode, line: int):
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<SCAN> - {self.body}"

    def to_dict(self):
        """
        Convert the ScanNode to a dictionary representation.
        :return: Dictionary representation of the ScanNode.
        """
        return {
            "type": "ScanNode",
            "body": self.body.to_dict()
        }

class CommandNode(ASTNode):
    """
    Node representing a command in the AST.
    """

    def __init__(self, name: str, body: ArgsCommandNode, line: int):
        """
        :param name: The command name (e.g., "sm", "cc")
        :param body: ArgsCommandNode containing the arguments of the command
        """
        super().__init__(line)
        self.name = name
        self.body = body

    def __repr__(self):
        return f"<{self.name}> - {self.body}"

    def to_dict(self):
        """
        Convert the CommandNode to a dictionary representation.
        :return: Dictionary representation of the CommandNode.
        """
        return {
            "type": "CommandNode",
            "name": self.name,
            "body": self.body.to_dict()
        }


class VarNode(ASTNode):
    """
    Node representing a variable declaration in the AST.
    """

    def __init__(self, name: Token, body: list[Union[Token, ASTNode]], line: int):
        """
        :param name: Token representing the variable name
        :param body: list of tokens representing the body of the variable
        """
        super().__init__(line)
        self.name = name
        self.body = body

    def __repr__(self):
        return f"<VAR> - {self.name} *- {self.body}"

    def to_dict(self):
        """
        Convert the VarNode to a dictionary representation.
        :return: Dictionary representation of the VarNode.
        """
        return {
            "type": "VarNode",
            "name": self.name.to_dict(),
            "body": [token.to_dict() for token in self.body]
        }

class LengthNode(ASTNode):
    """
    Node representing the length operation in the AST.
    """

    def __init__(self, body: Token, line: int):
        """
        :param body: list of tokens representing the body of the length operation
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<LENGTH> - {self.body}"

    def to_dict(self):
        """
        Convert the LengthNode to a dictionary representation.
        :return: Dictionary representation of the LengthNode.
        """
        return {
            "type": "LengthNode",
            "body": self.body.to_dict()
        }

class EndNode(ASTNode):
    """
    Node representing the end of the AST.
    """

    def __init__(self, line: int, error_message: Union[Token, bool] = True):
        super().__init__(line)
        self.error_message: bool = error_message

    def __repr__(self):
        return f"<END>"

    def to_dict(self):
        """
        Convert the EndNode to a dictionary representation.
        :return: Dictionary representation of the EndNode.
        """
        return {
            "type": "EndNode",
            "error_message": self.error_message
        }


class FieldEmbedNode(ASTNode):
    """
    Node representing a field in an embed structure.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the field content
        """
        super().__init__(line)
        self.body: list[Token] = body

    def __repr__(self):
        return f"<EMBED_FIELD> - {self.body}"

    def to_dict(self):
        """
        Convert the FieldEmbedNode to a dictionary representation.
        :return: Dictionary representation of the FieldEmbedNode.
        """
        return {
            "type": "FieldEmbedNode",
            "body": [token.to_dict() for token in self.body]
        }


class ConstructEmbedNode(ASTNode):
    """
    Node representing an embed structure in the AST.
    """

    def __init__(self, body: list[Token], fields: list[FieldEmbedNode], line: int):
        """
        :param body: list of tokens representing the embed content
        :param fields: list of FieldEmbedNode instances representing the fields of the embed
        """
        super().__init__(line)
        self.body = body
        self.fields = fields

    def __repr__(self):
        return f"<EMBED> - {self.body}"

    def to_dict(self):
        """
        Convert the EmbedNode to a dictionary representation.
        :return: Dictionary representation of the EmbedNode.
        """
        return {
            "type": "EmbedNode",
            "body": [token.to_dict() for token in self.body],
            "fields": [field.to_dict() for field in self.fields]
        }

class EmbedNode(ASTNode):
    def __init__(self, value: Embed):
        super().__init__(-1)
        self.value = value

    def __sizeof__(self):
        return len(self.value)*getsizeof(str)

    def __repr__(self):
        return f"<EMBED> - {self.value.title}"

class ConstructPermissionNode(ASTNode):
    """
    Node representing a permission structure in the AST.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the permission content
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<PERMISSION> - {self.body}"

    def to_dict(self):
        """
        Convert the PermissionNode to a dictionary representation.
        :return: Dictionary representation of the PermissionNode.
        """
        return {
            "type": "PermissionNode",
            "body": [token.to_dict() for token in self.body]
        }

class PermissionNode(ASTNode):
    def __init__(self, value: dict[Union[Member, Role, None], PermissionOverwrite]):
        super().__init__(-1)
        self.value = value

    def members(self):
        return PermissionNode({member: permission for member, permission in self.value.items() if isinstance(member, Member)})

    def roles(self):
        return PermissionNode({role: permission for role, permission in self.value.items() if isinstance(role, Role)})

    def none(self):
        return PermissionNode({None: permission for member, permission in self.value.items() if member is None})

    def update(self, other: "PermissionNode"):
        if not isinstance(other, PermissionNode):
            raise Exception(f"Cannot update PermissionNode with '{type(other).__name__}' type !")
        self.value.update(other.value)

    def __sizeof__(self):
        return len(self.value)*getsizeof(PermissionOverwrite)*getsizeof(str)

class SleepNode(ASTNode):
    """
    Node representing a sleep command in the AST.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the sleep duration
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<SLEEP> - {self.body}"

    def to_dict(self):
        """
        Convert the SleepNode to a dictionary representation.
        :return: Dictionary representation of the SleepNode.
        """
        return {
            "type": "SleepNode",
            "body": [token.to_dict() for token in self.body]
        }

class EvalGroupNode(ASTNode):
    """
    Node representing a group of evaluations in the AST.
    This is used to group multiple evaluations together.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the body of the evaluation group
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<EVAL GROUP> - {self.body}"

    def to_dict(self):
        """
        Convert the EvalGroupNode to a dictionary representation.
        :return: Dictionary representation of the EvalGroupNode.
        """
        return {
            "type": "EvalGroupNode",
            "body": [token.to_dict() for token in self.body]
        }

class ParamNode(ASTNode):
    """
    Node representing a parameter in the AST.
    This is used to define parameters for variables passed to the dshell interpreter.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param name: Token representing the parameter name
        :param body: list of tokens representing the body of the parameter
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<PARAM> - {self.body}"

    def to_dict(self):
        """
        Convert the ParamNode to a dictionary representation.
        :return: Dictionary representation of the ParamNode.
        """
        return {
            "type": "ParamNode",
            "body": [token.to_dict() for token in self.body]
        }

class CodeNode(ASTNode):
    """
    Node representing a block of code to pass in arguments.
    """
    def __init__(self, body: list[ASTNode], line: int):
        """
        :param body: list of Node representing the code already parsed
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<CODE> - {self.body}"

    def to_dict(self):
        """
        Convert the CodeNode to a dictionary representation.
        :return: Dictionary representation of the CodeNode.
        """
        return {
            "type": "CodeNode",
            "body": [token.to_dict() for token in self.body]
        }

class EvalNode(ASTNode):
    """
    Node representing an evaluation in the AST.
    This is used to evaluate expressions in Dshell.
    """

    def __init__(self, codeNode: Token, argsNode: ArgsCommandNode, line: int):
        """
        :param body: list of tokens representing the expression to evaluate
        """
        super().__init__(line)
        self.codeNode = codeNode
        self.argsNode = argsNode

    def __repr__(self):
        return f"<EVAL> - {self.argsNode} -> {self.codeNode}"

    def to_dict(self):
        """
        Convert the EvalNode to a dictionary representation.
        :return: Dictionary representation of the EvalNode.
        """
        return {
            "type": "EvalNode",
            "codeNode": self.codeNode.to_dict(),
            "argsNode": self.argsNode.to_dict()
        }

class ReturnNode(ASTNode):
    """
    Node representing a return statement in the AST.
    This is used to return values from functions in Dshell.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the value to return
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<RETURN> - {self.body}"

    def to_dict(self):
        """
        Convert the ReturnNode to a dictionary representation.
        :return: Dictionary representation of the ReturnNode.
        """
        return {
            "type": "ReturnNode",
            "body": [token.to_dict() for token in self.body]
        }


class UiButtonNode(ASTNode):
    """
    Node representing a UI button component in the AST.
    This is used to define button elements for commands in Dshell.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the button component
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<UI BUTTON> - {self.body}"

    def to_dict(self):
        """
        Convert the UiButtonNode to a dictionary representation.
        :return: Dictionary representation of the UiButtonNode.
        """
        return {
            "type": "UiButtonNode",
            "body": [token.to_dict() for token in self.body]
        }

class UiSelectNode(ASTNode):
    """
    Node representing a UI select component in the AST.
    This is used to define select elements for commands in Dshell.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the select component
        """
        super().__init__(line)
        self.body = body
        self.options: list[OptionUiSelectNode] = []

    def __repr__(self):
        return f"<UI SELECT> - {self.body} -> {self.options}"

    def to_dict(self):
        """
        Convert the UiSelectNode to a dictionary representation.
        :return: Dictionary representation of the UiSelectNode.
        """
        return {
            "type": "UiSelectNode",
            "body": [token.to_dict() for token in self.body]
        }

class OptionUiSelectNode(ASTNode):
    """
    Node representing an option in a UI select component in the AST.
    This is used to define options for select elements for commands in Dshell.
    """

    def __init__(self, body: list[Token], line: int):
        """
        :param body: list of tokens representing the option component
        """
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"<UI SELECT OPTION> - {self.body}"

    def to_dict(self):
        """
        Convert the OptionUiSelectNode to a dictionary representation.
        :return: Dictionary representation of the OptionUiSelectNode.
        """
        return {
            "type": "OptionUiSelectNode",
            "body": [token.to_dict() for token in self.body]
        }

class FileNode(ASTNode):
    def __init__(self, name: Optional[StrNode] = None, description: Optional[StrNode] = None, spoiler: bool = False):
        super().__init__(0)
        self.name = name
        self.description = description
        self.spoiler = spoiler
        self.content: bytearray = bytearray("", "utf-8")

    def write(self, content: bytearray, append: bool):

        if self.size() + len(content) > 5 * 1024:
            raise Exception("The file content cannot exceed 5 Ko !")

        if append:
            self.content += content
        else:
            self.content = content

    def read(self):
        return self.content.decode(encoding="utf-8", errors="ignore")

    def size(self):
        return len(self.content)

    def __len__(self):
        return len(self.read())
    
    def __sizeof__(self):
        return self.size()*getsizeof(str)

class ListNode(ASTNode):
    """
    Node representing a list structure in the AST.
    Iterable class for browsing lists created from Dshell code.
    This class also lets you interact with the list via specific methods not built in by python.
    """

    def __init__(self, body: list[Any]):
        """
        :param body: list of elements to initialize the ListNode with
        """
        super().__init__(-1)
        self.iterable: list[Any] = body
        self.len_iterable: int = len(body)
        self.iterator_count: int = 0
        self.size: int = 0

    def to_dict(self):
        """
        Convert the ListNode to a dictionary representation.
        :return: Dictionary representation of the ListNode.
        """
        return {
            "type": "ListNode",
            "body": [token.to_dict() for token in self.iterable]
        }

    def size_add(self, value):
        """
        Add the size value object to self.value
        :param value:
        :return:
        """
        self.size += getsizeof(value)

    def size_remove(self, value):
        """
        Remove the size value object from self.value
        :param value:
        :return:
        """
        self.size -= getsizeof(value)

    def add(self, value: Any):
        """
        Add a value to the list.
        """
        if self.len_iterable > 1000:
            raise PermissionError('The list is too long, it must not exceed 1000 elements !')

        if self.size + getsizeof(value) > MAX_LIST_SIZE:
            raise Exception(f"The list size cannot exceed {MAX_LIST_SIZE} bytes !")

        self.iterable.append(value)
        self.len_iterable += 1
        self.size_add(value)

    def remove(self, value: Any, number: int = 1):
        """
        Remove a value from the list.
        """
        if number < 1:
            raise Exception(f"The number of elements to remove must be at least 1, not {number} !")

        count = 0
        while number > 0 and count < self.len_iterable:
            if self.iterable[count] == value:
                self.iterable.pop(count)
                self.len_iterable -= 1
                number -= 1
                self.size_remove(value)
                continue
            count += 1

    def pop(self, index: int = -1):
        """
        Remove and return the last element of the list.
        :return: The last element of the list.
        """
        if self.len_iterable == 0:
            raise IndexError("pop from empty list")
        if 0 > index >= self.len_iterable or -self.len_iterable > index < 0:
            raise IndexError("pop index out of range")

        self.len_iterable -= 1
        self.size_remove(self.iterable[index])
        return self.iterable.pop(index)

    def set(self, index: int, value: Any):
        """
        Set the value at a specific index in the list.
        :param index: The index at which to set the value.
        :param value: The value to set at the specified index.
        """
        if 0 > index >= self.len_iterable or -self.len_iterable > index < 0:
            raise IndexError("set index out of range")

        self.size_remove(self.iterable[index])
        self.size_add(value)
        self.iterable[index] = value

    def count(self):
        """
        Return the number of elements in the list.
        :return: The number of elements in the list.
        """
        return self.len_iterable

    def clear(self):
        """
        Clear the list.
        """
        self.iterable = []
        self.len_iterable = 0
        self.iterator_count = 0
        self.size = 0

    def sort(self, reverse: bool = False):
        """
        Sort the list.
        :param reverse: Whether to sort the list in reverse order.
        """
        self.iterable.sort(reverse=reverse)

    def reverse(self):
        """
        Reverse the list.
        """
        self.iterable.reverse()

    def extend(self, values: "ListNode"):
        """
        Extend the list with another list.
        :param values: List of values to extend the list with.
        """
        for v in values:
            self.add(v)

    def __add__(self, other: "ListNode"):
        """
        Add another ListNode to this one.
        :param other: Another ListNode to add to this one.
        :return: Instance of ListNode with combined elements.
        """
        for i in other:
            self.add(i)
        return self

    def __iter__(self):
        return self

    def __next__(self):
        """
        Iterate over the elements of the list.
        :return: an element from the list.
        """

        if self.iterator_count >= self.len_iterable:
            self.iterator_count = 0
            raise StopIteration()

        v = self.iterable[self.iterator_count]
        self.iterator_count += 1
        return v

    def __len__(self):
        return self.len_iterable

    def __getitem__(self, item):
        if 0 <= item <= self.len_iterable-1:
            return self.iterable[item]
        raise IndexError(f"Index out of range on ListNode !")

    def __bool__(self):
        return bool(self.iterable)

    def __sizeof__(self):
        return self.size

    def __repr__(self):
        return f"<LIST> - {self.iterable}"

