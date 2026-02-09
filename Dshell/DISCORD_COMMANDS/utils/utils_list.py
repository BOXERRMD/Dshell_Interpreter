__all__ = [
    "utils_list_add",
    "utils_list_remove",
    "utils_list_clear",
    "utils_list_pop",
    "utils_list_sort",
    "utils_list_reverse",
    "utils_list_get_value",
]

from ..._DshellParser.ast_nodes import ListNode

from .utils_type_validation import (_validate_required_list_node,
                                    _validate_required_int,
                                    _validate_required_bool)

async def utils_list_add(ctx, value: ListNode, *elements):
    """
    Add an element to a list
    :param value:
    :param elements:
    :return:
    """
    _validate_required_list_node(value, "value", "add")

    for elem in elements:
            value.add(elem)

    return value

async def utils_list_remove(ctx, value: ListNode, element, count: int = 1):
    """
    Remove an element from a list
    :param value:
    :param element:
    :param count:
    :return:
    """
    _validate_required_list_node(value, "value", "remove")

    value.remove(element, count)
    return value

async def utils_list_clear(ctx, value: ListNode):
    """
    Clear a list
    :param value:
    :return:
    """
    _validate_required_list_node(value, "value", "clear")
    value.clear()
    return value

async def utils_list_pop(ctx, value: ListNode, index: int = -1):
    """
    Pop an element from a list
    :param value:
    :param index:
    :return:
    """
    _validate_required_list_node(value, "value", "pop")
    _validate_required_int(index, "index", "pop")
    return value.pop(index)

async def utils_list_sort(ctx, value: ListNode, reverse: bool = False):
    """
    Sort a list
    :param value:
    :param reverse:
    :return:
    """
    _validate_required_list_node(value, "value", "sort")
    _validate_required_bool(reverse, "reverse", "sort")
    value.sort(reverse=reverse)
    return value

async def utils_list_reverse(ctx, value: ListNode):
    """
    Reverse a list
    :param value:
    :return:
    """
    _validate_required_list_node(value, "value", "reverse")
    value.reverse()
    return value

async def utils_list_get_value(ctx, value: ListNode, index: int = 0):
    """
    Get a value from a list
    :param value:
    :param index:
    :return:
    """
    _validate_required_list_node(value, "value", "get")
    _validate_required_int(index, "index", "get")
    return value[index]