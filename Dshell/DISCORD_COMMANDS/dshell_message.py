from Dshell.full_import import (Message,
                           Embed,
                           PartialMessage,
                                File)

from ..DshellParser.ast_nodes import ListNode, FileNode

from .utils.utils_message import utils_get_message, utils_autorised_mentions
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
                                          _validate_optional_list_node,
                                          _validate_required_file_node)
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
                              message=None,
                              delete=None,
                              channel=None,
                              global_mentions: bool = None,
                              everyone_mention: bool = True,
                              roles_mentions: bool = True,
                              users_mentions: bool = True,
                              reply_mention: bool = False,
                              embeds=None,
                              files: Optional[ListNode] = None,
                              view=None) -> int:
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
    _validate_optional_list_node(files, "files", _CMD)

    channel_to_send = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)
    allowed_mentions = utils_autorised_mentions(global_mentions, everyone_mention, roles_mentions, users_mentions, reply_mention)

    if channel_to_send is None:
        raise Exception(f'Channel {channel} not found!')

    if files is not None:
        for file in files:
            _validate_required_file_node(file, "file", _CMD)

    final_files: list[File] = []
    for file in files:
        final_files.append(File(fp=file.content, filename=file.name, description=file.description, spoiler=file.spoiler))

    _validate_optional_embed(embeds, "Embeds", _CMD)

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

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

    return sended_message.id


async def dshell_respond_message(ctx: Message,
                                 message=None,
                                 content: str = None,
                                 global_mentions: bool = None,
                                 everyone_mention: bool = True,
                                 roles_mentions: bool = True,
                                 users_mentions: bool = True,
                                 reply_mention: bool = False,
                                 delete=None,
                                 files: Optional[ListNode] = None,
                                 embeds=None):
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
    _validate_optional_list_node(files, "files", _CMD)

    respond_message = ctx if message is None else utils_get_message(ctx, message)  # builds a reference to the message (even if it doesn't exist)
    autorised_mentions = utils_autorised_mentions(global_mentions, everyone_mention, roles_mentions, users_mentions, reply_mention)
    mention_author = True if reply_mention else False

    if files is not None:
        for file in files:
            _validate_required_file_node(file, "file", _CMD)

    final_files: list[File] = []
    for file in files:
        final_files.append(
            File(fp=file.content, filename=file.filename, description=file.description, spoiler=file.spoiler))

    _validate_optional_embed(embeds, "Embeds", _CMD)

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    sended_message = await respond_message.reply(
                                     content=str(content),
                                     mention_author=mention_author,
                                     allowed_mentions=autorised_mentions,
                                     delete_after=delete,
                                     embeds=embeds,
                                     files=final_files)

    cached_messages = dshell_cached_messages.get()
    cached_messages[sended_message.id] = sended_message
    dshell_cached_messages.set(cached_messages)

    return sended_message.id

async def dshell_delete_message(ctx: Message, message=None, reason=None, delay=0):
    """
    Deletes a message
    """

    delete_message = ctx if message is None else utils_get_message(ctx, message)

    _validate_optional_int(delay, "Delay", "dm")

    if delay > 3600:
        raise Exception(f'The message deletion delay is too long! ({delay} seconds)')

    await delete_message.delete(delay=delay, reason=reason)


async def dshell_purge_message(ctx: Message, message_number: int, channel: Optional[int]=None, reason: Optional[str]=None, check: Optional[str] = None):
    """
    Purges messages from a channel
    """
    _CMD = "pm"

    _validate_required_int(message_number, "Message number", _CMD)
    _validate_optional_eval_group_node(check, "check", _CMD)

    purge_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if purge_channel is None:
        raise Exception(f"Channel {channel} to purge not found!")

    await purge_channel.purge(limit=message_number, reason=reason)


async def dshell_edit_message(ctx: Message, message, new_content=None, embeds=None, view=None, files=None) -> int:
    """
    Edits a message
    """
    _CMD = "em"

    edit_message = utils_get_message(ctx, message)

    _validate_optional_embed(embeds, "Embeds", _CMD)
    _validate_optional_view(view, "View", _CMD)
    _validate_optional_list_node(files, "files", _CMD)

    if files is not None:
        for file in files:
            _validate_required_file_node(file, "file", _CMD)

    final_files: list[File] = []
    for file in files:
        final_files.append(
            File(fp=file.content, filename=file.filename, description=file.description, spoiler=file.spoiler))

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    await edit_message.edit(content=new_content, embeds=embeds, view=view, files=final_files)

    return edit_message.id

