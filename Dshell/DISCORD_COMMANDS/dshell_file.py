from ..full_import import Message, Union, PartialMessage, Optional
from ..DshellParser.ast_nodes import ListNode, FileNode, StrNode, BoolNode, IntNode

from .utils.utils_message import utils_get_message
from .utils.utils_type_validation import (_validate_required_file_node,
                                          _validate_required_string,
                                          _validate_optional_string,
                                          _validate_required_bool)

__all__ = [
    "dshell_get_message_files",
    "dshell_write_file",
    "dshell_read_file",
]

async def dshell_get_message_files(ctx: Message, message: Union[StrNode, IntNode]) -> ListNode:
    """
    Récupère les fichiers d'un message
    :param ctx:
    :param message:
    :return:
    """

    target_message = ctx if message is None else utils_get_message(ctx, message)

    attachments_list: ListNode = ListNode([])

    if isinstance(target_message, PartialMessage):
        target_message = await target_message.fetch()

    for attachment in target_message.attachments:
        if attachment.content_type is not None and attachment.content_type.startswith("text/"):
            file = FileNode(name=attachment.filename,
                            description=attachment.description,
                            spoiler=attachment.is_spoiler())
            file.write(bytearray(await attachment.read()), append=False)
            attachments_list.add(file)

    return attachments_list

async def dshell_read_file(ctx: Message, file: FileNode) -> StrNode:
    """
    Lit en entier un fichier
    :param ctx:
    :param file:
    :return:
    """
    _CMD = "rf"
    _validate_required_file_node(file, 'file', _CMD)

    return file.read()

async def dshell_write_file(ctx: Message,
                            message: StrNode,
                            append: BoolNode = BoolNode(False),
                            file: Optional[FileNode] = None,
                            filename: Optional[StrNode] = None,
                            description: Optional[StrNode] = None,
                            spoiler: BoolNode = BoolNode(False)) -> FileNode:

    """
    Ecrit dans un fichier
    :param ctx:
    :param file:
    :param message:
    :param append:
    :param filename:
    :return:
    """
    _validate_required_string(message, 'message', 'wf')
    _validate_required_bool(append, 'append', 'wf')
    _validate_optional_string(filename, 'filename', 'wf')

    target_file = file if isinstance(file, FileNode) else FileNode(filename if filename is not None else "unnamed_file.txt")

    target_file.description = description if description is not None else target_file.description
    target_file.spoiler = spoiler if spoiler is not None else target_file.spoiler

    target_file.write(bytearray(message, "utf-8"), append)

    return target_file