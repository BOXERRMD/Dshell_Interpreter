from Dshell.full_import import (Message,
                           MISSING,
                           _MissingSentinel,
                           Member,
                           Role,
                           PermissionOverwrite,
                           CategoryChannel,
                           VoiceChannel,
                           PartialMessage)

from .._DshellParser.ast_nodes import ListNode

from Dshell.full_import import search

from Dshell.full_import import sleep

from Dshell.full_import import Union

from .utils.utils_message import utils_get_message
from .utils.utils_thread import utils_get_thread
from .utils.utils_type_validation import (_validate_optional_string,
                                          _validate_optional_int,
                                          _validate_optional_bool,
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
]


async def dshell_get_channel(ctx: Message, name):
    """
    Returns the channel object of the channel where the command was executed or the specified channel.
    """

    if isinstance(name, str):
        return next((c.id for c in ctx.channel.guild.channels if c.name == name), None)

    raise Exception(f"Channel must be an integer or a string, not {type(name)} !")


async def dshell_get_channels(ctx: Message, name=None, regex=None):
    """
    Returns a list of channels with the same name and/or matching the same regex.
    If neither is set, it will return all channels in the server.
    """
    _validate_optional_string(name, "Name", "gcs")
    _validate_optional_string(regex, "Regex", "gcs")

    channels = ListNode([])

    for channel in ctx.channel.guild.channels:
        if name is not None and channel.name == str(name):
            channels.add(channel.id)

        elif regex is not None and search(regex, channel.name):
            channels.add(channel.id)

    return channels

async def dshell_get_channels_in_category(ctx: Message,
                                          category=None,
                                          name=None,
                                          regex=None):
    """
    Returns a list of channels in a specific category with the same name and/or matching the same regex.
    If neither is set, it will return all channels in the specified category.
    """

    _validate_optional_int(category, "Category", "gccs")

    if category is None and ctx.channel.category is not None:
        category = ctx.channel.category.id

    _validate_not_none(category, "[gccs] The current channel has no category, you must specify a category ID !")

    _validate_optional_string(name, "Name", "gccs")
    _validate_optional_string(regex, "Regex", "gccs")

    channels = ListNode([])

    category_channel = ctx.channel.guild.get_channel(category)
    if category_channel is None or not hasattr(category_channel, 'channels'):
        raise Exception(f"Category {category} not found or does not contain channels !")

    for channel in category_channel.channels:
        if name is not None and channel.name == str(name):
            channels.add(channel.id)

        elif regex is not None and search(regex, channel.name):
            channels.add(channel.id)

    return channels

async def dshell_create_text_channel(ctx: Message,
                                     name,
                                     category=None,
                                     position=MISSING,
                                     slowmode=MISSING,
                                     topic=MISSING,
                                     nsfw=MISSING,
                                     permissions: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                     reason=None):
    """
    Creates a text channel on the server
    """

    _validate_required_string(name, "Name", "cc")

    _validate_optional_int(category, "Category", "cc")

    _validate_missing_or_type(position, "Position", int, "cc")

    _validate_missing_or_type(slowmode, "Slowmode", int, "cc")

    _validate_missing_or_type(topic, "Topic", str, "cc")

    _validate_missing_or_type(nsfw, "NSFW", bool, "cc")

    _validate_missing_or_type(permissions, "Permissions", dict, "cc")
    
    _validate_optional_string(reason, "Reason", "cc")

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_text_channel(str(name),
                                                          category=channel_category,
                                                          position=position,
                                                          slowmode_delay=slowmode,
                                                          topic=topic,
                                                          nsfw=nsfw,
                                                          overwrites=permissions,
                                                          reason=reason)

    return created_channel.id


async def dshell_create_voice_channel(ctx: Message,
                                      name,
                                      category=None,
                                      position=MISSING,
                                      bitrate=MISSING,
                                      permissions: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                      reason=None):
    """
    Creates a voice channel on the server
    """
    _validate_required_string(name, "Name", "cvc")

    _validate_optional_int(category, "Category", "cvc")

    _validate_missing_or_type(position, "Position", int, "cvc")

    _validate_missing_or_type(bitrate, "Bitrate", int, "cvc")
    
    _validate_optional_string(reason, "Reason", "cvc")

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_voice_channel(str(name),
                                                           category=channel_category,
                                                           position=position,
                                                           bitrate=bitrate,
                                                           overwrites=permissions,
                                                           reason=reason)

    return created_channel.id


async def dshell_delete_channel(ctx: Message,
                                channel=None,
                                reason=None,
                                timeout=0):
    """
    Deletes a channel.
    You can add a waiting time before it is deleted (in seconds)
    """
    _validate_optional_int(timeout, "Timeout", "dc")
    _validate_optional_string(reason, "Reason", "dc")

    channel_to_delete = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_delete, f"[dc] Channel {channel} not found !")

    await sleep(timeout)

    await channel_to_delete.delete(reason=reason)

    return channel_to_delete.id


