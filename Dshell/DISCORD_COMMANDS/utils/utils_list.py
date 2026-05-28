__all__ = [
    "utils_convert_to_list",
    "utils_list_add",
    "utils_list_remove",
    "utils_list_clear",
    "utils_list_set_value",
    "utils_list_pop",
    "utils_list_sort",
    "utils_list_reverse",
    "utils_list_get_value",
]

from ...DshellParser.ast_nodes import ListNode, UiButtonNode, UiSelectNode, CodeNode, StrNode, IntNode, FloatNode, BoolNode
from ...full_import import Union
from .utils_type_validation import (_validate_required_list_node,
                                    _validate_required_int,
                                    _validate_required_bool,
                                    _validate_optional_bool)

async def utils_convert_to_list(ctx,
                                value: Union[StrNode, IntNode, FloatNode, UiButtonNode, UiSelectNode, CodeNode],
                                split: BoolNode = BoolNode(0)):
    """
    Make a list with any value
    :param ctx:
    :param value:
    :param split: split the value into list
    :return:
    """
    _CMD = 'list'
    _validate_optional_bool(split, "split", _CMD)

    if isinstance(value, StrNode):
        if split:
            return ListNode([i for i in value])
        return ListNode([value])

    elif isinstance(value, IntNode):
        if split:
            l = ListNode([])
            while value != 0:
                l.add(value % 10)
                value //= 10
            return l
        return ListNode([value])

    else:
        return ListNode([value])



async def utils_list_add(ctx, value: ListNode, *elements):
    """
    Ajoute un ou plusieurs éléments à une liste Dshell.
    
    Cette fonction modifie la liste en place en ajoutant tous les éléments fournis
    à la fin de la liste.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste à laquelle ajouter des éléments
    :type value: ListNode
    :param elements: Un ou plusieurs éléments à ajouter
    :return: La liste modifiée
    :rtype: ListNode
    :raises TypeError: Si value n'est pas un ListNode
    
    Example:
        >>> my_list = ListNode([1, 2, 3])
        >>> await utils_list_add(ctx, my_list, 4, 5)
        ListNode([1, 2, 3, 4, 5])
    """
    _CMD = "add"
    _validate_required_list_node(value, "value", _CMD)

    for elem in elements:
            value.add(elem)

    return value

async def utils_list_remove(ctx, value: ListNode, element, count: IntNode = IntNode(1)):
    """
    Retire une ou plusieurs occurrences d'un élément d'une liste Dshell.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste dont retirer l'élément
    :type value: ListNode
    :param element: L'élément à retirer
    :param count: Nombre d'occurrences à retirer (par défaut: 1)
    :type count: int
    :return: La liste modifiée
    :rtype: ListNode
    """
    _CMD = "remove"
    _validate_required_list_node(value, "value", _CMD)

    value.remove(element, count)
    return value

async def utils_list_clear(ctx, value: ListNode):
    """
    Vide complètement une liste Dshell.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste à vider
    :type value: ListNode
    :return: La liste vide
    :rtype: ListNode
    """
    _CMD = "clear"
    _validate_required_list_node(value, "value", _CMD)
    value.clear()
    return value

async def utils_list_pop(ctx, value: ListNode, index: IntNode = IntNode(-1)):
    """
    Retire et retourne un élément d'une liste à l'index spécifié.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste dont retirer l'élément
    :type value: ListNode
    :param index: Index de l'élément à retirer (par défaut: -1 pour le dernier)
    :type index: int
    :return: L'élément retiré
    """
    _CMD = "pop"
    _validate_required_list_node(value, "value", _CMD)
    _validate_required_int(index, "index", _CMD)
    return value.pop(index)

async def utils_list_sort(ctx, value: ListNode, reverse: BoolNode = BoolNode(0)):
    """
    Trie une liste Dshell en place.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste à trier
    :type value: ListNode
    :param reverse: Si True, trie en ordre décroissant (par défaut: False)
    :type reverse: bool
    :return: La liste triée
    :rtype: ListNode
    """
    _CMD = "sort"
    _validate_required_list_node(value, "value", _CMD)
    _validate_required_bool(reverse, "reverse", _CMD)
    value.sort(reverse=reverse)
    return value

async def utils_list_reverse(ctx, value: ListNode):
    """
    Inverse l'ordre des éléments d'une liste Dshell en place.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste à inverser
    :type value: ListNode
    :return: La liste inversée
    :rtype: ListNode
    """
    _CMD = "reverse"
    _validate_required_list_node(value, "value", _CMD)
    value.reverse()
    return value

async def utils_list_get_value(ctx, value: ListNode, index: IntNode = IntNode(0)):
    """
    Récupère un élément d'une liste Dshell à l'index spécifié.
    
    :param ctx: Le contexte du message Discord
    :param value: La liste dont récupérer l'élément
    :type value: ListNode
    :param index: Index de l'élément à récupérer (par défaut: 0)
    :type index: int
    :return: L'élément à l'index spécifié
    :raises IndexError: Si l'index est hors limites
    """
    _CMD = "get"
    _validate_required_list_node(value, "value", _CMD)
    _validate_required_int(index, "index", _CMD)
    return value[index]

async def utils_list_set_value(ctx, value: ListNode, index: IntNode, new_value):
    """
    Set an element in a list
    :param ctx:
    :param value:
    :param index:
    :param new_value:
    :return:
    """
    _CMD = "set"
    _validate_required_list_node(value, "value", _CMD)
    _validate_required_int(index, "index", _CMD)

    value.set(index, new_value)

    return value
