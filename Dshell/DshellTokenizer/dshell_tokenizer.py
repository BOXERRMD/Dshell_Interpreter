__all__ = [
    "DshellTokenizer",
    "table_regex"
]

from .dshell_token_type import Token
from .dshell_token_type import DshellTokenType as DTT
from ..full_import import Enum, Optional, StrEnum

from .dshell_keywords import (dshell_keyword,
                              dshell_discord_keyword,
                              dshell_commands,
                              dshell_mathematical_operators,
                              dshell_logical_operators,
                              dshell_logical_word_operators)


class DshellSpecialChar(StrEnum):
    """Special characters that are structurally significant in the Dshell syntax."""
    QUOTE = '"'
    HASH = '#'
    L_ANGLE = '<'
    R_ANGLE = '>'
    AT = '@'
    BANG = '!'
    AMPERSAND = '&'
    L_BRACE = '{'
    R_BRACE = '}'
    L_PAREN = '('
    R_PAREN = ')'
    BACKTICK = '`'
    L_BRACKET = '['
    R_BRACKET = ']'


class DshellLiteralWord(StrEnum):
    """Keyword-like literals that are recognized as standalone values."""
    TRUE = 'True'
    FALSE = 'False'
    NONE = 'None'


class DshellParameterPrefix(Enum):
    """Supported parameter prefixes used to tag command arguments."""
    STR = "--'"
    LIST = '--*'
    VAR = '--'

    @property
    def token_type(self):
        return {
            DshellParameterPrefix.VAR: DTT.PARAMETER,
            DshellParameterPrefix.STR: DTT.STR_PARAMETER,
            DshellParameterPrefix.LIST: DTT.PARAMETERS,
        }[self]

from ..DshellPreProcess.dshell_preprocess import preProcessor


def is_line_empty(line: str) -> bool:
    """
    Check if a line is empty (only contains whitespace characters).
    :param line: The line to check.
    :return: True if the line is empty, False otherwise.
    """
    return all(c in ('', ' ', '\n') for c in line)


def _is_identifier_char(char: str) -> bool:
    """Return True if the character can be part of an identifier in Dshell."""
    return char.isalnum() or char == '_'


def _is_word_boundary_left(line: str, index: int) -> bool:
    """Return True if the left side of a word is not attached to another identifier."""
    if index == 0:
        return True
    return not (line[index - 1].isalnum() or line[index - 1] == '_')


def _is_word_boundary_right(line: str, index: int) -> bool:
    """Return True if the right side of a word is not attached to another identifier."""
    if index >= len(line):
        return True
    return not (line[index].isalnum() or line[index] == '_')


def _read_word(line: str, index: int) -> str:
    """Read a contiguous identifier-like word starting at index."""
    start = index
    while index < len(line) and _is_identifier_char(line[index]):
        index += 1
    return line[start:index]


def _read_escaped_string(line: str, index: int) -> tuple[str, int]:
    """Read a quoted string while unescaping backslash-escaped characters."""
    value: list[str] = []
    i = index + 1
    while i < len(line):
        char = line[i]
        if char == '\\':
            if i + 1 < len(line):
                value.append(line[i + 1])
                i += 2
            else:
                value.append(char)
                i += 1
            continue
        if char == '"':
            return ''.join(value), i + 1
        value.append(char)
        i += 1
    raise SyntaxError('Unterminated string literal')


