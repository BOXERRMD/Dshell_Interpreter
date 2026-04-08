__all__ = [
    "utils_convert_to_int",
    "utils_convert_to_float",
]

from ...full_import import Any, Message

async def utils_convert_to_int(ctx: Message, value: Any) -> int:
    """
    Convert any value to an integer
    :param ctx:
    :param value:
    :return:
    """
    return int(value)

async def utils_convert_to_float(ctx: Message, value: Any) -> float:
    """
    Convert any value to a float
    :param ctx:
    :param value:
    :return:
    """
    return float(value)