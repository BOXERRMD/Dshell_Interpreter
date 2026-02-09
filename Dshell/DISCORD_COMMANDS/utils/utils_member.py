__all__ = [
    "utils_has_permissions",
]

from Dshell.full_import import (Message,
                            PermissionOverwrite)

from .utils_global import DiscordType, utils_what_discord_type_is
from .utils_type_validation import (_validate_required_int,
                                    _validate_required_dict)

async def utils_has_permissions(ctx: Message, member: int, permission: dict[None, PermissionOverwrite]) -> bool:
    """
    Return True if the member has the specified permissions.
    :param member:
    :param permission:
    :return:
    """

    _validate_required_int(member, "member", "has_perms")

    _validate_required_dict(permission, "permissions", "has_perms")

    if None not in permission:
        raise ValueError(f"permissions must have simple 'allow' permission in has_perms command, not {permission.keys()}")

    discord_type, member = utils_what_discord_type_is(ctx, member)

    if discord_type != DiscordType.MEMBER:
        raise ValueError(f"No member found with ID {member} in has_perms command.")

    return (member.guild_permissions & permission[None].pair()[0]) == permission[None].pair()[0]
