from requests import get
from Dshell.full_import import Message
from .utils.utils_type_validation import _validate_required_string
from ..DshellParser.ast_nodes import StrNode, BoolNode, ListNode, FileNode
from .dshell_file import dshell_write_file

__all__ = [
    'dshell_get_pastbin'
]


async def dshell_get_pastbin(ctx: Message, code: StrNode) -> FileNode:
    """
    Get a pastbin from a code snippet.
    Return a FileNode to stream the result
    """
    _CMD = "gp"

    _validate_required_string(code, "code", _CMD)

    content = FileNode(name=StrNode(f"Pastbin {code}"))

    with get(f"https://pastebin.com/raw/{code}", stream=True, timeout=10) as response:

        if not response.ok:
            raise Exception(f"Failed to retrieve pastbin with code {code} !")

        for line in response.iter_lines(decode_unicode=True, chunk_size=1024):
            await dshell_write_file(ctx, StrNode(line), append=BoolNode(1), file=content)

    return content
