from Dshell.full_import import (Message,
                           Embed,
                           MISSING,
                           Member,
                           Permissions,
                           Role)

from ..DshellParser.ast_nodes import ListNode

from Dshell.full_import import (datetime,
                           timedelta,
                           UTC)

from .utils.utils_type_validation import (_validate_optional_number,
                                          _validate_optional_string,
                                          _validate_optional_int,
                                          _validate_required_int,
                                          _validate_required_string,
                                          _validate_required_bool,
                                          _validate_optional_embed,
                                          _validate_missing_or_type)

__all__ = [
    "dshell_send_private_message",
    "dshell_ban_member",
    "dshell_unban_member",
    "dshell_kick_member",
    "dshell_rename_member",
    "dshell_check_permissions",
    "dshell_timeout_member",
    "dshell_move_member",
    "dshell_give_member_roles",
    "dshell_remove_member_roles"
]

async def dshell_send_private_message(ctx: Message, message: str = None, member: int = None, delete: int = None, embeds = None, ):
    """
    Envoie un message privé à un membre Discord.
    
    Cette fonction envoie un message en privé (DM) à un membre du serveur.
    Si aucun membre n'est spécifié, le message est envoyé à l'auteur de la commande.
    Supporte les embeds et la suppression automatique après un délai.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param message: Le contenu du message à envoyer (optionnel)
    :type message: str | None
    :param member: L'ID du membre destinataire (par défaut: auteur de la commande)
    :type member: int | None
    :param delete: Temps en secondes avant suppression automatique du message (optionnel)
    :type delete: int | None
    :param embeds: Embed(s) à inclure (Embed unique ou ListNode) (optionnel)
    :type embeds: Embed | ListNode | None
    :return: L'ID du message envoyé
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé
    :raises Exception: Si le format des embeds est invalide
    
    Example:
        >>> # Envoyer un message à un membre
        >>> await dshell_send_private_message(ctx, "Bonjour!", member=123456789)
        111222333
        >>> # Envoyer à l'auteur avec suppression après 10s
        >>> await dshell_send_private_message(ctx, "Message temporaire", delete=10)
        444555666
    """
    _CMD = "spm"

    _validate_optional_string(message, "Message", _CMD)
    _validate_optional_int(member, "Member", _CMD)
    _validate_optional_number(delete, "Delete", _CMD)
    _validate_optional_embed(embeds, "Embeds", _CMD)

    member_to_send = ctx.author if member is None else ctx.channel.guild.get_member(member)

    if member_to_send is None:
        raise Exception(f'Member {member} not found!')



    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    else:
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    sended_message = await member_to_send.send(message, delete_after=delete, embeds=embeds)

    return sended_message.id


async def dshell_ban_member(ctx: Message, member: int, reason: str = MISSING):
    """
    Bannit un membre du serveur Discord.
    
    Cette fonction bannit définitivement un membre du serveur. Le membre
    ne pourra plus rejoindre le serveur à moins d'être débanni.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param member: L'ID du membre à bannir
    :type member: int
    :param reason: Raison du bannissement (apparaît dans les logs Discord) (optionnel)
    :type reason: str | MISSING
    :return: L'ID du membre banni
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé dans le serveur
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> await dshell_ban_member(ctx, 123456789, reason="Spam")
        123456789
    """
    _CMD = "bm"

    _validate_required_int(member, "Member", _CMD)
    _validate_missing_or_type(reason, "Reason", str, _CMD)
    
    banned_member = ctx.channel.guild.get_member(member)

    if not banned_member:
        raise Exception(f'Member {member} not found in the server !')

    await ctx.channel.guild.ban(banned_member, reason=reason)

    return banned_member.id


