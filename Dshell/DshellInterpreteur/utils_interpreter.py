from .dshell_arguments import DshellArguments
from ..DshellTokenizer.dshell_token_type import Token
from ..DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from ..DshellTokenizer.dshell_token_type import DTT_DATA

from ..DshellParser.ast_nodes import IfNode, ParamNode, ListNode, StrNode
from ..DshellParser.dshell_parser import to_postfix

from Dshell.full_import import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..DshellInterpreteur.dshell_interpreter import DshellInterpreteur

async def regroupe_commandes(body: list[Token], interpreter: "DshellInterpreteur", normalise: bool = False) -> DshellArguments:
    """
    Groups the command arguments in the form of a python dictionary.
    Note that you can specify the parameter you wish to pass via -- followed by the parameter name. But this is not mandatory!
    Non-mandatory parameters will be stored in a list in the form of tokens with the key \`*\`.
    The others, having been specified via a separator, will be in the form of a list of tokens with the IDENT token as key, following the separator for each argument.
    If two parameters have the same name, the last one will overwrite the previous one.
    To accept duplicates, use the SUB_SEPARATOR (~~) to create a sub-dictionary for parameters with the same name (sub-dictionary is added to the list returned).

    :param body: The list of tokens to group.
    :param interpreter: The Dshell interpreter instance.
    :param normalise: If True, normalizes the arguments (make value lowercase).
    """
    # tokens to return

    instance_dhsell_arguments = DshellArguments()
    index = 0
    n = len(body)

    while index < n:

        if normalise and hasattr(body[index], 'value') and isinstance(body[index].value, str):
                body[index].value = body[index].value.lower()

        # If the current token is the last one and is a parameter marker, add it with empty value
        if index == n - 1 and body[index].type in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):
            if body[index].type == DTT.PARAMETER:
                instance_dhsell_arguments.set_parameter(body[index].value, StrNode(''), DTT.PARAMETER)
            elif body[index].type == DTT.STR_PARAMETER:
                instance_dhsell_arguments.set_parameter(body[index].value, StrNode(''), DTT.STR_PARAMETER)
            else:  # DTT.PARAMETERS
                instance_dhsell_arguments.set_parameter(body[index].value, ListNode([]), DTT.PARAMETERS)
            index += 1
            continue

        if body[index].type == DTT.PARAMETER:

            value = ''
            current_index = index
            while (index + 1) < n and body[index + 1].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):

                value = await interpreter.eval_data_token(body[index + 1])
                index += 1
                break

            instance_dhsell_arguments.set_parameter(body[current_index].value, value, DTT.PARAMETER, obligatory=value == '*')
            index += 1

        elif body[index].type == DTT.STR_PARAMETER:

            final_argument = ''
            current_index = index

            while (index + 1) < n and body[index + 1].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):

                final_argument += body[index + 1].value + ' '
                index += 1

            instance_dhsell_arguments.set_parameter(body[current_index].value, StrNode(final_argument), type_=DTT.STR_PARAMETER)
            index += 1

        elif body[index].type == DTT.PARAMETERS:

            list_parameters = []
            current_index = index
            while (index + 1) < n and body[index + 1].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):

                list_parameters.append(await interpreter.eval_data_token(body[index + 1]))
                index += 1

            instance_dhsell_arguments.set_parameter(body[current_index].value, ListNode(list_parameters), type_=DTT.PARAMETERS)
            index += 1

        else:
            instance_dhsell_arguments.add_non_specified_parameters(await interpreter.eval_data_token(body[index]))
            index += 1

    return instance_dhsell_arguments

