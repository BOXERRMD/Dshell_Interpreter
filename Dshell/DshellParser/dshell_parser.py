__all__ = [
    "parse",
    "parser_inline",
    "to_postfix",
    "print_ast",
    "ast_to_dict",
]

from ..DshellTokenizer.dshell_token_type import Token
from ..DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from ..DshellTokenizer.dshell_token_type import DTT_DATA
from .ast_nodes import *


def parse(token_lines: list[list[Token]], start_node: ASTNode) -> tuple[list[ASTNode], int]:
    """
    Parse the list of tokens and return a list of AST nodes.
    :param token_lines: table of tokens
    :param start_node: the node where to start the parsing
    """
    pointer = 0  # pointer on token lists to track where to parse
    blocks = [start_node]  # list of block nesting to manage indentation
    len_token_lines = len(token_lines)

    while pointer < len_token_lines:

        tokens_by_line = token_lines[pointer]  # get the token list based on the pointer
        len_tokens_by_line = len(tokens_by_line)
        len_tokens_by_line_since_command_name = len_tokens_by_line - 1
        first_token_line = tokens_by_line[0]  # get the first token of the line
        last_block = blocks[-1]

        line = pointer+1

        if first_token_line.type == DTT.COMMAND:  # if the token is a command
            body = tokens_by_line[1:]  # get its arguments
            last_block.body.append(CommandNode(first_token_line.value,
                                               ArgsCommandNode(body, line=line), line=line))  # add the command to the last block's body

        ############################## DSHELL KEYWORDS ##############################

        elif first_token_line.type == DTT.KEYWORD:  # if it's a keyword

            if first_token_line.value == 'if':  # if it's a condition
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[IF] Take one or more arguments on line {first_token_line.position} !')

                if_node = IfNode(condition=tokens_by_line[1:],
                                 body=[], line=line)  # create the node with the if condition arguments
                last_block.body.append(if_node)
                _, p = parse(token_lines[pointer + 1:],
                             if_node)  # parse the rest of the code with if_node as the start of the new parsing
                pointer += p + 1  # essential to not parse already processed lines

            elif first_token_line.value == '#if':
                if not isinstance(last_block, (IfNode, ElseNode, ElifNode)):
                    raise SyntaxError(f'[#IF] No conditional bloc open on line {first_token_line.position} !')

                if isinstance(last_block, (ElifNode, ElseNode)):

                    while isinstance(last_block, (ElifNode, ElseNode)):
                        blocks.pop()
                        last_block = blocks[-1]
                blocks.pop()
                return blocks, pointer

            elif first_token_line.value == 'elif':
                if not isinstance(last_block, (IfNode, ElifNode)):
                    raise SyntaxError(f'[ELIF] No conditional bloc open on line {first_token_line.position} !')
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[ELIF] Take one or more arguments on line {first_token_line.position} !')
                elif_node = ElifNode(condition=tokens_by_line[1:], body=[],
                                     parent=last_block if isinstance(last_block, IfNode) else last_block.parent, line=line)

                if isinstance(last_block, ElifNode):
                    last_block.parent.elif_nodes.append(elif_node)
                else:
                    if last_block.elif_nodes is None:
                        last_block.elif_nodes = [elif_node]
                    else:
                        last_block.elif_nodes.append(elif_node)
                blocks.append(elif_node)

            elif first_token_line.value == 'else':
                if not isinstance(last_block, (IfNode, ElifNode)):
                    raise SyntaxError(f'[ELSE] No conditional bloc open on line {first_token_line.position} !')

                if isinstance(last_block, ElseNode) and last_block.else_body is not None:
                    raise SyntaxError(f'[ELSE] already define !')

                else_node = ElseNode(body=[], line=line)
                if isinstance(last_block, ElifNode):  # if the last block is an elif
                    last_block.parent.else_body = else_node  # add the else block to its parent (which is the last if)
                else:
                    last_block.else_body = else_node  # once parsing is done, add it to the last block
                blocks.append(else_node)

            elif first_token_line.value == 'loop':

                if len_tokens_by_line <= 1:
                    raise SyntaxError(f'[LOOP] Take one (or two) argument(s) on line {first_token_line.position} !')

                if len_tokens_by_line_since_command_name >= 2: # if the loop has two arguments : an ident and an iterator

                    if tokens_by_line[1].type != DTT.IDENT:
                        raise TypeError(f'[LOOP] the variable given must be a ident, '
                                        f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')
                    if tokens_by_line[2].type not in DTT_DATA:
                        raise TypeError(f'[LOOP] the iterator must be a ident, string, integer, float or list, '
                                        f'not {tokens_by_line[2].type} in line {tokens_by_line[2].position}')

                    loop_node = LoopNode(VarNode(tokens_by_line[1], to_postfix(tokens_by_line[2:]), line=line), body=[], line=line)
                    last_block.body.append(loop_node)
                    _, p = parse(token_lines[pointer + 1:],
                                 loop_node)  # parse everything after the loop instruction
                    pointer += p + 1

                else:
                    if tokens_by_line[1].type not in DTT_DATA:
                        raise TypeError(f'[LOOP] the iterator must be a ident, string, integer, float or list, '
                                        f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                    loop_node = LoopNode(VarNode(Token(DTT.IDENT, "__loop__", tokens_by_line[1].position), to_postfix(tokens_by_line[1:]), line=line), body=[], line=line)
                    last_block.body.append(loop_node)
                    _, p = parse(token_lines[pointer + 1:],
                                 loop_node)  # parse everything after the loop instruction
                    pointer += p + 1

            elif first_token_line.value == '#loop':  # if encountered
                if not isinstance(last_block, LoopNode):
                    raise SyntaxError(f'[#LOOP] No loop open on line {first_token_line.position} !')

                blocks.pop()
                return blocks, pointer  # return the parsed information to the last opened loop

            elif first_token_line.value == 'var':
                if len(tokens_by_line) <= 2:
                    raise SyntaxError(f'[VAR] Take two arguments on line {first_token_line.position} !')
                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[VAR] the variable given must be a ident, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                var_node = VarNode(name=tokens_by_line[1], body=[], line=line)
                last_block.body.append(var_node)
                result, status = parser_inline(tokens_by_line[
                                               2:])  # separate tokens on the line by newlines at each condition/else
                if status:
                    parse(result, var_node)  # parse everything in the variable
                else:
                    # var_node.body = parse(result, StartNode([]))[0][0].body
                    var_node.body = result[0]

            elif first_token_line.value == 'sleep':
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[SLEEP] Take one arguments on line {first_token_line.position} !')
                if tokens_by_line[1].type != DTT.INT:
                    raise TypeError(f'[SLEEP] the variable given must be an integer, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                sleep_node = SleepNode(tokens_by_line[1:], line=line)
                last_block.body.append(sleep_node)

            elif first_token_line.value == 'param':

                param_node = ParamNode(body=[], line=line)
                last_block.body.append(param_node)
                _, p = parse(token_lines[pointer + 1:], param_node)
                pointer += p + 1  # advance the pointer to the next line

            elif first_token_line.value == '#param':
                if not isinstance(last_block, ParamNode):
                    raise SyntaxError(f'[#PARAM] No parameters open on line {first_token_line.position} !')

                blocks.pop()  # remove the last block (the parameter)
                return blocks, pointer  # return the parsed information to the last opened parameter

            elif first_token_line.value == 'code':

                if len(tokens_by_line) < 2:
                    raise SyntaxError(f"[CODE] take one argument on line {first_token_line.position}")

                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[CODE] the variable given must be a ident, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                code_node = CodeNode(body=[], line=line)
                var_node = VarNode(tokens_by_line[1], [code_node], line=line)
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointer + 1:], code_node)
                pointer += p + 1

            elif first_token_line.value == '#code':
                if not isinstance(last_block, CodeNode):
                    raise SyntaxError(f"[#CODE] No code open on line {first_token_line.position}")

                blocks.pop()
                return blocks, pointer

            elif first_token_line.value == 'eval':
                if len(tokens_by_line) < 2:
                    raise SyntaxError(f"[EVAL] take one or more arguments on line {first_token_line.position}")

                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[EVAL] the first variable given must be a ident (CodeNode), '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                eval_node = EvalNode(codeNode=tokens_by_line[1], argsNode=ArgsCommandNode(tokens_by_line[2:], line=line), line=line)
                last_block.body.append(eval_node)

            elif first_token_line.value == 'return':
                if not isinstance(last_block, CodeNode):
                    raise SyntaxError(f"[RETURN] No code open on line {first_token_line.position} !")
                if len(tokens_by_line) < 2:
                    raise SyntaxError(f"[RETURN] take one or more arguments on line {first_token_line.position}")

                return_node = ReturnNode(body=tokens_by_line[1:], line=line)
                last_block.body.append(return_node)

            elif first_token_line.value == 'scan':
                scan_node = ScanNode(ArgsCommandNode(body=tokens_by_line[1:], line=line), line=line)
                last_block.body.append(scan_node)

            elif first_token_line.value == '#end':  # node pour arrêter le programme si elle est rencontré
                error_message = True
                if len(tokens_by_line) > 1:
                    if tokens_by_line[1].type != DTT.BOOL:
                        raise TypeError(f'[#END] the variable given must be a boolean, not {tokens_by_line[1].type}')
                    else:
                        error_message = tokens_by_line[1]
                end_node = EndNode(error_message)
                last_block.body.append(end_node)

        ############################## DISCORD KEYWORDS ##############################

        elif first_token_line.type == DTT.DISCORD_KEYWORD:

            if first_token_line.value == 'embed':
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[EMBED] Take one or more arguments on line {first_token_line.position} !')
                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[EMBED] the variable given must be a ident, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                embed_node = EmbedNode(body=[], fields=[], line=line)
                var_node = VarNode(tokens_by_line[1], body=[embed_node], line=line)
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointer + 1:], embed_node)
                pointer += p + 1

            elif first_token_line.value == '#embed':
                if not isinstance(last_block, EmbedNode):
                    raise SyntaxError(f'[#EMBED] No embed open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointer

            elif first_token_line.value == 'field':
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[FIELD] Take one or more arguments on line {first_token_line.position} !')
                if not isinstance(last_block, EmbedNode):
                    raise SyntaxError(f'[FIELD] No embed open on line {first_token_line.position} !')

                last_block.fields.append(FieldEmbedNode(tokens_by_line[1:], line=line))

            elif first_token_line.value in ('perm', 'permission'):
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[PERM] Take one argument on line {first_token_line.position} !')
                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[PERM] the variable given must be a ident, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                perm_node = PermissionNode(body=[], line=line)
                var_node = VarNode(tokens_by_line[1], body=[perm_node], line=line)
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointer + 1:], perm_node)
                pointer += p + 1

            elif first_token_line.value in ('#perm', '#permission'):
                if not isinstance(last_block, PermissionNode):
                    raise SyntaxError(f'[#PERM] No permission open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointer

            elif first_token_line.value == 'button':
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[BUTTON] Take one or more arguments on line {first_token_line.position} !')
                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[BUTTON] the variable given must be a ident, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                button_node = UiButtonNode([], line=line)
                var_node = VarNode(tokens_by_line[1], body=[button_node], line=line)
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointer + 1:], button_node)
                pointer += p + 1

            elif first_token_line.value == '#button':
                if not isinstance(last_block, UiButtonNode):
                    raise SyntaxError(f'[#BUTTON] No UIButton open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointer

            elif first_token_line.value == 'select':
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[SELECT] Take one or more arguments on line {first_token_line.position} !')
                if tokens_by_line[1].type != DTT.IDENT:
                    raise TypeError(f'[SELECT] the variable given must be a ident, '
                                    f'not {tokens_by_line[1].type} in line {tokens_by_line[1].position}')

                select_node = UiSelectNode([], line=line)
                var_node = VarNode(tokens_by_line[1], body=[select_node], line=line)
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointer + 1:], select_node)
                pointer += p + 1

            elif first_token_line.value == '#select':
                if not isinstance(last_block, UiSelectNode):
                    raise SyntaxError(f'[#SELECT] No UISelect open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointer

            elif first_token_line.value == 'option':
                if len(tokens_by_line) <= 1:
                    raise SyntaxError(f'[OPTION] Take one or more arguments on line {first_token_line.position} !')
                if not isinstance(last_block, UiSelectNode):
                    raise SyntaxError(f'[OPTION] No UISelect open on line {first_token_line.position} !')

                last_block.options.append(OptionUiSelectNode(tokens_by_line[1:], line=line))

        ############################## AUTRE ##############################

        elif first_token_line.type in DTT_DATA:  # if the line starts with a data token, we consider it as a command with an implicit "sm" name
            for token in tokens_by_line:

                if token.type in DTT_DATA:
                    last_block.body.append(CommandNode(name='sm', body=ArgsCommandNode([token], line=line), line=line))

        else:
            last_block.body += tokens_by_line

        pointer += 1

    return blocks, pointer


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
    from Dshell.DshellTokenizer import dshell_operators

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


def print_ast(ast: list[ASTNode], decalage: int = 0):
    for i in ast:

        if isinstance(i, StartNode):
            print_ast(i.body, decalage)

        if isinstance(i, LoopNode):
            print(f"{' ' * decalage}LOOP -> {i.variable.name} : {i.variable.body}")
            print_ast(i, decalage + 5)

        elif isinstance(i, IfNode):
            print(f"{' ' * decalage}IF -> {i.condition}")
            print_ast(i, decalage + 5)

            if i.elif_nodes is not None:
                for elif_body in i.elif_nodes:
                    print(f"{' ' * decalage}ELIF -> {elif_body.condition}")
                    print_ast(elif_body, decalage + 5)

            if i.else_body is not None:
                print(f"{' ' * decalage}ELSE -> ...")
                print_ast(i.else_body, decalage + 5)

        elif isinstance(i, CommandNode):
            print(f"{' ' * decalage}COMMAND -> {i.name} : {i.body}")

        elif isinstance(i, VarNode):
            print(f"{' ' * decalage}VAR -> {i.name} : {i.body}")

        elif isinstance(i, EmbedNode):
            print(f"{' ' * decalage}EMBED :")
            print_ast(i.fields, decalage + 5)

        elif isinstance(i, FieldEmbedNode):
            for field in i.body:
                print(f"{' ' * decalage}FIELD -> {field.value}")

        elif isinstance(i, PermissionNode):
            print(f"{' ' * decalage}PERMISSION -> {i.body}")

        elif isinstance(i, ParamNode):
            print(f"{' ' * decalage}PARAM -> {i.body}")


        elif isinstance(i, UiButtonNode):
            print(f"{' ' * decalage}BUTTON -> {i.body}")

        elif isinstance(i, UiSelectNode):
            print(f"{' ' * decalage}SELECT -> {i.body}")

        elif isinstance(i, SleepNode):
            print(f"{' ' * decalage}SLEEP -> {i.body}")

        elif isinstance(i, EndNode):
            print(f"{' ' * decalage}END -> ...")

        else:
            print(f"{' ' * decalage}UNKNOWN NODE {i}")