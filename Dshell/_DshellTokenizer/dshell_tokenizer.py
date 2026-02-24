__all__ = [
    "DshellTokenizer",
    "table_regex",
    "MASK_CHARACTER"
]

from .dshell_token_type import Token
from .dshell_token_type import DshellTokenType as DTT

from Dshell.full_import import (Pattern,
                           ASCII,
                           DOTALL,
                           IGNORECASE,
                           MULTILINE,
                           compile,
                           escape,
                           findall,
                           finditer,
                           search,
                           sub)

from .dshell_keywords import (dshell_keyword,
                              dshell_discord_keyword,
                              dshell_commands,
                              dshell_mathematical_operators,
                              dshell_logical_operators,
                              dshell_logical_word_operators)

MASK_CHARACTER = '§'

def is_line_empty(line: str) -> bool:
    """
    Check if a line is empty (only contains whitespace characters).
    :param line: The line to check.
    :return: True if the line is empty, False otherwise.
    """
    return all(c in (MASK_CHARACTER, ' ') for c in line)

table_regex: dict[DTT, Pattern] = {
    DTT.COMMENT: compile(r"::(.*)", flags=MULTILINE),
    DTT.STR: compile(r'"((?:[^\\"]|\\.)*)"', flags=DOTALL),
    DTT.EVAL_EXPRESSION: compile(r"(?P<brace>\{(?:[^{}]+|(?&brace))*})"),
    DTT.EVAL_GROUP: compile(r"(?P<brace>`(?:[^`]+|(?&brace))*`)"),
    DTT.LIST: compile(r"(?P<brace>\[(?:[^\[]+|(?&brace))*])"),
    DTT.PARAMETERS: compile(rf"--\*\s*([A-Za-z_]+)\s*", flags=ASCII),
    DTT.STR_PARAMETER: compile(rf"--\'\s*([A-Za-z_]+)\s*", flags=ASCII),
    DTT.PARAMETER: compile(rf"--\s*([A-Za-z_]+)\s*", flags=ASCII),
    DTT.MENTION: compile(r'<(?:@!?|@&|#)([0-9]+)>'),
    DTT.KEYWORD: compile(rf"(?<!\w)(#?{'|'.join(dshell_keyword)})(?!\w)"),
    DTT.DISCORD_KEYWORD: compile(rf"(?<!\w|-)(#?{'|'.join(dshell_discord_keyword)})(?!\w|-)", flags=IGNORECASE),
    DTT.COMMAND: compile(rf"\b({'|'.join(dshell_commands.keys())})\b", flags=IGNORECASE),
    DTT.MATHS_OPERATOR: compile(rf"({'|'.join([escape(i) for i in dshell_mathematical_operators.keys()])})"),
    DTT.LOGIC_OPERATOR: compile(rf"({'|'.join([escape(i) for i in dshell_logical_operators.keys()])})"),
    DTT.LOGIC_WORD_OPERATOR: compile(rf"(?:^|\s)({'|'.join([escape(i) for i in dshell_logical_word_operators.keys()])})(?:$|\s)"),
    DTT.FLOAT: compile(r"(\d+\.\d+)"),
    DTT.INT: compile(r"(\d+)"),
    DTT.BOOL: compile(r"(True|False)", flags=IGNORECASE),
    DTT.NONE: compile(r"(None)", flags=IGNORECASE),
    DTT.IDENT: compile(rf"([A-Za-z0-9_]+)"),
    DTT.ANY_CHARACTER: compile(rf"([^{MASK_CHARACTER}\n]+)"),
}


class DshellTokenizer:

    def __init__(self, code: str, math_any_character: bool = False):
        """
        Initialize the tokenizer.
        :param code: The code to tokenize
        :param math_any_character: Whether to match any character
        """
        self.code: str = code
        self.match_any_character: bool = math_any_character

    def start(self):
        """
        Start the tokenizer to process the current code.
        Returns an array of tokens per line (normally separated by \\n)
        """
        split_commands = self.split(self.code)
        return self.tokenizer(split_commands)

    def tokenizer(self, command_lines: list[str]) -> list[list[Token]]:
        """
        Tokenize each line of code
        :param command_lines: The code separated into multiple lines by the split method
        """
        tokens: list[list[Token]] = []

        line_number = 1
        for line in command_lines:  # iterate each line of code
            tokens_per_line: list[Token] = []
            is_comment: bool = False

            if is_line_empty(line):
                line_number += 1
                continue

            for token_type, pattern in table_regex.items():  # iterate the regex table to test all patterns on the line

                if is_line_empty(line):
                    break

                if not self.match_any_character and token_type == DTT.ANY_CHARACTER:
                    continue

                if is_comment:
                    is_comment = False
                    break

                for match in finditer(pattern, line):  # iterate the match results to get their positions

                    if token_type == DTT.COMMENT:  # if we encounter a comment, stop tokenizing the line
                        is_comment = True
                        break

                    start_match = match.start()  # start position of the match

                    token = Token(token_type, match.group(1), (line_number, start_match))  # record its token
                    tokens_per_line.append(token)

                    if token_type == DTT.STR:
                        token.value = token.value.replace(r'\"', '"')

                    if token_type in (
                            DTT.LIST,
                            DTT.EVAL_GROUP,
                            DTT.EVAL_EXPRESSION):  # if it's a data grouping, tokenize its contents
                        result = self.tokenizer([token.value[1:-1]]) # tokenize the content of the grouping without the grouping characters
                        token.value = result[0] if len(
                            result) > 0 else result  # handle whether the data structure is empty or not

                        for token_in_list in token.value:
                            token_in_list.position = (line_number, token_in_list.position[1])

                        for token_in_line in range(len(tokens_per_line)-1):
                            if tokens_per_line[token_in_line].position[1] > start_match:
                                str_tokens_in_list = tokens_per_line[token_in_line:-1]
                                tokens_per_line = tokens_per_line[:token_in_line] + [tokens_per_line[-1]]
                                token.value.extend(str_tokens_in_list)
                                token.value.sort(key=lambda t: t.position[1])  # sort tokens by their position
                                break


                    len_match = len(match.group(0))  # length of the match found
                    line = line[:start_match] + (MASK_CHARACTER * len_match) + line[
                                                                                    match.end():]  # replace the match to avoid matching it a second time

            tokens_per_line.sort(key=lambda
                token: token.position[1])  # sort the position based on token match positions to have them in code order
            if tokens_per_line:
                tokens.append(tokens_per_line)

            line_number += 1  # increment the line number for the next line

        return tokens

    @staticmethod
    def split(command: str, global_split='\n', keep_grouping_character=True, grouping_character='"') -> list[
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

        commands: str = command.strip()
        temporary_replacement = '[REPLACE]'
        pattern_find_regrouped_part = compile(fr'({grouping_character}(?:[^\\{grouping_character}]|\\.)*{grouping_character})', flags=DOTALL)
        between_grouping_character = findall(pattern_find_regrouped_part, commands)  # find parts between quotes and save them

        res = sub(pattern_find_regrouped_part,
                  temporary_replacement,
                  commands,
                  )  # replace parts between quotes

        res = res.split(global_split)  # split commands without quotes

        # restore quotes to their place
        result = []
        for i in res:
            while temporary_replacement in i:
                i = i.replace(temporary_replacement,
                              between_grouping_character[0][1: -1] if not keep_grouping_character else
                              between_grouping_character[0], 1)
                between_grouping_character.pop(0)
            result.append(i)
        return result
