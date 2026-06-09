from Dshell.full_import import (Message,
                           MISSING,
                           _MissingSentinel,
                           CategoryChannel,
                           VoiceChannel,
                           PartialMessage)

from ..DshellParser.ast_nodes import ListNode, StrNode, IntNode, PermissionNode, BoolNode, FloatNode

from Dshell.full_import import search

from Dshell.full_import import sleep

from Dshell.full_import import Union, Optional

from .utils.utils_message import utils_get_message
from .utils.utils_thread import utils_get_thread
from .utils.utils_type_validation import (_validate_optional_string,
                                          _validate_optional_int,
                                          _validate_missing_or_type,
                                          _validate_not_none,
                                          _validate_has_attribute,
                                          _validate_required_string)

__all__ = [
    'dshell_get_channel',
    'dshell_get_channels',
    'dshell_get_thread',
    'dshell_get_channels_in_category',
    'dshell_create_text_channel',
    'dshell_create_thread_message',
    'dshell_delete_channel',
    'dshell_delete_channels',
    'dshell_delete_thread',
    'dshell_create_voice_channel',
    'dshell_edit_text_channel',
    'dshell_edit_voice_channel',
    'dshell_edit_thread',
    'dshell_create_category',
    'dshell_edit_category',
    'dshell_delete_category',
    'dshell_get_channel_category_id',
    'dshell_get_channel_nsfw',
    'dshell_get_channel_slowmode',
    'dshell_get_channel_topic',
    'dshell_get_channel_threads',
    'dshell_get_channel_position',
    'dshell_get_channel_url',
    'dshell_get_channel_voice_members',
    'dshell_clone_channel'
]


async def dshell_get_channel(ctx: Message, name: StrNode):
    """
    Returns the channel object of the channel where the command was executed or the specified channel.
    """
    # name peut être str ou int, validation manuelle dans le corps
    if isinstance(name, StrNode):
        return next((IntNode(c.id) for c in ctx.channel.guild.channels if c.name == name), None)

    raise Exception(f"Channel must be an integer or a string, not {type(name)} !")


async def dshell_get_channels(ctx: Message, name: Optional[StrNode]=None, regex: Optional[StrNode]=None) -> ListNode:
    """
    Returns a list of channels with the same name and/or matching the same regex.
    If neither is set, it will return all channels in the server.
    """
    _CMD = "gcs"

    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_string(regex, "Regex", _CMD)

    channels = ListNode([])

    for channel in ctx.channel.guild.channels:
        if name is not None and channel.name == StrNode(name):
            channels.add(IntNode(channel.id))

        elif regex is not None and search(regex, channel.name):
            channels.add(IntNode(channel.id))

    return channels

async def dshell_get_channels_in_category(ctx: Message,
                                          category: Optional[IntNode] = None,
                                          name: Optional[StrNode]=None,
                                          regex: Optional[StrNode]=None):
    """
    Returns a list of channels in a specific category with the same name and/or matching the same regex.
    If neither is set, it will return all channels in the specified category.
    """

    _CMD = "gccs"

    _validate_optional_int(category, "Category", _CMD)

    if category is None and ctx.channel.category is not None:
        category = ctx.channel.category.id

    _validate_not_none(category, "[{_CMD}] The current channel has no category, you must specify a category ID !")

    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_string(regex, "Regex", _CMD)

    channels = ListNode([])

    category_channel = ctx.channel.guild.get_channel(category)
    if category_channel is None or not hasattr(category_channel, 'channels'):
        raise Exception(f"Category {category} not found or does not contain channels !")

    for channel in category_channel.channels:
        if name is not None and channel.name == str(name):
            channels.add(IntNode(channel.id))

        elif regex is not None and search(regex, channel.name):
            channels.add(IntNode(channel.id))

    return channels

