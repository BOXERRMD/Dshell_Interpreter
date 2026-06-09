
from ..full_import import Message, Union, PartialMessage, Optional
from ..DshellParser.ast_nodes import ListNode, FileNode, StrNode, BoolNode, IntNode, FileStreamNode

from .utils.utils_message import utils_get_message
from .utils.utils_type_validation import (_validate_required_file_node,
                                          _validate_required_string,
                                          _validate_optional_string,
                                          _validate_required_bool)

__all__ = [
    "dshell_get_message_files",
    "dshell_write_file",
    "dshell_read_file",
    "dshell_stream_file"
]

async def dshell_get_message_files(ctx: Message, message: Union[StrNode, IntNode]) -> ListNode:
    """
    Récupère les fichiers d'un message
    :param ctx:
    :param message:
    :return:
    """

    target_message = ctx if message is None else await utils_get_message(ctx, message)

    attachments_list: ListNode = ListNode([], bypass_limit_elt=True)

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

    return StrNode(file.read())

async def dshell_stream_file(ctx: Message, file: FileNode, separator: Optional[StrNode] = None) -> FileStreamNode:
    """
    Stream le contenue d'un fichier. Si un séparateur est passé en paramètre,
    le stream s'arrêtera à chaque fois que le séparateur est rencontré, sinon il streamera ligne par ligne
    (MAX_STR_SIZE de la str max renvoyé)
    :param ctx:
    :param file:
    :param separator:
    :return:
    """

    _validate_optional_string(separator, 'separator', 'sf')

    if separator is not None and len(separator) > 1:
        raise Exception(f"Separator in stream file must be a single character, not '{separator}' !")

    return file.stream(separator)


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