async def dshell_unban_member(ctx: Message, user: int, reason: str = MISSING):
    """
    Débannit un utilisateur du serveur Discord.
    
    Cette fonction retire le bannissement d'un utilisateur, lui permettant
    de rejoindre à nouveau le serveur.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param user: L'ID de l'utilisateur à débannir
    :type user: int
    :param reason: Raison du débannissement (apparaît dans les logs Discord) (optionnel)
    :type reason: str | MISSING
    :return: L'ID de l'utilisateur débanni
    :rtype: int
    :raises Exception: Si l'utilisateur n'est pas dans la liste des bannis
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> await dshell_unban_member(ctx, 123456789, reason="Appel accepté")
        123456789
    """
    _CMD = "um"

    _validate_required_int(user, "User", _CMD)
    _validate_missing_or_type(reason, "Reason", str, _CMD)
    
    banned_users = ctx.channel.guild.bans()
    user_to_unban = None

    async for ban_entry in banned_users:
        if ban_entry.user.id == user:
            user_to_unban = ban_entry.user
            break

    if not user_to_unban:
        raise Exception(f'User {user} not found in the banned list')

    await ctx.channel.guild.unban(user_to_unban, reason=reason)

    return user_to_unban.id


async def dshell_kick_member(ctx: Message, member: int, reason: str = MISSING):
    """
    Expulse un membre du serveur Discord.
    
    Cette fonction expulse un membre du serveur. Contrairement au bannissement,
    le membre peut rejoindre à nouveau le serveur avec une nouvelle invitation.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param member: L'ID du membre à expulser
    :type member: int
    :param reason: Raison de l'expulsion (apparaît dans les logs Discord) (optionnel)
    :type reason: str | MISSING
    :return: L'ID du membre expulsé
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé dans le serveur
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> await dshell_kick_member(ctx, 123456789, reason="Comportement inapproprié")
        123456789
    """
    _CMD = "km"

    _validate_required_int(member, "Member", _CMD)
    _validate_missing_or_type(reason, "Reason", str, _CMD)
    
    kicked_member = ctx.channel.guild.get_member(member)

    if not kicked_member:
        raise Exception(f'Member {member} not found in the server !')

    await ctx.channel.guild.kick(kicked_member, reason=reason)

    return kicked_member.id


async def dshell_timeout_member(ctx: Message, duration: int, member=None, reason: str = MISSING):
    """
    Met un membre en timeout (temps mort) pour une durée spécifiée.
    
    Cette fonction empêche temporairement un membre d'envoyer des messages,
    réagir, ou parler dans les canaux vocaux pendant la durée spécifiée.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param duration: Durée du timeout en secondes
    :type duration: int
    :param member: L'ID du membre à timeout (par défaut: auteur de la commande)
    :type member: int | None
    :param reason: Raison du timeout (apparaît dans les logs Discord) (optionnel)
    :type reason: str | MISSING
    :return: L'ID du membre mis en timeout
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé
    :raises TypeError: Si duration n'est pas un entier
    :raises ValueError: Si duration est négatif
    
    Example:
        >>> # Timeout de 60 secondes
        >>> await dshell_timeout_member(ctx, 60, member=123456789, reason="Spam")
        123456789
    """
    _CMD = "tm"

    _validate_required_int(duration, "Duration", _CMD)
    _validate_optional_int(member, "Member", _CMD)
    _validate_missing_or_type(reason, "Reason", str, _CMD)
    
    target_member = ctx.author if member is None else ctx.channel.guild.get_member(member)

    if not target_member:
        raise Exception(f'Member {member} not found in the server !')

    if not isinstance(duration, int):
        raise TypeError("Duration must be an integer representing seconds.")

    if duration < 0:
        raise ValueError("Duration must be a non-negative integer.")

    await target_member.timeout(until=datetime.now(UTC) + timedelta(seconds=duration), reason=reason)

    return target_member.id