async def dshell_create_text_channel(ctx: Message,
                                     name: StrNode,
                                     category: Optional[IntNode] = None,
                                     position: IntNode = MISSING,
                                     slowmode: IntNode = MISSING,
                                     topic: StrNode = MISSING,
                                     nsfw: BoolNode = MISSING,
                                     permissions: PermissionNode = MISSING,
                                     reason: Optional[StrNode] = None):
    """
    Creates a text channel on the server
    """

    _CMD = "cc"

    _validate_required_string(name, "Name", _CMD)

    _validate_optional_int(category, "Category", _CMD)

    _validate_missing_or_type(position, "Position", IntNode, _CMD)

    _validate_missing_or_type(slowmode, "Slowmode", IntNode, _CMD)

    _validate_missing_or_type(topic, "Topic", StrNode, _CMD)

    _validate_missing_or_type(nsfw, "NSFW", BoolNode, _CMD)

    _validate_missing_or_type(permissions, "Permissions", PermissionNode, _CMD)
    
    _validate_optional_string(reason, "Reason", _CMD)

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_text_channel(str(name),
                                                          category=channel_category,
                                                          position=position,
                                                          slowmode_delay=slowmode,
                                                          topic=topic,
                                                          nsfw=nsfw,
                                                          overwrites=permissions.value,
                                                          reason=reason)

    return IntNode(created_channel.id)


async def dshell_create_voice_channel(ctx: Message,
                                      name: StrNode,
                                      category: Optional[IntNode] = None,
                                      position: IntNode = MISSING,
                                      bitrate: IntNode = MISSING,
                                      permissions: PermissionNode = MISSING,
                                      reason: Optional[StrNode] = None):
    """
    Creates a voice channel on the server
    """
    _CMD = "cvc"

    _validate_required_string(name, "Name", _CMD)

    _validate_optional_int(category, "Category", _CMD)

    _validate_missing_or_type(position, "Position", IntNode, _CMD)

    _validate_missing_or_type(bitrate, "Bitrate", IntNode, _CMD)
    
    _validate_missing_or_type(permissions, "Permissions", PermissionNode, _CMD)
    
    _validate_optional_string(reason, "Reason", _CMD)

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_voice_channel(StrNode(name),
                                                           category=channel_category,
                                                           position=position,
                                                           bitrate=bitrate,
                                                           overwrites=permissions.value,
                                                           reason=reason)

    return IntNode(created_channel.id)


async def dshell_delete_channel(ctx: Message,
                                channel=None,
                                reason=None,
                                timeout: FloatNode = FloatNode(0)):
    """
    Deletes a channel.
    You can add a waiting time before it is deleted (in seconds)
    """
    _CMD = "dc"

    _validate_optional_int(channel, "Channel", _CMD)
    _validate_optional_int(timeout, "Timeout", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)

    channel_to_delete = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_delete, f"[{_CMD}] Channel {channel} not found !")

    await sleep(timeout)

    await channel_to_delete.delete(reason=reason)

    return IntNode(channel_to_delete.id)


async def dshell_delete_channels(ctx: Message,
                                 name: Optional[StrNode]=None,
                                 regex: Optional[StrNode]=None,
                                 reason: Optional[StrNode]=None) -> None:
    """
    Deletes all channels with the same name and/or matching the same regex.
    If neither is set, it will delete all channels with the same name as the one where the command was executed.
    """
    _CMD = "dcs"

    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_string(regex, "Regex", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)

    for channel in ctx.channel.guild.channels:

        if name is not None and channel.name == StrNode(name):
            await channel.delete(reason=reason)

        elif regex is not None and search(regex, channel.name):
            await channel.delete(reason=reason)

    return None


