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
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to an integer")

async def utils_convert_to_float(ctx: Message, value: Any) -> float:
    """
    Convert any value to a float
    :param ctx:
    :param value:
    :return:
    """
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to a float")