__all__ = [
    "utils_split_string",
    "utils_upper_string",
    "utils_lower_string",
    "utils_title_string",
    "utils_strip_string",
    "utils_replace_string"
]

from discord import Message

async def utils_split_string(ctx: Message, value: str, separator: str = ' ') -> "ListNode":
    """
    Split a string into a list of strings using the specified separator.
    :param value:
    :param separator:
    :return:
    """

    if not isinstance(value, str):
        raise TypeError(f"value must be a str in split command, not {type(value)}")

    if not isinstance(separator, str):
        raise TypeError(f"separator must be a str in split command, not {type(separator)}")

    from ..._DshellParser.ast_nodes import ListNode

    return ListNode(value.split(separator))

async def utils_upper_string(ctx: Message, value: str) -> str:
    """
    Convert a string to uppercase.
    :param value:
    :return:
    """

    if not isinstance(value, str):
        raise TypeError(f"value must be a str in upper command, not {type(value)}")

    return value.upper()

async def utils_lower_string(ctx: Message, value: str) -> str:
    """
    Convert a string to lowercase.
    :param value:
    :return:
    """

    if not isinstance(value, str):
        raise TypeError(f"value must be a str in lower command, not {type(value)}")

    return value.lower()

async def utils_title_string(ctx: Message, value: str) -> str:
    """
    Convert a string to title case.
    :param value:
    :return:
    """

    if not isinstance(value, str):
        raise TypeError(f"value must be a str in title command, not {type(value)}")

    return value.title()

async def utils_strip_string(ctx: Message, value: str) -> str:
    """
    Strip whitespace from the beginning and end of a string.
    :param value:
    :return:
    """

    if not isinstance(value, str):
        raise TypeError(f"value must be a str in strip command, not {type(value)}")

    return value.strip()

async def utils_replace_string(ctx: Message, value: str, old: str, new: str) -> str:
    """
    Replace all occurrences of old with new in a string.
    :param value:
    :param old:
    :param new:
    :return:
    """

    if not isinstance(value, str):
        raise TypeError(f"value must be a str in replace command, not {type(value)}")

    if not isinstance(old, str):
        raise TypeError(f"old must be a str in replace command, not {type(old)}")

    if not isinstance(new, str):
        raise TypeError(f"new must be a str in replace command, not {type(new)}")

    return value.replace(old, new)