async def dshell_edit_text_channel(ctx: Message,
                                   channel: Optional[IntNode] = None,
                                   name: Optional[StrNode]=None,
                                   category: IntNode = MISSING,
                                   position: IntNode = MISSING,
                                   slowmode: IntNode = MISSING,
                                   topic: StrNode = MISSING,
                                   nsfw: BoolNode = MISSING,
                                   permissions: PermissionNode = MISSING,
                                   reason: Optional[StrNode] = None):
    """
    Edits a text channel on the server
    """
    _CMD = "ec"

    _validate_optional_string(name, "Name", _CMD)

    _validate_missing_or_type(position, "Position", IntNode, _CMD)

    _validate_missing_or_type(category, "Category", IntNode, _CMD)

    _validate_missing_or_type(slowmode, "Slowmode", IntNode, _CMD)

    _validate_missing_or_type(topic, "Topic", StrNode, _CMD)

    _validate_missing_or_type(nsfw, "NSFW", BoolNode, _CMD)

    _validate_missing_or_type(permissions, "Permissions", PermissionNode, _CMD)

    _validate_optional_string(reason, "Reason", _CMD)

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)
    new_categoy = ctx.channel.category if isinstance(category, _MissingSentinel) else ctx.channel.guild.get_channel(category)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               category=new_categoy,
                               slowmode_delay=slowmode if slowmode is not MISSING else channel_to_edit.slowmode_delay,
                               topic=topic if topic is not MISSING else channel_to_edit.topic,
                               nsfw=nsfw if nsfw is not MISSING else channel_to_edit.nsfw,
                               overwrites=permissions.value if permissions is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return IntNode(channel_to_edit.id)


async def dshell_edit_voice_channel(ctx: Message,
                                    channel=None,
                                    name: Optional[StrNode]=None,
                                    category: IntNode = MISSING,
                                    position: IntNode = MISSING,
                                    bitrate: IntNode = MISSING,
                                    permissions: PermissionNode = MISSING,
                                    reason=None):
    """
    Edits a voice channel on the server
    """
    _CMD = "evc"

    _validate_optional_int(channel, "Channel", _CMD)

    _validate_optional_string(name, "Name", _CMD)

    _validate_missing_or_type(position, "Position", IntNode, _CMD)

    _validate_missing_or_type(category, "Category", IntNode, _CMD)

    _validate_missing_or_type(bitrate, "Bitrate", IntNode, _CMD)

    _validate_missing_or_type(permissions, "Permissions", PermissionNode, _CMD)

    _validate_optional_string(reason, "Reason", _CMD)

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)
    new_categoy = ctx.channel.category if isinstance(category, _MissingSentinel) else ctx.channel.guild.get_channel(category)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               category=new_categoy,
                               bitrate=bitrate if bitrate is not MISSING else channel_to_edit.bitrate,
                               overwrites=permissions.value if permissions is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return IntNode(channel_to_edit.id)


async def dshell_create_thread_message(ctx: Message,
                                       name: StrNode,
                                       message: Optional[Union[IntNode, StrNode]] = None,
                                       archive: IntNode=MISSING,
                                       slowmode: IntNode=MISSING):
    """
    Creates a thread from a message.
    """

    _CMD = "ct"

    message = ctx if message is None else await utils_get_message(ctx, message)

    _validate_required_string(name, "Name", _CMD)

    _validate_missing_or_type(archive, "Auto archive duration", IntNode, _CMD)

    if isinstance(archive, IntNode) and archive not in (60, 1440, 4320, 10080):
        raise Exception("Auto archive duration must be one of the following values: 60, 1440, 4320, 10080 !")

    _validate_missing_or_type(slowmode, "Slowmode delay", IntNode, _CMD)

    _validate_missing_or_type(slowmode, "Slowmode delay", IntNode, _CMD)

    if isinstance(slowmode, IntNode) and slowmode < 0:
        raise Exception("Slowmode delay must be a positive integer !")

    thread = await message.create_thread(name=name,
                    auto_archive_duration=archive,
                    slowmode_delay=slowmode)

    return IntNode(thread.id)

