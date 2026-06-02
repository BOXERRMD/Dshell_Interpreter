from Dshell.full_import import (Message,
                           PartialMessage,
                                File)

from ..DshellParser.ast_nodes import ListNode, StrNode, BoolNode, IntNode, EmbedNode, FileNode

from .utils.utils_message import utils_get_message, utils_autorised_mentions
from .utils.utils_file import utils_check_files_arguments
from .utils.utils_embed import utils_check_embeds_arguments
from .utils.utils_type_validation import (_validate_optional_number,
                                          _validate_optional_embed,
                                          _validate_optional_view,
                                          _validate_optional_string,
                                          _validate_optional_int,
                                          _validate_optional_bool,
                                          _validate_required_bool,
                                          _validate_required_int,
                                          _validate_not_none,
                                          _validate_optional_eval_group_node,
                                          _validate_required_string)
from ..DshellInterpreteur.cached_messages import dshell_cached_messages

from Dshell.full_import import Optional, Union, compile, DOTALL
from asyncio import wait_for, sleep


__all__ = [
    'dshell_send_message',
    'dshell_respond_message',
    'dshell_delete_message',
    'dshell_purge_message',
    'dshell_edit_message',
    'dshell_get_history_messages',
    'dshell_add_reactions',
    'dshell_remove_reactions',
    'dshell_clear_message_reactions',
    'dshell_clear_one_reactions',
    'dshell_pin_message',
    'dshell_unpin_message',
    'dshell_get_content_message',
    'dshell_get_author_id_message',
    'dshell_get_message_link',
    'dshell_get_message_category_id',
    'dshell_get_message_attachments',
    'dshell_get_channel_pined_messages',
    'dshell_is_message_system',
    'dshell_scan_message'
]


async def dshell_send_message(ctx: Message,
                              message: Optional[StrNode]=None,
                              delete=None,
                              channel=None,
                              global_mentions: Optional[BoolNode] = None,
                              everyone_mention: BoolNode = BoolNode(1),
                              roles_mentions: BoolNode = BoolNode(1),
                              users_mentions: BoolNode = BoolNode(1),
                              reply_mention: BoolNode = BoolNode(0),
                              embeds=None,
                              files: Optional[ListNode] = None,
                              view=None) -> IntNode:
    """
    Sends a message on Discord
    """
    _CMD = "sm"

    _validate_optional_number(delete, "Delete", _CMD)
    _validate_optional_bool(global_mentions, "Global mentions", _CMD)
    _validate_required_bool(everyone_mention, "Everyone mention", _CMD)
    _validate_required_bool(roles_mentions, "Roles mentions", _CMD)
    _validate_required_bool(users_mentions, "Users mentions", _CMD)
    _validate_required_bool(reply_mention, "Reply mention", _CMD)

    channel_to_send = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)
    allowed_mentions = utils_autorised_mentions(global_mentions, everyone_mention, roles_mentions, users_mentions, reply_mention)

    if channel_to_send is None:
        raise Exception(f'Channel {channel} not found!')

    final_files: Optional[list[File]] = utils_check_files_arguments(_CMD, files)

    _validate_optional_embed(embeds, "Embeds", _CMD)

    embeds = utils_check_embeds_arguments(_CMD, embeds)

    _validate_optional_view(view, "View", _CMD)

    sended_message = await channel_to_send.send(message,
                                                delete_after=delete,
                                                embeds=embeds,
                                                allowed_mentions=allowed_mentions,
                                                view=view,
                                                files=final_files)

    cached_messages = dshell_cached_messages.get()
    cached_messages[sended_message.id] = sended_message
    dshell_cached_messages.set(cached_messages)

    return IntNode(sended_message.id)


