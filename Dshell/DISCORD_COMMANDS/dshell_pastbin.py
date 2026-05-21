from Dshell.full_import import get, Message
from .utils.utils_type_validation import _validate_required_string
from ..DshellParser.ast_nodes import StrNode, ListNode

__all__ = [
    'dshell_get_pastbin'
]


async def dshell_get_pastbin(ctx: Message, code: StrNode) -> ListNode:
    """
    Get a pastbin from a code snippet.
    """
    _CMD = "gp"

    _validate_required_string(ctx, code, _CMD)

    content = ListNode([])  # Initialize content to an empty string

    with get(f"https://pastebin.com/raw/{code}", stream=True, timeout=10) as response:

        if not response.ok:
            raise Exception(f"Failed to retrieve pastbin with code {code} !")

        for line in response.iter_lines(decode_unicode=True, chunk_size=512):
            content.add(line)

    return content