def _match_parameter(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a parameter token such as --name, --*name or --'name."""
    for prefix in DshellParameterPrefix:
        prefix_value = prefix.value
        if not line.startswith(prefix_value, index):
            continue
        j = index + len(prefix_value)
        while j < len(line) and line[j].isspace():
            j += 1
        start = j
        while j < len(line) and _is_identifier_char(line[j]):
            j += 1
        if j == start:
            return None
        name = line[start:j]
        return prefix.token_type, name, j
    return None


def _match_mention(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a Discord mention like <@1234>, <#1234>, <@!1234> or <@&1234>."""
    if line[index] != DshellSpecialChar.L_ANGLE:
        return None
    j = index + 1
    if j < len(line) and line[j] == DshellSpecialChar.AT:
        j += 1
        if j < len(line) and line[j] in (DshellSpecialChar.BANG, DshellSpecialChar.AMPERSAND):
            j += 1
    elif j < len(line) and line[j] == DshellSpecialChar.HASH:
        j += 1
    if j >= len(line) or not line[j].isdigit():
        return None
    start = j
    while j < len(line) and line[j].isdigit():
        j += 1
    if j < len(line) and line[j] == DshellSpecialChar.R_ANGLE:
        return DTT.MENTION, line[start:j], j + 1
    return None


def _match_keyword(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a Dshell keyword such as if, var, loop, #if, #end, etc."""
    if index < len(line) and line[index] == DshellSpecialChar.HASH:
        start = index + 1
    else:
        start = index
    word = _read_word(line, start)
    if not word:
        return None
    if start == index and not _is_word_boundary_left(line, index):
        return None
    candidate = f"{DshellSpecialChar.HASH if index < len(line) and line[index] == DshellSpecialChar.HASH else ''}{word}"
    if candidate in dshell_keyword:
        return DTT.KEYWORD, candidate, start + len(word)
    return None


def _match_discord_keyword(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a Discord-related keyword like #embed, #field, #button, etc."""
    if index < len(line) and line[index] == DshellSpecialChar.HASH:
        start = index + 1
    else:
        start = index
    if start >= len(line) or not (line[start].isalpha() or line[start] == '_'):
        return None
    word = _read_word(line, start)
    candidate = f"{DshellSpecialChar.HASH if index < len(line) and line[index] == DshellSpecialChar.HASH else ''}{word}"
    if candidate.lower() in {k.lower() for k in dshell_discord_keyword}:
        return DTT.DISCORD_KEYWORD, candidate, start + len(word)
    return None


def _match_command(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a built-in command name when it appears as a standalone word."""
    start = index
    if not (line[start].isalpha() or line[start] == '_'):
        return None
    word = _read_word(line, start)
    if not word:
        return None
    if not _is_word_boundary_left(line, start) or not _is_word_boundary_right(line, start + len(word)):
        return None
    lowered = word.lower()
    for command_name in dshell_commands:
        if lowered == command_name.lower():
            return DTT.COMMAND, word, start + len(word)
    return None


def _match_literal(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match an integer, float or hexadecimal literal starting at index."""
    if index + 1 < len(line) and line[index] == '0' and line[index + 1] in 'xX':
        j = index + 2
        while j < len(line) and line[j] in '0123456789abcdefABCDEF':
            j += 1
        if j > index + 2:
            return DTT.HEXA, line[index:j], j
    j = index
    while j < len(line) and line[j].isdigit():
        j += 1
    if j > index:
        if j + 1 < len(line) and line[j] == '.' and line[j + 1].isdigit():
            k = j + 1
            while k < len(line) and line[k].isdigit():
                k += 1
            return DTT.FLOAT, line[index:k], k
        return DTT.INT, line[index:j], j
    return None


def _match_operator(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a mathematical or logical operator at the current position."""
    for key in dshell_mathematical_operators.keys():
        if line.startswith(key, index):
            return DTT.MATHS_OPERATOR, key, index + len(key)
    for key in dshell_logical_operators.keys():
        if line.startswith(key, index):
            return DTT.LOGIC_OPERATOR, key, index + len(key)
    for key in dshell_logical_word_operators.keys():
        if line.startswith(key, index):
            end = index + len(key)
            if _is_word_boundary_left(line, index) and _is_word_boundary_right(line, end):
                return DTT.LOGIC_WORD_OPERATOR, key, end
    return None


def _match_boolean(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a boolean literal (True or False) regardless of the exact casing."""
    booleans: tuple[DshellLiteralWord, ...] = (DshellLiteralWord.TRUE, DshellLiteralWord.FALSE)
    for literal in booleans:
        value = literal.value
        if line[index:index + len(value)].lower() == value.lower() and _is_word_boundary_left(line, index) and _is_word_boundary_right(line, index + len(value)):
            return DTT.BOOL, value, index + len(value)
    return None


def _match_none(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match the None literal as a standalone identifier-like word."""
    value = DshellLiteralWord.NONE.value
    if line[index:index + len(value)].lower() == value.lower() and _is_word_boundary_left(line, index) and _is_word_boundary_right(line, index + len(value)):
        return DTT.NONE, value, index + len(value)
    return None


def _match_identifier(line: str, index: int) -> Optional[tuple[DTT, str, int]]:
    """Match a plain identifier for variables or names not reserved by other rules."""
    if not (line[index].isalpha() or line[index] == '_'):
        return None
    end = index + 1
    while end < len(line) and _is_identifier_char(line[end]):
        end += 1
    return DTT.IDENT, line[index:end], end


table_regex = {}
class DshellTokenizer:

    def __init__(self, code: str):
        """
        Initialize the tokenizer.
        :param code: The code to tokenize
        :param match_any_character: Whether to match any character
        """
        self.code: str = code

    def start(self):
        """
        Start the tokenizer to process the current code.
        Returns an array of tokens per line (normally separated by \\n)
        """
        split_commands = self.split(self.code)
        split_commands = preProcessor(split_commands)
        return self.tokenizer(split_commands)

    def tokenizer(self, command_lines: list[str]) -> list[list[Token]]:
        """
        Tokenize each line of code without regex, but following the same priority order
        as the original regex-based matcher.
        :param command_lines: The code separated into multiple lines by the split method
        """
        tokens: list[list[Token]] = []
        ident_tokens = 0

        for line_number, line in enumerate(command_lines, start=1):
            line = command_lines[line_number - 1]

            if is_line_empty(line):
                continue

            tokens.append([])
            tokens_per_line = tokens[ident_tokens]
            i = 0

            while i < len(line):
                char = line[i]

                if char.isspace():
                    i += 1
                    continue

                if char == DshellSpecialChar.QUOTE:
                    start = i
                    value, i = _read_escaped_string(line, i)
                    tokens_per_line.append(Token(DTT.STR, value, (line_number, start)))
                    continue

                if char == DshellSpecialChar.L_BRACE:
                    tokens_per_line.append(Token(DTT.EVAL_L_EXPRESSION, char, (line_number, i)))
                    i += 1
                    continue
                if char == DshellSpecialChar.R_BRACE:
                    tokens_per_line.append(Token(DTT.EVAL_R_EXPRESSION, char, (line_number, i)))
                    i += 1
                    continue
                if char == DshellSpecialChar.L_PAREN:
                    tokens_per_line.append(Token(DTT.EVAL_L_GROUP, char, (line_number, i)))
                    i += 1
                    continue
                if char == DshellSpecialChar.R_PAREN:
                    tokens_per_line.append(Token(DTT.EVAL_R_GROUP, char, (line_number, i)))
                    i += 1
                    continue
                if char == DshellSpecialChar.BACKTICK:
                    tokens_per_line.append(Token(DTT.EVAL_OUTDATED_GROUP, char, (line_number, i)))
                    i += 1
                    continue
                if char == DshellSpecialChar.L_BRACKET:
                    tokens_per_line.append(Token(DTT.LIST_L, char, (line_number, i)))
                    i += 1
                    continue
                if char == DshellSpecialChar.R_BRACKET:
                    tokens_per_line.append(Token(DTT.LIST_R, char, (line_number, i)))
                    i += 1
                    continue

                match = _match_parameter(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_mention(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_keyword(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_discord_keyword(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_command(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_literal(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_operator(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_boolean(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_none(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                match = _match_identifier(line, i)
                if match is not None:
                    token_type, value, next_index = match
                    tokens_per_line.append(Token(token_type, value, (line_number, i)))
                    i = next_index
                    continue

                i += 1

            tokens_per_line.sort(key=lambda t: t.position[1])

            if tokens_per_line:
                tokens[ident_tokens] = self.parse_group(tokens_per_line, line_number)

            ident_tokens += 1
        return tokens

    @staticmethod
    def split(command: str,
              global_split='\n',
              keep_grouping_character=True,
              grouping_character='"') -> list[
        str]:
        """
        Separate commands into a list while respecting strings between quotes.
        Escape grouping characters with a backslash (\\) to include them in the string.
        :param command: The string to split.
        :param global_split: The separator used (default '\\n').
        :param keep_grouping_character: If False, remove quotes around strings.
        :param grouping_character: The character used to group a string (default '"').
        :return: A list of split commands with restored strings.
        """

        result: list[str] = []
        in_string: bool = False # True if we are in a string
        backslash: bool = False
        line: list[str] = [] # buffer for each line

        for char in command:

            if backslash:
                line.append('\\')
                line.append(char)
                backslash = False

            elif char == global_split and not in_string:
                result.append(''.join(line))
                line.clear()

            elif char == grouping_character:
                in_string = not in_string
                if keep_grouping_character:
                    line.append(char)

            elif char == '\\':
                backslash = True

            else:
                line.append(char)

        result.append(''.join(line))

        return result

    @staticmethod
    def parse_group(tokens_in_line: list[Token],
                   line_position: int):
        """
        Parse all list in the current token line and return the modified list line.
        :return:
        """
        new_line: list[Token] = []
        last_tokens: list[Token] = []

        is_outdated_group: bool = False

        def add_new_group(dtt, ident):
            new_token = Token(dtt, [], (line_position, ident + 1))
            if last_tokens:
                last_tokens[-1].value.append(new_token)
            else:
                last_tokens.append(new_token)
                new_line.append(new_token)

        def add_group_in_existing_group(dtt_to_compare, dtt, ident: int):
            if token.type == dtt_to_compare:
                new_token = Token(dtt, [], (line_position, ident + 1))
                last_tokens[-1].value.append(new_token)
                last_tokens.append(new_token)
            else:
                last_tokens[-1].value.append(token)

        i = 0
        while i < len(tokens_in_line):
            token = tokens_in_line[i]

            if token.type == DTT.LIST_L:
                if last_tokens:
                    add_group_in_existing_group(DTT.LIST_L, DTT.LIST, i)
                else:
                    add_new_group(DTT.LIST, i)

            elif token.type == DTT.LIST_R:
                if last_tokens and last_tokens[-1].type == DTT.LIST:
                    last_tokens.pop()
                else:
                    raise SyntaxError(f"Unexpected ']' at line {line_position}")

            elif token.type == DTT.EVAL_L_EXPRESSION:
                if last_tokens:
                    add_group_in_existing_group(DTT.EVAL_L_EXPRESSION, DTT.EVAL_EXPRESSION, i)
                else:
                    add_new_group(DTT.EVAL_EXPRESSION, i)

            elif token.type == DTT.EVAL_R_EXPRESSION:
                if last_tokens and last_tokens[-1].type == DTT.EVAL_EXPRESSION:
                    last_tokens.pop()
                else:
                    raise SyntaxError("Unexpected '}' at line " + str(line_position))

            elif token.type == DTT.EVAL_L_GROUP:
                if last_tokens:
                    add_group_in_existing_group(DTT.EVAL_L_GROUP, DTT.EVAL_GROUP, i)
                else:
                    add_new_group(DTT.EVAL_GROUP, i)

            elif token.type == DTT.EVAL_R_GROUP:
                if last_tokens and last_tokens[-1].type == DTT.EVAL_GROUP:
                    last_tokens.pop()
                else:
                    raise SyntaxError(f"Unexpected ')' at line {line_position}, position {token.position}")

            elif token.type == DTT.EVAL_OUTDATED_GROUP:
                if is_outdated_group:
                    last_tokens.pop()
                    is_outdated_group = False
                elif last_tokens:
                    add_group_in_existing_group(DTT.EVAL_OUTDATED_GROUP, DTT.EVAL_GROUP, i)
                    is_outdated_group = True
                else:
                    add_new_group(DTT.EVAL_GROUP, i)
                    is_outdated_group = True


            elif last_tokens:
                last_tokens[-1].value.append(token)

            else:
                new_line.append(token)
            i += 1

        return new_line