async def dshell_rename_member(ctx: Message, new_name, member=None):
    """
    Renomme un membre sur le serveur (change son surnom).
    
    Cette fonction modifie le surnom (nickname) d'un membre sur le serveur.
    Le nom d'utilisateur global Discord n'est pas modifié.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param new_name: Le nouveau surnom du membre
    :type new_name: str
    :param member: L'ID du membre à renommer (optionnel)
    :type member: int | None
    :return: L'ID du membre renommé
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé
    :raises TypeError: Si new_name n'est pas une chaîne
    
    Example:
        >>> await dshell_rename_member(ctx, "Super Modérateur", member=123456789)
        123456789
    """
    _CMD = "rm"

    _validate_required_string(new_name, "New name", _CMD)
    _validate_optional_int(member, "Member", _CMD)
    
    renamed_member = ctx.channel.guild.get_member(member)

    if not renamed_member:
        raise Exception(f'Member {member} not found in the server !')

    await renamed_member.edit(nick=new_name)

    return renamed_member.id


async def dshell_check_permissions(ctx: Message, permissions, member=None):
    """
    Vérifie si un membre possède des permissions spécifiques sur le serveur.
    
    Cette fonction vérifie si un membre possède au moins une des permissions
    spécifiées par le code de permissions fourni.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param permissions: Code des permissions à vérifier (entier de drapeaux)
    :type permissions: int
    :param member: L'ID du membre à vérifier (par défaut: auteur de la commande)
    :type member: int | None
    :return: True si le membre a au moins une des permissions, False sinon
    :rtype: bool
    :raises Exception: Si le membre n'est pas trouvé
    :raises TypeError: Si permissions n'est pas un entier
    
    Example:
        >>> # Vérifier permission administrateur (8)
        >>> await dshell_check_permissions(ctx, 8, member=123456789)
        True
    """
    _CMD = "cp"

    _validate_required_int(permissions, "Permissions", _CMD)
    _validate_optional_int(member, "Member", _CMD)
    
    target_member: Member = ctx.author if member is None else ctx.channel.guild.get_member(member)

    if not target_member:
        raise Exception(f'Member {member} not found in the server !')

    if not isinstance(permissions, int):
        raise TypeError("Permissions must be an integer representing permissions flags.")

    permissions_to_check = Permissions(permissions)
    member_permissions = target_member.guild_permissions

    if (permissions_to_check.value & member_permissions.value) != 0:
        return True
    return False


