__all__ = [
    "parse",
    "parser_inline",
    "to_postfix",
    "ast_to_dict",
]

from .ast_nodes import *
from .._DshellKeys.dshell_keywords import dshell_keyword, dshell_discord_keyword
from .._DshellTokenizer.dshell_token_type import Token
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from .._DshellTokenizer.dshell_token_type import DTT_DATA
from .._DshellKeys.dshell_operators import dshell_operators


def parse(tokens: list[Token], start_node, start_parsing: int = 0) -> tuple[list[ASTNode], int]:
    """
    Parse the list of tokens and return a list of AST nodes.
    :param tokens: table of tokens
    """
    pointer = start_parsing  # pointer on token lists to track where to parse
    blocks = [start_node]  # list of block nesting to manage indentation
    tokens_by_line: list[list[Token]] = split_newlines(tokens)  # split tokens by line to facilitate parsing

    while pointer < len(tokens_by_line):

        current_line = tokens_by_line[pointer]
        first_token = current_line[0]

        if first_token.type == DTT.COMMAND:
            command_node = CommandNode(first_token.value, parse_parameters(current_line, 1))
            blocks[-1].body.append(command_node)
            pointer += 1

        elif first_token.type == DTT.KEYWORD:
            keyword_node = dshell_keyword.get(first_token.value, None)

            if keyword_node is None:
                raise SyntaxError(f"Unknown keyword: {first_token.value} at line {first_token.position[0]}, position {first_token.position[1]}")

            if keyword_node == LoopNode:
                if first_token.value.startswith("#"):
                    if not isinstance(blocks[-1], LoopNode):
                        raise SyntaxError(f'[LOOP] Unexpected end of loop at line {first_token.position[0]}, position {first_token.position[1]}')
                    # if it's an end of loop, we pop the last loop block
                    blocks.pop()
                    return blocks, pointer
                else:
                    loop_node = parse_loop_definition(first_token, current_line[1:])
                    blocks[-1].body.append(loop_node)
                    _, p = parse(tokens, loop_node, pointer + 1)
                    pointer += p + 1

    return blocks, pointer

def parse_loop_definition(token_loop: DTT.KEYWORD, tokens: list[Token]) -> LoopNode:
    """
    Parse the definition of a loop and return a LoopNode.
    :param tokens: the tokens of the line containing the loop definition
    :return: a LoopNode representing the loop definition
    """
    if len(tokens) < 1:
        raise SyntaxError(f'[LOOP] Take one (or two) argument(s) on line {token_loop.position} !')

    if len(tokens) >= 2:  # if the loop has two arguments : an ident and an iterator

        if tokens[0].type != DTT.IDENT:
            raise TypeError(f'[LOOP] the variable given must be a ident, '
                            f'not {tokens[1].type} in line {tokens[1].position}')
        if tokens[1].type not in DTT_DATA:
            raise TypeError(f'[LOOP] the iterator must be a ident, string, integer, float or list, '
                            f'not {tokens[2].type} in line {tokens[2].position}')

        loop_node = LoopNode(VarNode(tokens[0], to_postfix(tokens[1:])), body=[])

    else:
        if tokens[0].type not in DTT_DATA:
            raise TypeError(f'[LOOP] the iterator must be a ident, string, integer, float or list, '
                            f'not {tokens[0].type} in line {tokens[0].position}')

        loop_node = LoopNode(
            VarNode(Token(DTT.IDENT, "__loop__", tokens[0].position), to_postfix(tokens[0:])), body=[])

    return loop_node

def parse_parameters(tokens: list[Token], start_parsing: int) -> list[ArgsCommandNode]:
    """
    Parse the parameters of a command and return a ParamNode.
    :param tokens:
    :return:
    """
    params = []
    i = start_parsing
    while i < len(tokens):
        token = tokens[i]
        if token.type in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):
            param_name = token.value # le nom du paramètre est dans token.value, et sa valeur est dans le/les token(s) suivant
            i += 1
            param_value = tokens[i] if i < len(tokens) else []

            if token.type == DTT.PARAMETERS:
                # Handle multiple parameters separated by spaces
                i += 1
                while i < len(tokens) and tokens[i].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):
                    param_value.append(tokens[i])
                    i += 1

            params.append(ArgsCommandNode(param_name, param_value))
        else:
            params.append(ArgsCommandNode(None, tokens[i] if i < len(tokens) else []))
        i += 1
    return params



def split_newlines(tokens: list[Token]) -> list[list[Token]]:
    """
    Split a list of tokens into a list of lists of tokens, each inner list representing a line of code.
    :param tokens: the list of tokens to split
    :return: a list of lists of tokens, each inner list representing a line of code
    """
    lines = []
    current_line = []
    for token in tokens:
        if token.type == DTT.NEWLINE:
            if current_line:  # only add non-empty lines
                lines.append(current_line)
                current_line = []
        else:
            current_line.append(token)
    if current_line:  # add the last line if it's not empty
        lines.append(current_line)
    return lines

def ast_to_dict(obj):
    if isinstance(obj, list):
        return [ast_to_dict(item) for item in obj]
    elif hasattr(obj, "to_dict"):
        return obj.to_dict()
    else:
        return obj  # fallback for primitives or tokens


def dict_to_ast(data):
    """
    Convertit un dictionnaire en une structure AST.
    :param data: le dictionnaire à convertir
    :return: la structure AST correspondante
    """
    if isinstance(data, list):
        return [dict_to_ast(item) for item in data]
    elif isinstance(data, dict):
        pass


def parser_inline(tokens: list[Token]) -> tuple[list[list[Token]], bool]:
    """
    Transform a line with an inline if/else into a multi-line structure
    """
    result: list[list[Token]] = []

    try:
        if_index = next(i for i, tok in enumerate(tokens) if tok.value == 'if')
        else_index = next(i for i, tok in enumerate(tokens) if tok.value == 'else')
    except StopIteration:
        return [tokens], False  # normal line

    value_tokens = tokens[:if_index]
    condition_tokens = tokens[if_index + 1:else_index]
    else_tokens = tokens[else_index + 1:]

    # Generate:
    result.append([tokens[if_index]] + condition_tokens)  # "if cond" line
    result.append(value_tokens)  # if body
    result.append([tokens[else_index]])  # "else" line
    result.append(else_tokens)  # else body
    return result, True


def to_postfix(expression, interpreter=None):
    """
    Transform the expression into postfix notation (RPN)
    :param expression: the expression given by the tokenizer
    :param interpreter: optional interpreter instance
    :return: the expression in postfix notation
    """

    output = []
    operators: list[Token] = []

    for token in expression:
        if token.type in DTT_DATA:  # If it's an ident
            output.append(token)
        elif token.value in dshell_operators:
            while (operators and operators[-1].value in dshell_operators and
                   dshell_operators[operators[-1].value][1] >= dshell_operators[token.value][1]):
                output.append(operators.pop())
            operators.append(token)
        else:
            raise ValueError(f"Unknown token: {token}")

    while operators:
        output.append(operators.pop())

    return output