async def dshell_edit_thread(ctx: Message,
                             thread: Union[IntNode, StrNode] = None,
                             name: Optional[StrNode]=None,
                             archive=MISSING,
                             slowmode: IntNode=MISSING,
                             reason: Optional[StrNode]=None) -> IntNode:
    """ Edits a thread.
    """
    _CMD = "et"

    if thread is None:
        thread = ctx.thread

    if thread is None:
        raise Exception("Thread must be specified !")

    thread = await utils_get_thread(ctx, thread)

    _validate_missing_or_type(name, "Name", StrNode, _CMD)

    _validate_missing_or_type(archive, "Auto archive duration", IntNode, _CMD)

    if isinstance(archive, IntNode) and archive not in (60, 1440, 4320, 10080):
        raise Exception("Auto archive duration must be one of the following values: 60, 1440, 4320, 10080 !")

    _validate_missing_or_type(slowmode, "Slowmode delay", IntNode, _CMD)

    _validate_missing_or_type(slowmode, "Slowmode delay", IntNode, _CMD)

    if isinstance(slowmode, IntNode) and slowmode < 0:
        raise Exception("Slowmode delay must be a positive integer !")

    await thread.edit(name=name if name is not None else thread.name,
                      auto_archive_duration=archive if archive is not MISSING else thread.auto_archive_duration,
                      slowmode_delay=slowmode if slowmode is not MISSING else thread.slowmode_delay,
                      reason=reason)

    return IntNode(thread.id)


async def dshell_get_thread(ctx: Message, message: Optional[Union[IntNode, StrNode]] = None):
    """
    Returns the thread object of the specified thread ID.
    """

    _CMD = "gt"

    message = ctx if message is None else await utils_get_message(ctx, message)

    # Return None if message doesn't have thread attribute (not raising error for this case)
    if not hasattr(message, 'thread'):
        return None

    thread = message.thread

    if thread is None:
        return None

    return IntNode(thread.id)


async def dshell_delete_thread(ctx: Message,
                               thread: Optional[Union[IntNode, StrNode]] = None,
                               reason: Optional[StrNode]=None):
    """
    Deletes a thread.
    """

    _CMD = "dt"

    target_message = ctx if thread is None else await utils_get_message(ctx, thread)

    _validate_has_attribute(thread, 'thread', f"[{_CMD}] The specified message does not have a thread !")
    _validate_optional_string(reason, "reason", _CMD)

    if target_message.thread is None:
        raise Exception("The specified message does not have a thread !")

    await target_message.thread.delete(reason=reason)

    return IntNode(target_message.thread.id)

async def dshell_create_category(ctx: Message,
                                   name: StrNode,
                                   position: IntNode = MISSING,
                                   permissions: PermissionNode = MISSING,
                                   reason: Optional[StrNode] = None):
    """
    Creates a category on the server
    """

    _CMD = "cca"

    _validate_missing_or_type(position, "Position", PermissionNode, _CMD)
    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    _validate_missing_or_type(permissions, "Permissions", PermissionNode, _CMD)
    _validate_missing_or_type(position, "Position", IntNode, _CMD)


    created_category = await ctx.guild.create_category(StrNode(name),
                                                      position=position,
                                                      overwrites=permissions.value if permissions is not MISSING else permissions,
                                                      reason=reason)

    return IntNode(created_category.id)