async def dshell_respond_message(ctx: Message,
                                 message: Optional[StrNode]=None,
                                 content: Optional[StrNode] = None,
                                 global_mentions: Optional[BoolNode] = None,
                                 everyone_mention: BoolNode = BoolNode(1),
                                 roles_mentions: BoolNode = BoolNode(1),
                                 users_mentions: BoolNode = BoolNode(1),
                                 reply_mention: BoolNode = BoolNode(0),
                                 delete=None,
                                 files: Optional[ListNode] = None,
                                 embeds=None) -> IntNode:
    """
    Responds to a message on Discord
    """
    _CMD = "srm"
    
    _validate_optional_string(content, "Content", _CMD)
    _validate_optional_number(delete, "Delete", _CMD)
    _validate_optional_bool(global_mentions, "Global mentions", _CMD)
    _validate_required_bool(everyone_mention, "Everyone mention", _CMD)
    _validate_required_bool(roles_mentions, "Roles mentions", _CMD)
    _validate_required_bool(users_mentions, "Users mentions", _CMD)
    _validate_required_bool(reply_mention, "Reply mention", _CMD)

    respond_message = ctx if message is None else utils_get_message(ctx, message)  # builds a reference to the message (even if it doesn't exist)
    autorised_mentions = utils_autorised_mentions(global_mentions, everyone_mention, roles_mentions, users_mentions, reply_mention)
    mention_author = True if reply_mention else False

    final_files: Optional[list[File]] = utils_check_files_arguments(_CMD, files)

    _validate_optional_embed(embeds, "Embeds", _CMD)

    embeds = utils_check_embeds_arguments(_CMD, embeds)

    sended_message = await respond_message.reply(
                                     content=StrNode(content),
                                     mention_author=mention_author,
                                     allowed_mentions=autorised_mentions,
                                     delete_after=delete,
                                     embeds=embeds,
                                     files=final_files)

    cached_messages = dshell_cached_messages.get()
    cached_messages[sended_message.id] = sended_message
    dshell_cached_messages.set(cached_messages)

    return IntNode(sended_message.id)

async def dshell_delete_message(ctx: Message,
                                message: Optional[StrNode]=None,
                                reason: Optional[StrNode]=None,
                                delay: IntNode= IntNode('0')) -> BoolNode:
    """
    Deletes a message
    """
    _CMD = "dm"

    delete_message = ctx if message is None else utils_get_message(ctx, message)

    _validate_optional_int(delay, "delay", _CMD)
    _validate_optional_string(reason, "reason", _CMD)
    _validate_optional_string(reason, "message", _CMD)

    if delay > 3600:
        raise Exception(f'The message deletion delay is too long! ({delay} seconds)')

    await delete_message.delete(delay=delay, reason=reason)

    return BoolNode(True)


async def dshell_purge_message(ctx: Message,
                               message_number: IntNode,
                               channel: Optional[IntNode]=None,
                               reason: Optional[StrNode]=None,
                               check: Optional[StrNode] = None) -> IntNode:
    """
    Purges messages from a channel
    """
    _CMD = "pm"

    _validate_required_int(message_number, "Message number", _CMD)
    _validate_optional_eval_group_node(check, "check", _CMD)
    _validate_optional_string(reason, "reason", _CMD)
    _validate_optional_string(check, "check", _CMD)

    purge_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if purge_channel is None:
        raise Exception(f"Channel {channel} to purge not found!")

    await purge_channel.purge(limit=message_number, reason=reason)

    return IntNode(purge_channel.id)


async def dshell_edit_message(ctx: Message,
                              message,
                              new_content: Optional[StrNode]=None,
                              embeds: Optional[EmbedNode]=None,
                              view=None,
                              files: Optional[FileNode]=None) -> IntNode:
    """
    Edits a message
    """
    _CMD = "em"

    edit_message = utils_get_message(ctx, message)

    _validate_optional_embed(embeds, "embeds", _CMD)
    _validate_optional_view(view, "view", _CMD)
    _validate_optional_string(new_content, "new_content", _CMD)

    final_files: Optional[list[File]] = utils_check_files_arguments(_CMD, files)

    embeds = utils_check_embeds_arguments(_CMD, embeds)

    await edit_message.edit(content=new_content, embeds=embeds, view=view, files=final_files)

    return IntNode(edit_message.id)

async def dshell_add_reactions(ctx: Message, reactions: Union[StrNode, ListNode], message: Optional[Union[StrNode, IntNode]]=None) -> IntNode:
    """
    Adds reactions to a message
    """
    _CMD = "ar"
    message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(reactions, StrNode):
        reactions = (reactions,)

    for reaction in reactions:
        _validate_required_string(reaction, "reactions", _CMD)
        await message.add_reaction(reaction)

    return IntNode(message.id)


async def dshell_remove_reactions(ctx: Message, reactions: Union[ListNode, StrNode], message: Optional[Union[IntNode, StrNode]]=None) -> IntNode:
    """
    Removes reactions from a message
    """
    _CMD = "rr"
    message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(reactions, StrNode):
        reactions = [reactions]

    for reaction in reactions:
        _validate_required_string(reaction, "reactions", _CMD)
        await message.clear_reaction(reaction)

    return IntNode(message.id)

