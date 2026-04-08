from Dshell.full_import import Enum, auto, Union

__all__ = [
    'DshellTokenType',
    'Token',
    'MASK_CHARACTER'
]

MASK_CHARACTER = '§'


class DshellTokenType(Enum):
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto(),
    NONE = auto(),
    LIST = auto(),
    LIST_L = auto()
    LIST_R = auto()
    MENTION = auto()
    IDENT = auto()  # nom de variable, fonction
    KEYWORD = auto()  # if, let, end, etc.
    DISCORD_KEYWORD = auto()  # embed, #embed...
    COMMAND = auto()
    PARAMETER = auto()  # --
    PARAMETERS = auto(),  # --*
    STR_PARAMETER = auto(),  # --"
    MATHS_OPERATOR = auto()  # ==, +, -, *, etc.
    LOGIC_OPERATOR = auto(),
    LOGIC_WORD_OPERATOR = auto()  # and, or, not
    EVAL_GROUP = auto()  # (code)
    EVAL_OUTDATED_GROUP = auto()  # `code`
    EVAL_L_GROUP = auto() # (
    EVAL_R_GROUP = auto() # )
    EVAL_EXPRESSION = auto()
    EVAL_L_EXPRESSION = auto()  # for inline mathematical and logical expression
    EVAL_R_EXPRESSION = auto()
    ANY_CHARACTER = auto()  # pour les caractères non reconnus mais utilisé dans les données passé en paramètre des commandes
    COMMENT = auto()  # lignes commençant par ##

DTT_DATA = {
            DshellTokenType.NONE,
            DshellTokenType.INT,
            DshellTokenType.FLOAT,
            DshellTokenType.STR,
            DshellTokenType.BOOL,
            DshellTokenType.IDENT,
            DshellTokenType.LIST,
            DshellTokenType.EVAL_GROUP,
            DshellTokenType.EVAL_EXPRESSION
            }

class Token:
    def __init__(self, type_: DshellTokenType, value: Union[str, list], position: tuple[int, int]):
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return f"<{self.type.name} '{self.value}'>"

    def to_dict(self):
        def serialize_value(value):
            if isinstance(value, list):
                return [serialize_value(v) for v in value]
            elif isinstance(value, Token):
                return value.to_dict()
            return value

        return {
            "type": self.type.name,
            "value": serialize_value(self.value),
            "position": self.position
        }
