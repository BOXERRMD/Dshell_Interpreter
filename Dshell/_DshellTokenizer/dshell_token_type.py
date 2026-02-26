from Dshell.full_import import Enum, auto, Any

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
    BOOL = auto()
    NONE = auto()
    R_LIST = auto() # [
    L_LIST = auto() # ]
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
    EVAL_GROUP = auto()  # `code`
    R_EVAL_EXPRESSION = auto()  # for inline mathematical and logical expression {
    L_EVAL_EXPRESSION = auto()  # for inline mathematical and logical expression }
    ANY_CHARACTER = auto()  # pour les caractères non reconnus mais utilisé dans les données passé en paramètre des commandes
    COMMENT = auto()  # lignes commençant par ##

DTT_DATA = {DshellTokenType.INT,
            DshellTokenType.FLOAT,
            DshellTokenType.STR,
            DshellTokenType.BOOL,
            DshellTokenType.IDENT,
            DshellTokenType.R_LIST,
            DshellTokenType.EVAL_GROUP,
            DshellTokenType.R_EVAL_EXPRESSION}

class Token:
    def __init__(self, type_: DshellTokenType, value: Any, position: tuple[int, int]):
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