async def dshell_clear_message_reactions(ctx: Message, message: Optional[Union[IntNode, StrNode]]=None) -> IntNode:
    """
    Clear all reaction on the target message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if message is None:
        raise Exception(f'Message not found !')

    await message.clear_reactions()

    return IntNode(message.id)

async def dshell_clear_one_reactions(ctx: Message, message: Union[IntNode, StrNode], emoji: StrNode) -> IntNode:
    """
    Clear one emoji on the target message
    """

    if not isinstance(emoji, StrNode):
        raise Exception(f'Emoji must be StrNode, not {type(emoji)}')

    target_message = ctx if message is None else utils_get_message(ctx, message)

    await target_message.clear_reaction(emoji)

    return IntNode(target_message.id)

async def dshell_pin_message(ctx: Message, message: Union[IntNode, StrNode]=None) -> IntNode:
    """
    Pin a message
    """

    target_message = ctx if message is None else utils_get_message(ctx, message)

    await target_message.pin()

    return IntNode(target_message.id)

async def dshell_unpin_message(ctx: Message, message: Optional[Union[IntNode, StrNode]]=None, reason: Optional[StrNode]=None) -> IntNode:
    """
    Unpin a message
    """

    _CMD = "upinm"

    target_message = ctx if message is None else utils_get_message(ctx, message)

    _validate_optional_string(reason, "Reason", _CMD)

    await target_message.unpin()

    return IntNode(target_message.id)


################################# GET MESSAGE INFO #################################

async def dshell_get_history_messages(ctx: Message,
                                      channel: Optional[IntNode]=None,
                                      limit: Optional[IntNode]=None) -> "ListNode":
    """
    Searches for messages matching a regex in a channel
    """

    _validate_optional_int(limit, "Limit", "mh")

    search_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if search_channel is None:
        raise Exception(f"Channel {channel} to search not found!")



    cached_messages = dshell_cached_messages.get()
    messages = ListNode([])
    async for message in search_channel.history(limit=limit):
        message_id = message.id
        messages.add(IntNode(message_id))
        cached_messages[message_id] = message

    dshell_cached_messages.set(cached_messages)
    return messages

async def dshell_get_content_message(ctx: Message, message: Optional[Union[IntNode, StrNode]]=None):
    """
    Get the content of a message
    """

    target_message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(target_message, PartialMessage):
        try:
            fetch_target_message = await target_message.fetch()
        except:
            raise Exception(f'Message not found !')
    else:
        fetch_target_message = target_message

    return StrNode(fetch_target_message.content)


async def dshell_get_author_id_message(ctx: Message, message: Optional[Union[IntNode, StrNode]] = None):
    """
    Return author ID of the message given (or ctx if message=None)
    :param ctx:
    :param message: message ID
    :return:
    """
    _CMD = "gma"

    target_message = ctx
    if message is not None:
        target_message = utils_get_message(ctx, message)

        if isinstance(target_message, PartialMessage):
            try:
                target_message = await target_message.fetch()
            except:
                raise Exception(f"[message_author] Author ID message to get is not found !")

    return IntNode(target_message.author.id)

async def dshell_get_message_link(ctx: Message, message: Union[IntNode, StrNode]):
    """
    Return the link of a message given its ID
    :param ctx:
    :param message: message ID
    :return:
    """

    target_message = utils_get_message(ctx, message)

    return StrNode(target_message.jump_url)

async def dshell_get_message_category_id(ctx: Message, message: Optional[Union[IntNode, StrNode]] = None):
    """
    Return the category ID of a message given its ID
    :param ctx:
    :param message: message ID
    :return:
    """
    _CMD = "gmc"

    target_message = ctx
    if message is not None:
        target_message = utils_get_message(ctx, message)

        if isinstance(target_message, PartialMessage):
            try:
                target_message = await target_message.fetch()
            except:
                raise Exception(f"[category_message] Message ID to get is not found !")

    return IntNode(target_message.channel.category.id) if target_message.channel.category is not None else IntNode(0)

async def dshell_get_message_attachments(ctx: Message, message: Optional[Union[InterruptedError, StrNode]] = None):
    """
    Return the attachments of a message given its ID
    :param ctx:
    :param message: message ID
    :return:
    """
    _CMD = "gmat"

    _validate_optional_int(message, "Message parameter", _CMD)

    target_message = ctx
    if message is not None:
        target_message = utils_get_message(ctx, message)

        if isinstance(target_message, PartialMessage):
            try:
                target_message = await target_message.fetch()
            except:
                raise Exception(f"[attachments_message] Message ID to get is not found !")

    attachments = ListNode([])

    for attachment in target_message.attachments:
        attachments.add(StrNode(attachment.url))

    return attachments

async def dshell_get_channel_pined_messages(ctx: Message, channel: Optional[IntNode]=None):
    """
    Returns a list of pined messages IDs in a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gmp] Channel {channel} not found !")

    pinned_messages = await channel_to_check.pins()


    messages_list = ListNode([])

    cached_messages = dshell_cached_messages.get()
    for message in pinned_messages:
        messages_list.add(IntNode(message.id))
        cached_messages[message.id] = message

    return messages_list