async def get_params(node: ParamNode, interpreter: "DshellInterpreteur") -> dict[StrNode, Any]:
    """
    Get the parameters from a ParamNode and replace their value if an input user is valide
    :param node: The ParamNode to get the parameters from.
    :param interpreter: The Dshell interpreter instance.
    :return: A dictionary of parameters.
    """

    user_input: list[str] = interpreter.vars.strip().split()
    param_node_arguments: DshellArguments = await regroupe_commandes(node.body, interpreter)
    param_node_arguments_dict: dict[str, Union[Any, None]] = param_node_arguments.get_dict_parameters()
    param_node_arguments_order: list[tuple[str, DTT]] = param_node_arguments.order

    index_user_input: int = 0
    index_order: int = 0

    while index_order < len(param_node_arguments_order) and index_user_input < len(user_input):

        # traitement des paramètres simple à tokeniser
        if param_node_arguments_order[index_order][1] == DTT.PARAMETER:
            old_index_order = index_order
            tmp_parameter = ''
            while (index_order < len(param_node_arguments_order) and
                   param_node_arguments_order[index_order][1] == DTT.PARAMETER and
                   index_user_input < len(user_input)):

                tmp_parameter += user_input[index_user_input] + ' '
                index_user_input += 1
                index_order += 1

            from ..DshellTokenizer.dshell_tokenizer import DshellTokenizer
            tmp_tokens = DshellTokenizer(tmp_parameter).start()

            if tmp_tokens and len(tmp_tokens[0]) > 0:
                for i in range(old_index_order, index_order):
                    param_node_arguments_dict[param_node_arguments_order[i][0]] = tmp_tokens[0][i]

        # traitement des paramètres à tokeniser à la chaine
        elif param_node_arguments_order[index_order][1] == DTT.PARAMETERS:
            old_index_order = index_order
            tmp_parameter = ''
            while index_user_input < len(user_input):

                tmp_parameter += user_input[index_user_input] + ' '
                index_user_input += 1

            from ..DshellTokenizer.dshell_tokenizer import DshellTokenizer
            tmp_tokens = DshellTokenizer(tmp_parameter).start()

            if tmp_tokens and len(tmp_tokens[0]) > 0:
                param_node_arguments_dict[param_node_arguments_order[old_index_order][0]] = ListNode(tmp_tokens[0])

        # traitement des paramètres à considéré comme une chaine de caractère à la chaine
        elif param_node_arguments_order[index_order][1] == DTT.STR_PARAMETER:
            old_index_order = index_order
            tmp_parameter = ''
            while index_user_input < len(user_input):

                tmp_parameter += user_input[index_user_input] + ' '
                index_user_input += 1

            param_node_arguments_dict[param_node_arguments_order[old_index_order][0]] = StrNode(tmp_parameter)

        else:
            raise Exception(f"Parameter type {param_node_arguments_order[index_order][1]} not found !\n"
                            f"Please, use : -- or --' or --*")

    param_node_arguments_dict.pop('*')
    return {StrNode(key): value for key, value in param_node_arguments_dict.items()}




async def eval_expression_inline(if_node: IfNode, interpreter: "DshellInterpreteur") -> Token:
    """
    Eval a conditional expression inline.
    :param if_node: The IfNode to evaluate.
    :param interpreter: The Dshell interpreter instance.
    """
    if await eval_expression(if_node.condition, interpreter):
        return await eval_expression(if_node.body, interpreter)
    else:
        return await eval_expression(if_node.else_body.body, interpreter)


async def eval_expression(tokens: list[Token], interpreter: "DshellInterpreteur") -> Any:
    """
    Evaluates an arithmetic and logical expression.
    :param tokens: A list of tokens representing the expression.
    :param interpreter: The Dshell interpreter instance.
    """
    from ..DshellTokenizer.dshell_keywords import dshell_operators
    postfix = to_postfix(tokens, interpreter)
    stack = []

    for token in postfix:

        if token.type in DTT_DATA:
            stack.append(await interpreter.eval_data_token(token))

        elif token.type in (DTT.MATHS_OPERATOR, DTT.LOGIC_OPERATOR, DTT.LOGIC_WORD_OPERATOR):
            op = token.value

            if op in dshell_operators:

                number_operands_min = dshell_operators[op][2]
                number_operands_max = dshell_operators[op][3]

                i = 0
                operands = []
                while len(stack) > 0 and (i != number_operands_max):
                    operands.append(stack.pop())
                    i += 1

                if len(operands) < number_operands_min:
                    raise SyntaxError(f"Not enough operands for operator '{op}'")
                elif len(operands) > number_operands_max:
                    raise SyntaxError(f"Too many operands for operator '{op}'")

                operands.reverse()
                result = dshell_operators[op][0](*operands)  # call the operator function with the operands

                stack.append(result)

        else:
            raise SyntaxError(f"Unexpected token type: {token.type} - {token.value}")

    if len(stack) != 1:
        raise SyntaxError(f"Invalid expression: missing operators or operands in expression <{' '.join((i.value for i in tokens))}>")

    return stack[0]