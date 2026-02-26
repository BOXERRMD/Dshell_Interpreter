__all__ = [
    "DshellTokenizer"
]

from .dshell_token_type import Token
from .dshell_token_type import DshellTokenType as DTT
from ..full_import import sub, findall, DOTALL

from .dshell_keywords import (dshell_keyword,
                              dshell_discord_keyword,
                              dshell_commands,
                              dshell_mathematical_operators,
                              dshell_logical_operators,
                              dshell_logical_word_operators)

encapsulated_caracter: dict[str, DTT] = {
    '[' : DTT.R_LIST,
    ']' : DTT.L_LIST,
    '{' : DTT.R_EVAL_EXPRESSION,
    '}' : DTT.L_EVAL_EXPRESSION,
    '`' :DTT.EVAL_GROUP
}

multiple_characters: dict[str, DTT] = {
    '--*': DTT.PARAMETERS,
    "--'": DTT.STR_PARAMETER,
    '--' : DTT.PARAMETER
}

word_characters: dict[str, DTT] = {
    'none' : DTT.NONE,
    'true' : DTT.BOOL,
    'false' : DTT.BOOL
}

string_caracters: dict[str, DTT] = {
    '"' : DTT.STR,
    "'" : DTT.STR
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
        return self.tokenizer(self.code)

    def tokenizer(self, code: str) -> list[Token]:
        """
        Tokenize each line of code
        :param command_lines: The code separated into multiple lines by the split method
        """
        allow_ident_caracters = ('_', '#')


        tokens: list[Token] = []
        current_line: int = 1
        i: int = 0 # position in the code

        while i < len(code):

            caracter = code[i]

            if caracter in "\t\r\n ":
                pass

            elif caracter in string_caracters.keys():
                string_delimiter = caracter
                string_value = ''
                i += 1
                while i < len(code) and code[i] != string_delimiter:
                    if code[i] == '\\' and i + 1 < len(code): # gestion des caractères d'échappement
                        string_value += code[i + 1]
                        i += 2
                    else:
                        string_value += code[i]
                        i += 1
                if i >= len(code):
                    raise SyntaxError(f"Unterminated string starting at line {current_line}, position {i - len(string_value) - 1}")
                tokens.append(Token(string_caracters[string_delimiter], string_value, (current_line, i - len(string_value) - 1)))
                i += 1

            elif caracter in encapsulated_caracter.keys():
                tokens.append(
                    Token(encapsulated_caracter[caracter], caracter, (current_line, i))
                )

            elif caracter in dshell_keyword:
                tokens.append(
                    Token(DTT.KEYWORD, caracter, (current_line, i))
                )

            elif caracter in dshell_discord_keyword:
                tokens.append(
                    Token(DTT.DISCORD_KEYWORD, caracter, (current_line, i))
                )

            elif any(code.startswith(multi_char, i) for multi_char in multiple_characters.keys()):
                for multi_char, token_type in multiple_characters.items():
                    if code.startswith(multi_char, i):
                        tokens.append(
                            Token(token_type, multi_char, (current_line, i))
                        )
                        i += len(multi_char)-1
                        break

            elif caracter in dshell_mathematical_operators:
                tokens.append(
                    Token(DTT.MATHS_OPERATOR, caracter, (current_line, i))
                )

            elif caracter in dshell_logical_operators:
                tokens.append(
                    Token(DTT.LOGIC_OPERATOR, caracter, (current_line, i))
                )

            elif caracter in dshell_logical_word_operators:
                tokens.append(
                    Token(DTT.LOGIC_WORD_OPERATOR, caracter, (current_line, i))
                )

            elif caracter.isdigit():
                number_str = caracter
                i += 1
                while i < len(code) and (code[i].isdigit() or code[i] == '.'):
                    number_str += code[i]
                    i += 1
                if '.' in number_str:
                    tokens.append(Token(DTT.FLOAT, float(number_str), (current_line, i - len(number_str))))
                else:
                    tokens.append(Token(DTT.INT, int(number_str), (current_line, i - len(number_str))))
                continue

            elif caracter.isalpha() or caracter in allow_ident_caracters:
                ident_str = caracter
                i += 1
                while i < len(code) and (code[i].isalnum() or code[i] in allow_ident_caracters):
                    ident_str += code[i]
                    i += 1
                if ident_str in dshell_commands:
                    tokens.append(Token(DTT.COMMAND, ident_str, (current_line, i - len(ident_str))))
                elif ident_str in dshell_keyword:
                    tokens.append(Token(DTT.KEYWORD, ident_str, (current_line, i - len(ident_str))))
                elif ident_str in dshell_discord_keyword:
                    tokens.append(Token(DTT.DISCORD_KEYWORD, ident_str, (current_line, i - len(ident_str))))
                elif ident_str.lower() in word_characters: # on utilise lower() pour permettre une ecriture insensible à la casse
                    tokens.append(Token(word_characters[ident_str], ident_str, (current_line, i - len(ident_str))))
                else:
                    tokens.append(Token(DTT.IDENT, ident_str, (current_line, i - len(ident_str))))

            else:
                tokens.append(Token(DTT.ANY_CHARACTER, caracter, (current_line, i)))

            i += 1

        return tokens