async def dshell_add_reactions(ctx: Message, reactions, message=None):
    """
    Adds reactions to a message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(reactions, str):
        reactions = (reactions,)

    for reaction in reactions:
        await message.add_reaction(reaction)

    return message.id


async def dshell_remove_reactions(ctx: Message, reactions, message=None):
    """
    Removes reactions from a message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(reactions, str):
        reactions = [reactions]

    for reaction in reactions:
        await message.clear_reaction(reaction)

    return message.id

async def dshell_clear_message_reactions(ctx: Message, message):
    """
    Clear all reaction on the target message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if message is None:
        raise Exception(f'Message not found !')

    await message.clear_reactions()

    return message.id

async def dshell_clear_one_reactions(ctx: Message, message, emoji):
    """
    Clear one emoji on the target message
    """

    if not isinstance(emoji, str):
        raise Exception(f'Emoji must be string, not {type(emoji)}')

    target_message = ctx if message is None else utils_get_message(ctx, message)

    await target_message.clear_reaction(emoji)

    return target_message.id

async def dshell_pin_message(ctx: Message, message=None):
    """
    Pin a message
    """

    target_message = ctx if message is None else utils_get_message(ctx, message)

    await target_message.pin()

    return target_message.id

async def dshell_unpin_message(ctx: Message, message=None, reason=None):
    """
    Unpin a message
    """

    _CMD = "upinm"

    target_message = ctx if message is None else utils_get_message(ctx, message)

    _validate_optional_string(reason, "Reason", _CMD)

    await target_message.unpin()

    return target_message.id


################################# GET MESSAGE INFO #################################

async def dshell_get_history_messages(ctx: Message,
                                      channel=None,
                                      limit=None) -> "ListNode":
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
        messages.add(message_id)
        cached_messages[message_id] = message

    dshell_cached_messages.set(cached_messages)
    return messages

async def dshell_get_content_message(ctx: Message, message=None):
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

    return fetch_target_message.content


async def dshell_get_author_id_message(ctx: Message, message: Optional[int] = None):
    """
    Return author ID of the message given (or ctx if message=None)
    :param ctx:
    :param message: message ID
    :return:
    """
    _CMD = "gma"

    _validate_optional_int(message, "Message parameter", _CMD)

    target_message = ctx
    if message is not None:
        target_message = utils_get_message(ctx, message)

        if isinstance(target_message, PartialMessage):
            try:
                target_message = await target_message.fetch()
            except:
                raise Exception(f"[message_author] Author ID message to get is not found !")

    return target_message.author.id

async def dshell_get_message_link(ctx: Message, message: int):
    """
    Return the link of a message given its ID
    :param ctx:
    :param message: message ID
    :return:
    """
    if not isinstance(message, int):
        raise Exception(f'Message parameter must be an integer, not {type(message)} !')

    target_message = utils_get_message(ctx, message)

    return target_message.jump_url

async def dshell_get_message_category_id(ctx: Message, message: int = None):
    """
    Return the category ID of a message given its ID
    :param ctx:
    :param message: message ID
    :return:
    """
    _CMD = "gmc"

    _validate_optional_int(message, "Message parameter", _CMD)

    target_message = ctx
    if message is not None:
        target_message = utils_get_message(ctx, message)

        if isinstance(target_message, PartialMessage):
            try:
                target_message = await target_message.fetch()
            except:
                raise Exception(f"[category_message] Message ID to get is not found !")

    return target_message.channel.category.id if target_message.channel.category is not None else 0

async def dshell_get_message_attachments(ctx: Message, message: int = None):
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
        attachments.add(attachment.url)

    return attachments

async def dshell_get_channel_pined_messages(ctx: Message, channel=None):
    """
    Returns a list of pined messages IDs in a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gmp] Channel {channel} not found !")

    pinned_messages = await channel_to_check.pins()


    messages_list = ListNode([])

    cached_messages = dshell_cached_messages.get()
    for message in pinned_messages:
        messages_list.add(message.id)
        cached_messages[message.id] = message

    return messages_list

async def dshell_is_message_system(ctx: Message, message: int = None):
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

    return target_message.is_system()


async def dshell_scan_message(ctx: Message,
                              channel: Optional[int] = None,
                              regex: Optional[str] = None,
                              member: Optional[int] = None,
                              timeout: int = 60) -> Union[int, None]:
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

        return last_message.id

    except TimeoutError:
        return None

async def dshell_scan_check(target_channel) -> Message:
    last_message_id = target_channel.last_message_id
    while target_channel.last_message_id == last_message_id or target_channel.last_message.is_system():
        await sleep(1)

    return target_channel.last_message


