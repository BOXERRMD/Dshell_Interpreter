__all__ = [
    "utils_convert_to_int",
    "utils_convert_to_float",
]

from ...full_import import Any, Message
from ...DshellParser.ast_nodes import IntNode, FloatNode

async def utils_convert_to_int(ctx: Message, value: Any) -> IntNode:
    """
    Convert any value to an integer
    :param ctx:
    :param value:
    :return:
    """
    try:
        return IntNode(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to an integer")

async def utils_convert_to_float(ctx: Message, value: Any) -> FloatNode:
    """
    Convert any value to a float
    :param ctx:
    :param value:
    :return:
    """
    try:
        return FloatNode(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to a float")