async def dshell_edit_category(ctx: Message,
                                category,
                                name: Optional[StrNode]=None,
                                position=MISSING,
                                permissions: PermissionNode = MISSING,
                                reason: Optional[StrNode]=None):
    """
    Edits a category on the server
    """
    _CMD = "eca"

    _validate_missing_or_type(position, "Position", PermissionNode, _CMD)
    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_int(category, "Category", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    _validate_missing_or_type(permissions, "Permissions", PermissionNode, _CMD)

    category_to_edit = ctx.channel.guild.get_channel(category)

    if category_to_edit is None or not isinstance(category_to_edit, CategoryChannel):
        raise Exception(f"Category {category} not found or is not a category !")

    await category_to_edit.edit(name=name if name is not None else category_to_edit.name,
                                position=position if position is not MISSING else category_to_edit.position,
                                overwrites=permissions.value if permissions is not MISSING else category_to_edit.overwrites,
                                reason=reason)

    return IntNode(category_to_edit.id)

async def dshell_delete_category(ctx: Message,
                                 category: Optional[IntNode]=None,
                                 reason: Optional[StrNode]=None):
    """
    Deletes a category.
    """
    _CMD = "dca"

    if category is None and ctx.channel.category is None:
        raise Exception("Category must be specified !")

    category_to_delete = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    if category_to_delete is None or not isinstance(category_to_delete, CategoryChannel):
        raise Exception(f"Category {category} not found or is not a category !")

    _validate_optional_string(reason, "reason", _CMD)

    await category_to_delete.delete(reason=reason)

    return IntNode(category_to_delete.id)

############################# CHANNEL INFO ##############################

async def dshell_get_channel_category_id(ctx: Message,
                                         channel: Optional[IntNode]=None):
    """
    Returns the category ID of a channel.
    """
    _CMD = "gcc"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    if channel_to_check.category is None:
        return None

    return IntNode(channel_to_check.category.id) if channel_to_check.category is not None else IntNode(0)

async def dshell_get_channel_nsfw(ctx: Message, channel: Optional[IntNode]=None) -> BoolNode:
    """
    Returns if the channel is NSFW.
    """
    _CMD = "gcnsfw"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    return BoolNode(channel_to_check.nsfw)

async def dshell_get_channel_slowmode(ctx: Message, channel: Optional[IntNode]=None):
    """
    Returns the slowmode delay of a channel.
    """
    _CMD = "gcsl"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    _validate_has_attribute(channel_to_check, 'slowmode_delay', f"[{_CMD}] Channel {channel} is not a text channel !")

    return IntNode(channel_to_check.slowmode_delay)

async def dshell_get_channel_topic(ctx: Message, channel: Optional[IntNode]=None) -> StrNode:
    """
    Returns the topic of a channel.
    """
    _CMD = "gct"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    _validate_has_attribute(channel_to_check, 'topic', f"[{_CMD}] Channel {channel} is not a text channel !")

    return StrNode(channel_to_check.topic)

async def dshell_get_channel_threads(ctx: Message, channel: Optional[IntNode]=None):
    """
    Returns the list of threads in a channel.
    """
    _CMD = "gcth"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    _validate_has_attribute(channel_to_check, 'threads', f"[{_CMD}] Channel {channel} is not a text channel !")


    threads = ListNode([])

    for thread in channel_to_check.threads:
        threads.add(IntNode(thread.id))

    return threads

async def dshell_get_channel_position(ctx: Message, channel: Optional[IntNode]=None):
    """
    Returns the position of a channel.
    """
    _CMD = "gcp"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    return IntNode(channel_to_check.position)

async def dshell_get_channel_url(ctx: Message, channel: Optional[IntNode]=None) -> StrNode:
    """
    Returns the URL of a channel.
    """
    _CMD = "gcurl"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    return StrNode(channel_to_check.jump_url)

async def dshell_get_channel_voice_members(ctx: Message, channel=None):
    """
    Returns the list of members in a voice channel.
    """
    _CMD = "gvcm"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[{_CMD}] Channel {channel} not found !")

    if not isinstance(channel_to_check, VoiceChannel):
        raise Exception(f"Channel {channel} is not a voice channel !")


    members = ListNode([])

    for member in channel_to_check.members:
        members.add(IntNode(member.id))

    return members

async def dshell_clone_channel(ctx: Message,
                               channel: Optional[IntNode]=None,
                               catagory: Optional[IntNode]=None,
                               name: Optional[StrNode]=None,
                               reason: Optional[StrNode]=None):
    """
    Clones a channel.
    """
    _CMD = "clc"

    _validate_optional_int(channel, "Channel", _CMD)
    channel_to_clone = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_optional_int(catagory, "category", _CMD)
    category_to_put = ctx.channel.category if catagory is None else ctx.channel.guild.get_channel(catagory)

    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)

    cloned_channel = await channel_to_clone.clone(name=name if name is not None else channel_to_clone.name,
                                                  reason=reason)
    if category_to_put is not None:
        await cloned_channel.edit(category=category_to_put, reason=reason)

    return IntNode(cloned_channel.id)
