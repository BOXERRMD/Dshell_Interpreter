__all__ = [
    'dshell_respond_interaction',
    'dshell_defer_interaction',
    'dshell_delete_original_message'
]


from Dshell.full_import import (Interaction,
                           Embed,
                           EasyModifiedViews)

from .utils.utils_message import utils_autorised_mentions
from .utils.utils_type_validation import (_validate_optional_number,
                                          _validate_optional_embed,
                                          _validate_optional_view)

async def dshell_respond_interaction(ctx: Interaction,
                                     content: str = None,
                                     delete=None,
                                     global_mentions: bool = None,
                                     everyone_mention: bool = True,
                                     roles_mentions: bool = True,
                                     users_mentions: bool = True,
                                     reply_mention: bool = False,
                                     hide: bool = False,
                                     embeds=None,
                                     view=None) -> int:
    """
    Responds to a message interaction on Discord
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    _validate_optional_number(delete, "Delete")

    if not isinstance(hide, bool):
        raise Exception(f'Hide parameter must be a boolean, not {type(hide)} !')

    allowed_mentions = utils_autorised_mentions(global_mentions,
                                                everyone_mention,
                                                roles_mentions,
                                                users_mentions,
                                                reply_mention)

    from Dshell._DshellParser.ast_nodes import ListNode

    _validate_optional_embed(embeds, "Embeds")

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    _validate_optional_view(view, "View")

    sended_message = await ctx.response.send_message(
                                     content=str(content),
                                     ephemeral=hide,
                                     allowed_mentions=allowed_mentions,
                                     delete_after=delete,
                                     embeds=embeds,
                                     view=view)

    return sended_message.id

async def dshell_defer_interaction(ctx: Interaction) -> bool:
    """
    Defer a message interaction on Discord
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    await ctx.response.defer()

    return True

async def dshell_delete_original_message(ctx: Interaction) -> int:
    """
    Delete the original message of an interaction on Discord
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    await ctx.delete_original_message()

    return ctx.message.id
