from ...DshellParser.ast_nodes import FileNode, ListNode
from ...full_import import File, Optional, Union
from .utils_type_validation import _validate_required_file_node

from io import BytesIO

__all__ = [
    "utils_check_files_arguments"
]

def utils_check_files_arguments(_CMD: str, files: Optional[Union[FileNode, ListNode]]) -> Optional[list[File]]:
    """
    Check if the files argument is valid, and convert it to a list of File if it's a FileNode or a ListNode
    If the final_files list is empty, return None
    :param files:
    :return:
    """

    final_files: list[File] = []

    if files is not None:
        if isinstance(files, FileNode):
            buffer: BytesIO = BytesIO(files.content)
            buffer.seek(0)
            final_files.append(File(fp=buffer, filename=files.name, description=files.description,
                                    spoiler=files.spoiler))
        elif isinstance(files, ListNode):

            if (file_list_size := len(files)) > 10:
                raise Exception(f"Files argument has more than 10 items, not {file_list_size} in '{_CMD}' command")

            for file in files:
                _validate_required_file_node(file, "file", _CMD)
                buffer: BytesIO = BytesIO(file.content)
                buffer.seek(0)
                final_files.append(File(fp=buffer, filename=file.name, description=file.description,
                                        spoiler=file.spoiler))

        else:
            raise Exception(f"Files must be a FileNode or a ListNode, not {type(files)} in '{_CMD}' command")

    return final_files if len(final_files) > 0 else None