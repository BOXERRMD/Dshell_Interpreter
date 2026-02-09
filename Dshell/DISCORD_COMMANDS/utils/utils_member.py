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
    Vérifie si un membre possède les permissions spécifiées.
    
    Cette fonction vérifie si un membre du serveur Discord possède un ensemble
    de permissions donné en comparant ses permissions actuelles avec celles requises.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param member: L'ID du membre à vérifier
    :type member: int
    :param permission: Dictionnaire de permissions avec None comme clé et PermissionOverwrite comme valeur
    :type permission: dict[None, PermissionOverwrite]
    :return: True si le membre possède les permissions, False sinon
    :rtype: bool
    :raises ValueError: Si le membre n'est pas trouvé ou si le format des permissions est invalide
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> perms = {None: PermissionOverwrite(administrator=True)}
        >>> await utils_has_permissions(ctx, 123456789, perms)
        True
    """
    _CMD = "has_perms"
    _validate_required_int(member, "member", _CMD)

    _validate_required_dict(permission, "permissions", _CMD)

    if None not in permission:
        raise ValueError(f"permissions must have simple 'allow' permission in has_perms command, not {permission.keys()}")

    discord_type, member = utils_what_discord_type_is(ctx, member)

    if discord_type != DiscordType.MEMBER:
        raise ValueError(f"No member found with ID {member} in has_perms command.")

    return (member.guild_permissions & permission[None].pair()[0]) == permission[None].pair()[0]