async def dshell_is_message_system(ctx: Message, message: Optional[Union[IntNode, StrNode]] = None):
    """
    Return if the message is a system message
    :param ctx:
    :param message: message ID
    :return:
    """
    _CMD = "ims"

    _validate_optional_int(message, "Message parameter", _CMD)

    target_message = ctx
    if message is not None:
        target_message = utils_get_message(ctx, message)

        if isinstance(target_message, PartialMessage):
            try:
                target_message = await target_message.fetch()
            except:
                raise Exception(f"[is_system_message] Message ID to get is not found !")

    return BoolNode(target_message.is_system())


async def dshell_scan_message(ctx: Message,
                              channel: Optional[IntNode] = None,
                              regex: Optional[StrNode] = None,
                              member: Optional[IntNode] = None,
                              timeout: IntNode = IntNode(60)) -> Union[IntNode, None]:
    """
    Attend un message dans un salon spécifique qui correspond à une expression régulière (si spécifié), et retourne son ID.
    :param ctx:
    :param regex: Expression régulière à matcher dans le contenu du message (optionnel)
    :param timeout: Durée maximale d'attente en secondes (par défaut : 60 secondes)
    :return: ID du message qui correspond aux critères, ou None si le temps est écoulé ou si aucun message ne correspond
    """

    _CMD = "scan_message"

    _validate_optional_int(channel, "channel", _CMD)

    _validate_optional_string(regex, "regex", _CMD)

    _validate_optional_int(member, "member", _CMD)

    _validate_required_int(timeout, "timeout", _CMD)

    target_channel = ctx.channel if channel is None else ctx.guild.get_channel(channel)

    if target_channel is None:
        raise Exception(f"Channel with ID {channel} not found in guild {ctx.guild.name}.")

    if regex is not None:
        try:
            regex = compile(regex, flags=DOTALL)
        except Exception as e:
            raise Exception(f"Invalid regex pattern: {e}")

    try:

        last_message = None
        param_required = bool(regex) + bool(member)
        param_actual = -1 # on initialise à -1 pour compenser le fait que le message trouvé ne correspond pas encore aux critères, et ainsi entrer dans la boucle
        while param_actual < param_required: # tant que le message trouvé ne correspond pas aux critères, on continue d'attendre les nouveaux messages
            param_actual = -1 # on réinitialise à -1 à chaque nouveau message pour compenser le fait que le message trouvé ne correspond pas encore aux critères, et ainsi entrer dans la boucle si nécessaire

            last_message = await wait_for(dshell_scan_check(target_channel), timeout=timeout)

            if regex is not None and regex.search(last_message.content):
                param_actual += 1

            if member is not None and last_message.author.id == member:
                param_actual += 1

            param_actual += 1 # on ajoute 1 pour compenser l'initialisation à -1. Ainsi, si aucun critère n'est spécifié, le premier message trouvé fera que param_actual = 0, ce qui est égal à param_required, et donc fera sortir de la boucle.


        cached_messages = dshell_cached_messages.get()
        cached_messages[last_message.id] = last_message
        dshell_cached_messages.set(cached_messages)

        return IntNode(last_message.id)

    except TimeoutError:
        return None

async def dshell_scan_check(target_channel) -> Message:
    last_message_id = target_channel.last_message_id
    while target_channel.last_message_id == last_message_id or target_channel.last_message.is_system():
        await sleep(1)

    return target_channel.last_message