async def dshell_delete_channels(ctx: Message, name=None, regex=None, reason=None):
    """
    Deletes all channels with the same name and/or matching the same regex.
    If neither is set, it will delete all channels with the same name as the one where the command was executed.
    """
    _validate_optional_string(name, "Name", "dcs")
    _validate_optional_string(regex, "Regex", "dcs")
    _validate_optional_string(reason, "Reason", "dcs")

    for channel in ctx.channel.guild.channels:

        if name is not None and channel.name == str(name):
            await channel.delete(reason=reason)

        elif regex is not None and search(regex, channel.name):
            await channel.delete(reason=reason)


async def dshell_edit_text_channel(ctx: Message,
                                   channel=None,
                                   name=None,
                                   category=MISSING,
                                   position=MISSING,
                                   slowmode=MISSING,
                                   topic=MISSING,
                                   nsfw=MISSING,
                                   permissions: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                   reason=None):
    """
    Edits a text channel on the server
    """
    _validate_optional_string(name, "Name", "ec")

    _validate_missing_or_type(position, "Position", int, "ec")

    _validate_missing_or_type(category, "Category", int, "ec")

    _validate_missing_or_type(slowmode, "Slowmode", int, "ec")

    _validate_missing_or_type(topic, "Topic", str, "ec")

    _validate_missing_or_type(nsfw, "NSFW", bool, "ec")

    _validate_missing_or_type(permissions, "Permissions", dict, "ec")

    _validate_optional_string(reason, "Reason", "ec")

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
                               overwrites=permissions if permissions is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return channel_to_edit.id


async def dshell_edit_voice_channel(ctx: Message,
                                    channel=None,
                                    name=None,
                                    category=MISSING,
                                    position=MISSING,
                                    bitrate=MISSING,
                                    permissions: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                    reason=None):
    """
    Edits a voice channel on the server
    """
    _validate_optional_int(channel, "Channel", "evc")

    _validate_optional_string(name, "Name", "evc")

    _validate_missing_or_type(position, "Position", int, "evc")

    _validate_missing_or_type(category, "Category", int, "evc")

    _validate_missing_or_type(bitrate, "Bitrate", int, "evc")

    _validate_missing_or_type(permissions, "Permissions", dict, "evc")

    _validate_optional_string(reason, "Reason", "evc")

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)
    new_categoy = ctx.channel.category if isinstance(category, _MissingSentinel) else ctx.channel.guild.get_channel(category)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               category=new_categoy,
                               bitrate=bitrate if bitrate is not MISSING else channel_to_edit.bitrate,
                               overwrites=permissions if permissions is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return channel_to_edit.id


async def dshell_create_thread_message(ctx: Message,
                                       name,
                                       message: Union[int, str] = None,
                                       archive=MISSING,
                                       slowmode=MISSING):
    """
    Creates a thread from a message.
    """

    if message is None:
        message = ctx.id

    message = utils_get_message(ctx, message)

    _validate_required_string(name, "Name", "ct")

    _validate_missing_or_type(archive, "Auto archive duration", int, "ct")

    if isinstance(archive, int) and archive not in (60, 1440, 4320, 10080):
        raise Exception("Auto archive duration must be one of the following values: 60, 1440, 4320, 10080 !")

    _validate_missing_or_type(slowmode, "Slowmode delay", int, "ct")

    _validate_missing_or_type(slowmode, "Slowmode delay", int, "ct")

    if isinstance(slowmode, int) and slowmode < 0:
        raise Exception("Slowmode delay must be a positive integer !")

    if isinstance(message, PartialMessage):
        m = await message.fetch()
    else:
        m = message

    thread = await m.create_thread(name=name,
                    auto_archive_duration=archive,
                    slowmode_delay=slowmode)

    return thread.id

async def dshell_edit_thread(ctx: Message,
                             thread: Union[int, str] = None,
                             name=None,
                             archive=MISSING,
                             slowmode=MISSING,
                             reason=None):
    """ Edits a thread.
    """
    if thread is None:
        thread = ctx.thread

    if thread is None:
        raise Exception("Thread must be specified !")

    thread = await utils_get_thread(ctx, thread)

    _validate_missing_or_type(name, "Name", str, "et")

    _validate_missing_or_type(archive, "Auto archive duration", int, "et")

    if isinstance(archive, int) and archive not in (60, 1440, 4320, 10080):
        raise Exception("Auto archive duration must be one of the following values: 60, 1440, 4320, 10080 !")

    _validate_missing_or_type(slowmode, "Slowmode delay", int, "et")

    _validate_missing_or_type(slowmode, "Slowmode delay", int, "et")

    if isinstance(slowmode, int) and slowmode < 0:
        raise Exception("Slowmode delay must be a positive integer !")

    await thread.edit(name=name if name is not None else thread.name,
                      auto_archive_duration=archive if archive is not MISSING else thread.auto_archive_duration,
                      slowmode_delay=slowmode if slowmode is not MISSING else thread.slowmode_delay,
                      reason=reason)


