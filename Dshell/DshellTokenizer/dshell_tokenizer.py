__all__ = [
    "DshellTokenizer",
    "table_regex",
    "MASK_CHARACTER"
]

from .dshell_token_type import Token
from .dshell_token_type import DshellTokenType as DTT

from Dshell.full_import import (
                           Pattern,
                           ASCII,
                           DOTALL,
                           IGNORECASE,
                           compile,
                           escape,
                           finditer,
                           Match,
                           sub)

from .dshell_keywords import (dshell_keyword,
                              dshell_discord_keyword,
                              dshell_commands,
                              dshell_mathematical_operators,
                              dshell_logical_operators,
                              dshell_logical_word_operators)

from ..DshellPreProcess.dshell_preprocess import preProcessor

MASK_CHARACTER = '§'

def is_line_empty(line: str) -> bool:
    """
    Check if a line is empty (only contains whitespace characters).
    :param line: The line to check.
    :return: True if the line is empty, False otherwise.
    """
    return all(c in (MASK_CHARACTER, ' ', '\n') for c in line)

table_regex: dict[DTT, Pattern] = {
    DTT.STR: compile(r'"((?:[^\\"]|\\.)*)"', flags=DOTALL),
    DTT.EVAL_L_EXPRESSION: compile(r"({)"),
    DTT.EVAL_R_EXPRESSION: compile(r"(})"),
    DTT.EVAL_L_GROUP: compile(rf"(\()"),
    DTT.EVAL_R_GROUP: compile(r"(\))"),
    DTT.EVAL_OUTDATED_GROUP: compile(r"(`)"),
    DTT.LIST_L: compile(r"(\[)"),
    DTT.LIST_R: compile(r"(])"),
    DTT.PARAMETERS: compile(rf"--\*\s*([A-Za-z_]+)\s*", flags=ASCII),
    DTT.STR_PARAMETER: compile(rf"--'\s*([A-Za-z_]+)\s*", flags=ASCII),
    DTT.PARAMETER: compile(rf"--\s*([A-Za-z_]+)\s*", flags=ASCII),
    DTT.MENTION: compile(r'<(?:@[!&]?|#)([0-9]+)>'),
    DTT.KEYWORD: compile(rf"(?<!\w)(#?{'|'.join(dshell_keyword)})(?!\w)"),
    DTT.DISCORD_KEYWORD: compile(rf"(?<![\w\-])(#?{'|'.join(dshell_discord_keyword)})(?![\w\-])" , flags=IGNORECASE),
    DTT.COMMAND: compile(rf"\b({'|'.join(dshell_commands.keys())})\b", flags=IGNORECASE),
    DTT.FLOAT: compile(r"(\d+\.\d+)"),
    DTT.HEXA: compile(r"(0[Xx][0-9a-fA-F]+)"),
    DTT.INT: compile(r"(\d+)"),
    DTT.MATHS_OPERATOR: compile(rf"({'|'.join([escape(i) for i in dshell_mathematical_operators.keys()])})"),
    DTT.LOGIC_OPERATOR: compile(rf"({'|'.join([escape(i) for i in dshell_logical_operators.keys()])})"),
    DTT.LOGIC_WORD_OPERATOR: compile(
        rf"(?:^|\s)({'|'.join([escape(i) for i in dshell_logical_word_operators.keys()])})(?:$|\s)"),
    DTT.BOOL: compile(r"(True|False)", flags=IGNORECASE),
    DTT.NONE: compile(r"(None)", flags=IGNORECASE),
    DTT.IDENT: compile(rf"([A-Za-z0-9_]+)"),
}

backslash_pattern = compile(r"\\(.)", flags=DOTALL)

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
        Tokenize each line of code
        :param command_lines: The code separated into multiple lines by the split method
        """
        tokens: list[list[Token]] = []
        ident_tokens = 0

        for line_number, line in enumerate(command_lines, start=1):
            line: str = command_lines[line_number-1] # get the current line

            # if the line is empty or already tokenized, pass the line.
            if is_line_empty(line):
                continue

            tokens.append([])
            tokens_per_line = tokens[ident_tokens]

            for token_type, regex in table_regex.items():
                for match in finditer(regex, line):
                    match: Match

                    start_match = match.start()
                    end_match = match.end()

                    token = Token(token_type, match.group(1), (line_number, start_match))
                    tokens_per_line.append(token)

                    if token_type == DTT.STR:
                        token.value = sub(backslash_pattern, r"\1", token.value)

                    len_match = len(match.group(0))
                    line = line[:start_match] + MASK_CHARACTER * len_match + line[end_match:]

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