async def dshell_move_member(ctx: Message, member=None, channel=None, disconnect: bool = False, reason=None):
    """
    Déplace un membre vers un autre canal vocal ou le déconnecte.
    
    Cette fonction permet de déplacer un membre d'un canal vocal à un autre,
    ou de le déconnecter complètement des canaux vocaux.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param member: L'ID du membre à déplacer (par défaut: auteur de la commande)
    :type member: int | None
    :param channel: L'ID du canal vocal de destination (optionnel)
    :type channel: int | None
    :param disconnect: Si True, déconnecte le membre au lieu de le déplacer
    :type disconnect: bool
    :param reason: Raison du déplacement (apparaît dans les logs Discord) (optionnel)
    :type reason: str | None
    :return: L'ID du membre déplacé
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé
    :raises Exception: Si le membre n'est pas dans un canal vocal
    :raises Exception: Si le canal de destination n'est pas trouvé
    
    Example:
        >>> # Déplacer vers canal 999888777
        >>> await dshell_move_member(ctx, member=123456789, channel=999888777)
        123456789
        >>> # Déconnecter du vocal
        >>> await dshell_move_member(ctx, member=123456789, disconnect=True)
        123456789
    """
    _CMD = "mm"

    _validate_optional_int(member, "Member", _CMD)
    _validate_optional_int(channel, "Channel", _CMD)
    _validate_required_bool(disconnect, "Disconnect", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    
    target_member = ctx.author if member is None else ctx.channel.guild.get_member(member)
    target_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if not target_member:
        raise Exception(f'Member {member} not found in the server !')

    if target_member.voice.channel is None:
        raise Exception(f'Member {target_member.name} is not in a voice channel !')

    if not target_channel:
        raise Exception(f'Channel {channel} not found in the server !')

    if disconnect:
        await target_member.move_to(None, reason=reason)
    else:
        await target_member.move_to(target_channel, reason=reason)

    return target_member.id


async def dshell_give_member_roles(ctx: Message, roles, member=None, reason=None):
    """
    Attribue un ou plusieurs rôles à un membre.
    
    Cette fonction ajoute des rôles à un membre sans retirer ses rôles existants.
    Peut attribuer un seul rôle (int) ou plusieurs rôles (liste/ListNode).
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param roles: L'ID d'un rôle ou une liste d'IDs de rôles à attribuer
    :type roles: int | ListNode | list
    :param member: L'ID du membre (par défaut: auteur de la commande)
    :type member: int | None
    :param reason: Raison de l'attribution (apparaît dans les logs Discord) (optionnel)
    :type reason: str | None
    :return: L'ID du membre modifié
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé
    :raises Exception: Si un rôle n'est pas trouvé
    
    Example:
        >>> # Attribuer un rôle
        >>> await dshell_give_member_roles(ctx, 111222333, member=123456789)
        123456789
        >>> # Attribuer plusieurs rôles
        >>> await dshell_give_member_roles(ctx, ListNode([111, 222, 333]))
        123456789
    """
    # roles peut être int ou list, validation manuelle dans le corps de la fonction
    _CMD = "gmr"

    _validate_optional_int(member, "Member", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    
    target_member = ctx.author if member is None else ctx.guild.get_member(member)

    if target_member is None:
        raise Exception(f'Member {member} not found in the server !')

    if isinstance(roles, int):
        roles = (roles, )

    list_roles: list[Role] = []
    for i in roles:
        role_to_give = ctx.guild.get_role(i)

        if role_to_give is None:
            raise Exception(f'Role {i} not found in the server !')

        list_roles.append(role_to_give)

    list_roles.extend(target_member.roles)

    await target_member.edit(roles=list_roles, reason=str(reason))

    return target_member.id


async def dshell_remove_member_roles(ctx: Message, roles, member=None, reason=None):
    """
    Retire un ou plusieurs rôles d'un membre.
    
    Cette fonction retire des rôles spécifiques d'un membre tout en conservant
    ses autres rôles. Peut retirer un seul rôle (int) ou plusieurs (liste/ListNode).
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param roles: L'ID d'un rôle ou une liste d'IDs de rôles à retirer
    :type roles: int | ListNode | list
    :param member: L'ID du membre (par défaut: auteur de la commande)
    :type member: int | None
    :param reason: Raison du retrait (apparaît dans les logs Discord) (optionnel)
    :type reason: str | None
    :return: L'ID du membre modifié
    :rtype: int
    :raises Exception: Si le membre n'est pas trouvé
    :raises Exception: Si le membre n'a pas un des rôles spécifiés
    
    Example:
        >>> # Retirer un rôle
        >>> await dshell_remove_member_roles(ctx, 111222333, member=123456789)
        123456789
        >>> # Retirer plusieurs rôles
        >>> await dshell_remove_member_roles(ctx, ListNode([111, 222]))
        123456789
    """
    # roles peut être int ou list, validation manuelle dans le corps de la fonction
    _CMD = "rmr"

    _validate_optional_int(member, "Member", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    
    target_member = ctx.author if member is None else ctx.guild.get_member(member)

    if target_member is None:
        raise Exception(f'Member {member} not found in the server !')

    if isinstance(roles, int):
        roles = (roles,)

    list_roles: set[Role] = set()
    for i in roles:
        role_to_give = target_member.get_role(i)

        if role_to_give is None:
            raise Exception(f"{target_member.name} member doesn't have {i} role !")

        list_roles.add(role_to_give)

    new_set_role = list(set(target_member.roles) - list_roles)

    await target_member.edit(roles=new_set_role, reason=str(reason))

    return target_member.id
