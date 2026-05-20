
from ...full_import import Embed, Optional, Union
from ...DshellParser.ast_nodes import ListNode

__all__ = [
    "utils_check_embeds_arguments"
]

def utils_check_embeds_arguments(_CMD: str, embeds: Optional[Union[Embed, ListNode]]) -> Union[list[Optional[Embed]], ListNode]:
    """
    Check if the embeds argument is valid. Return a list of optional embeds arguments
    :param _CMD:
    :param embeds:
    :return:
    """

    final_embeds: Union[list[Optional[Embed]], ListNode] = []

    if embeds is not None:
        if isinstance(embeds, Embed):
            final_embeds.append(embeds)
        elif isinstance(embeds, ListNode):
            if (embed_list_size := len(embeds)) > 10:
                raise Exception(f"Embeds argument has more than 10 items, not {embed_list_size} in '{_CMD}' command")

            final_embeds = embeds
        else:
            raise Exception(f"Embeds must be a embed object or a ListNode, not {type(embeds)} in '{_CMD}' command")

    return final_embeds