async def dshell_get_thread(ctx: Message, message: Union[int, str] = None):
    """
    Returns the thread object of the specified thread ID.
    """

    if message is None:
        message = ctx.id

    target_message = utils_get_message(ctx, message)
    if isinstance(target_message, PartialMessage):
        message = await target_message.fetch()
    else:
        message = target_message

    # Return None if message doesn't have thread attribute (not raising error for this case)
    if not hasattr(message, 'thread'):
        return None

    thread = message.thread

    if thread is None:
        return None

    return thread.id


async def dshell_delete_thread(ctx: Message, thread: Union[int, str] = None, reason=None):
    """
    Deletes a thread.
    """

    if thread is None:
        thread = ctx.id

    target_message = utils_get_message(ctx, thread)
    if isinstance(target_message, PartialMessage):
        thread = await target_message.fetch()
    else:
        thread = target_message

    _validate_has_attribute(thread, 'thread', "[dt] The specified message does not have a thread !")

    if thread.thread is None:
        raise Exception("The specified message does not have a thread !")

    await thread.thread.delete(reason=reason)

    return thread.thread.id

async def dshell_create_category(ctx: Message,
                                   name,
                                   position=MISSING,
                                   permissions: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                   reason=None):
    """
    Creates a category on the server
    """

    _validate_missing_or_type(position, "Position", int, "cca")

    created_category = await ctx.guild.create_category(str(name),
                                                      position=position,
                                                      overwrites=permissions,
                                                      reason=reason)

    return created_category.id

async def dshell_edit_category(ctx: Message,
                                category,
                                name=None,
                                position=MISSING,
                                permissions: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                reason=None):
    """
    Edits a category on the server
    """
    _validate_missing_or_type(position, "Position", int, "eca")

    category_to_edit = ctx.channel.guild.get_channel(category)

    if category_to_edit is None or not isinstance(category_to_edit, CategoryChannel):
        raise Exception(f"Category {category} not found or is not a category !")

    await category_to_edit.edit(name=name if name is not None else category_to_edit.name,
                                position=position if position is not MISSING else category_to_edit.position,
                                overwrites=permissions if permissions is not MISSING else category_to_edit.overwrites,
                                reason=reason)

    return category_to_edit.id

async def dshell_delete_category(ctx: Message, category=None, reason=None):
    """
    Deletes a category.
    """

    if category is None and ctx.channel.category is None:
        raise Exception("Category must be specified !")

    category_to_delete = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    if category_to_delete is None or not isinstance(category_to_delete, CategoryChannel):
        raise Exception(f"Category {category} not found or is not a category !")

    await category_to_delete.delete(reason=reason)

    return category_to_delete.id

############################# CHANNEL INFO ##############################

async def dshell_get_channel_category_id(ctx: Message, channel=None):
    """
    Returns the category ID of a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gcc] Channel {channel} not found !")

    if channel_to_check.category is None:
        return None

    return channel_to_check.category.id if channel_to_check.category is not None else 0

async def dshell_get_channel_nsfw(ctx: Message, channel=None):
    """
    Returns if the channel is NSFW.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gcnsfw] Channel {channel} not found !")

    return channel_to_check.nsfw

async def dshell_get_channel_slowmode(ctx: Message, channel=None):
    """
    Returns the slowmode delay of a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gcsl] Channel {channel} not found !")

    _validate_has_attribute(channel_to_check, 'slowmode_delay', f"[gcsl] Channel {channel} is not a text channel !")

    return channel_to_check.slowmode_delay

async def dshell_get_channel_topic(ctx: Message, channel=None):
    """
    Returns the topic of a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gct] Channel {channel} not found !")

    _validate_has_attribute(channel_to_check, 'topic', f"[gct] Channel {channel} is not a text channel !")

    return channel_to_check.topic

async def dshell_get_channel_threads(ctx: Message, channel=None):
    """
    Returns the list of threads in a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gcth] Channel {channel} not found !")

    _validate_has_attribute(channel_to_check, 'threads', f"[gcth] Channel {channel} is not a text channel !")


    threads = ListNode([])

    for thread in channel_to_check.threads:
        threads.add(thread.id)

    return threads

async def dshell_get_channel_position(ctx: Message, channel=None):
    """
    Returns the position of a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gcp] Channel {channel} not found !")

    return channel_to_check.position

async def dshell_get_channel_url(ctx: Message, channel=None):
    """
    Returns the URL of a channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gcurl] Channel {channel} not found !")

    return channel_to_check.jump_url

async def dshell_get_channel_voice_members(ctx: Message, channel=None):
    """
    Returns the list of members in a voice channel.
    """

    channel_to_check = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    _validate_not_none(channel_to_check, f"[gvcm] Channel {channel} not found !")

    if not isinstance(channel_to_check, VoiceChannel):
        raise Exception(f"Channel {channel} is not a voice channel !")


    members = ListNode([])

    for member in channel_to_check.members:
        members.add(member.id)

    return members
