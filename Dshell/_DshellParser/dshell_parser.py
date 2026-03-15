__all__ = [
    "parse",
    "parser_inline",
    "to_postfix",
    "ast_to_dict",
]

from typing import Union

from .ast_nodes import *
from .._DshellKeys.dshell_keywords import dshell_keyword, dshell_discord_keyword
from .._DshellTokenizer.dshell_token_type import Token
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from .._DshellTokenizer.dshell_token_type import DTT_DATA
from .._DshellKeys.dshell_operators import dshell_operators

marker_parameter = {DTT.STR_PARAMETER, DTT.PARAMETERS, DTT.PARAMETER}

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

            elif keyword_node == IfNode:
                if first_token.value.startswith("#"):
                    if not isinstance(blocks[-1], (IfNode, ElifNode, ElseNode)):
                        raise SyntaxError(f'[IF] Unexpected end of if block at line {first_token.position[0]}, position {first_token.position[1]}')
                    # if it's an end of if, we pop the last if block
                    blocks.pop()
                    return blocks, pointer
                else:
                    if_node = IfNode(to_postfix(current_line[1:]), body=[])
                    blocks[-1].body.append(if_node)
                    blocks.append(if_node)
                    pointer += 1

            elif keyword_node == ElifNode:
                if not isinstance(blocks[-1], IfNode):
                    raise SyntaxError(f'[ELIF] Unexpected elif without a preceding if at line {first_token.position[0]}, position {first_token.position[1]}')
                # we pop the last if/elif block and create a new one for the elif
                blocks.pop()
                elif_node = ElifNode(to_postfix(current_line[1:]), body=[], parent=blocks[-1])
                blocks[-1].elif_node.append(elif_node)
                blocks.append(elif_node)
                pointer += 1

            elif keyword_node == ElseNode:
                if not isinstance(blocks[-1], (IfNode, ElifNode)):
                    raise SyntaxError(f'[ELSE] Unexpected else without a preceding if at line {first_token.position[0]}, position {first_token.position[1]}')
                # we pop the last if/elif block and create a new one for the else
                blocks.pop()
                else_node = ElseNode(body=[])
                blocks[-1].body.append(else_node)
                blocks.append(else_node)
                pointer += 1

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
        if token.type in marker_parameter:
            param_name = token.value # le nom du paramètre est dans token.value, et sa valeur est dans le/les token(s) suivant
            i += 1
            param_value = [tokens[i]] if i < len(tokens) else []

            if token.type == DTT.PARAMETERS:
                # Handle multiple parameters separated by spaces
                i += 1
                temp_ident = i
                while temp_ident < len(tokens) and tokens[temp_ident].type not in marker_parameter:
                    param_value.append(tokens[temp_ident])
                    temp_ident += 1

            parse_result = parse_arguments(param_value)
            params.append(ArgsCommandNode(param_name, parse_result))
            i += len(parse_result)
        else:
            tokens_to_parse = []
            temp_ident = i
            while temp_ident < len(tokens) and tokens[temp_ident].type not in marker_parameter:
                tokens_to_parse.append(tokens[temp_ident])
                temp_ident += 1
            parse_result = parse_arguments(tokens_to_parse)
            params.append(ArgsCommandNode(None, parse_result))
            i = temp_ident
    return params


def parse_encapsulated(tokens: list[Token],
                       start_node,
                       start_parsing: int) -> tuple[list[Union[ListNode, EvalExpressionNode, EvalGroupNode]], int]:
    """
        Parse encapsulated structures (parentheses, brackets, braces) and return a list of AST nodes representing these structures.
    :param tokens:
    :return:
    """
    result: list[Union[ListNode, EvalExpressionNode, EvalGroupNode]] = [start_node]
    pointer: int = start_parsing
    while pointer < len(tokens):
        token = tokens[pointer]
        if token.type == DTT.R_LIST:
            list_node = ListNode([])
            result[-1].body.append(list_node)
            _, p = parse_encapsulated(tokens, list_node, pointer + 1)
            pointer += p + 1

        elif token.type == DTT.L_LIST:
            if not isinstance(result[-1], ListNode):
                raise SyntaxError(f"Unexpected closing bracket at line {token.position[0]}, position {token.position[1]}")
            result.pop()  # we pop the last list node, which is now complete
            return result, pointer

        elif token.type == DTT.R_EVAL_EXPRESSION:
            eval_node = EvalExpressionNode([])
            result[-1].body.append(eval_node)
            eval_tokens_after_paring, p = parse_encapsulated(tokens, eval_node, pointer + 1)
            eval_node.expression = to_postfix(eval_tokens_after_paring)
            pointer += p + 1

        elif token.type == DTT.EVAL_GROUP:
            start_eval_group_node = StartNode([])
            result_parsing_eval_group, p = parse(tokens, start_eval_group_node, pointer + 1)
            if len(result_parsing_eval_group) != 1:
                raise SyntaxError(f"Unexpected number of nodes in eval group at line {token.position[0]}, position {token.position[1]}")
            eval_group_node = EvalGroupNode(result_parsing_eval_group[0])
            result[-1].body.append(eval_group_node)
            pointer += p + 1

        else:
            if token.type in DTT_DATA:
                result[-1].body.append(token)
            pointer += 1

    return result, pointer

def parse_arguments(tokens: list[Token]) -> list[Union[ListNode, EvalExpressionNode, EvalGroupNode, Token]]:
    """
    Parse the arguments of a command and return a list of AST nodes representing these arguments.
    :param tokens:
    :return:
    """
    result: list[Union[ListNode, EvalExpressionNode, EvalGroupNode, Token]] = []
    pointer: int = 0
    while pointer < len(tokens):
        token = tokens[pointer]
        if token.type in DTT_DATA:
            result.append(token)
            pointer += 1
        elif token.type in (DTT.R_LIST, DTT.R_EVAL_EXPRESSION, DTT.EVAL_GROUP):
            start_node = StartNode([])
            _, p = parse_encapsulated(tokens, start_node, pointer)
            result.extend(start_node.body)  # we skip the start node
            pointer += p + 1

        else:
            pointer += 1

    return result

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
