__all__ = [
    "utils_split_string",
    "utils_upper_string",
    "utils_lower_string",
    "utils_title_string",
    "utils_strip_string",
    "utils_replace_string",
    "utils_regex_findall",
    "utils_regex_sub",
    "utils_regex_search",
    "utils_regex_group"
]

from Dshell.full_import import Message
from ..._DshellParser.ast_nodes import ListNode
from Dshell.full_import import (search,
                            sub,
                            findall)


def _validate_string_type(value, param_name: str, command_name: str):
    """
    Validate that a value is a string type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages
    :raises TypeError: If the value is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"{param_name} must be a str in {command_name} command, not {type(value)}")


async def utils_split_string(ctx: Message, value: str, separator: str = ' ') -> ListNode:
    """
    Split a string into a list of strings using the specified separator.
    :param ctx: Discord message context
    :param value: String to split
    :param separator: Separator to use for splitting
    :return: ListNode containing split strings
    """
    _validate_string_type(value, 'value', 'split')
    _validate_string_type(separator, 'separator', 'split')
    return ListNode(value.split(separator))


async def utils_upper_string(ctx: Message, value: str) -> str:
    """
    Convert a string to uppercase.
    :param ctx: Discord message context
    :param value: String to convert
    :return: Uppercase string
    """
    _validate_string_type(value, 'value', 'upper')
    return value.upper()


async def utils_lower_string(ctx: Message, value: str) -> str:
    """
    Convert a string to lowercase.
    :param ctx: Discord message context
    :param value: String to convert
    :return: Lowercase string
    """
    _validate_string_type(value, 'value', 'lower')
    return value.lower()


async def utils_title_string(ctx: Message, value: str) -> str:
    """
    Convert a string to title case.
    :param ctx: Discord message context
    :param value: String to convert
    :return: Title case string
    """
    _validate_string_type(value, 'value', 'title')
    return value.title()


async def utils_strip_string(ctx: Message, value: str) -> str:
    """
    Strip whitespace from the beginning and end of a string.
    :param ctx: Discord message context
    :param value: String to strip
    :return: Stripped string
    """
    _validate_string_type(value, 'value', 'strip')
    return value.strip()


async def utils_replace_string(ctx: Message, value: str, old: str, new: str) -> str:
    """
    Replace all occurrences of old with new in a string.
    :param ctx: Discord message context
    :param value: String to perform replacement on
    :param old: Substring to replace
    :param new: Replacement string
    :return: String with replacements applied
    """
    _validate_string_type(value, 'value', 'replace')
    _validate_string_type(old, 'old', 'replace')
    _validate_string_type(new, 'new', 'replace')
    return value.replace(old, new)


async def utils_regex_findall(ctx: Message, regex: str, content: str = None) -> ListNode:
    """
    Find all occurrences of a regex in a string.
    :param ctx: Discord message context
    :param regex: Regular expression pattern
    :param content: Content to search (defaults to message content)
    :return: ListNode of ListNode of each group in the regex
    """
    _validate_string_type(regex, 'regex', 'regex_findall')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_findall')

    result = findall(regex, content if content is not None else ctx.content)
    return ListNode([list(i) for i in result])


async def utils_regex_sub(ctx: Message, regex: str, replace: str, content: str = None) -> str:
    """
    Replace all occurrences of a regex in a string with a replacement string.
    :param ctx: Discord message context
    :param regex: Regular expression pattern
    :param replace: Replacement string
    :param content: Content to search (defaults to message content)
    :return: String with replacements applied
    """
    _validate_string_type(regex, 'regex', 'regex_sub')
    _validate_string_type(replace, 'replacement', 'regex_sub')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_sub')

    return sub(regex, replace, content if content is not None else ctx.content)


async def utils_regex_search(ctx: Message, regex: str, content: str = None) -> str:
    """
    Search for a regex in a string.
    :param ctx: Discord message context
    :param regex: Regular expression pattern
    :param content: Content to search (defaults to message content)
    :return: Matched string or empty string if no match
    """
    _validate_string_type(regex, 'regex', 'regex_search')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_search')

    result = search(regex, content if content is not None else ctx.content)
    return result.group() if result else ''


async def utils_regex_group(ctx: Message, regex: str, content: str = None) -> ListNode:
    """
    Search for a regex in a string and return the groups.
    :param ctx: Discord message context
    :param regex: Regular expression pattern
    :param content: Content to search (defaults to message content)
    :return: ListNode of matched groups
    """
    _validate_string_type(regex, 'regex', 'regex_group')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_group')

    result = search(regex, content if content is not None else ctx.content)
    return ListNode(list(result.groups())) if result else ListNode([])