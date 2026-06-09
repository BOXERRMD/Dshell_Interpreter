from Dshell.full_import import (Message,
                            PartialMessage,
                            AllowedMentions,
                                search,
                                Optional,
                                NotFound,
                                Forbidden,
                                HTTPException)

from ...DshellInterpreteur.cached_messages import dshell_cached_messages
from ...DshellParser.ast_nodes import StrNode, BoolNode, IntNode

from Dshell.full_import import Union

from .utils_type_validation import (_validate_optional_bool,
                                    _validate_required_bool)

async def utils_get_message(ctx: Message, message: Union[IntNode, StrNode]) -> Message:
    """
    Récupère l'objet message Discord à partir d'un ID ou d'un lien.
    
    Cette fonction permet de récupérer un message Discord soit par son ID numérique,
    soit par son lien URL complet. Les messages sont mis en cache pour améliorer
    les performances. Le message doit être dans le même serveur que la commande.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param message: L'ID du message (int) ou le lien Discord complet (str)
    :type message: Union[int, str]
    :return: L'objet message (PartialMessage si non en cache, Message sinon)
    :rtype: Union[PartialMessage, Message]
    :raises Exception: Si le format du lien est invalide
    :raises Exception: Si le message n'est pas du même serveur
    :raises Exception: Si le type du paramètre est invalide
    
    Example:
        >>> # Par ID
        >>> msg = utils_get_message(ctx, 123456789)
        >>> # Par lien
        >>> msg = utils_get_message(ctx, "https://discord.com/channels/111/222/333")
    """
    cached_messages = dshell_cached_messages.get()

    if isinstance(message, IntNode):
        if message in cached_messages:
            return cached_messages[message]

        cached_messages[message] = await utils_fetch_partial_message(ctx.channel.get_partial_message(message))
        dshell_cached_messages.set(cached_messages)
        return cached_messages[message]

    elif isinstance(message, StrNode):
        match = search(r'https://discord\.com/channels/(\d+)/(\d+)/(\d+)', message)
        if not match:
            raise Exception("Invalid message link format. Use a valid Discord message link.")
        guild_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        if guild_id != ctx.guild.id:
            raise Exception("The message must be from the same server as the command !")

        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            raise Exception(f"Channel with ID {channel_id} not found in guild {ctx.guild.name}.")
        cached_messages[message_id] = await utils_fetch_partial_message(channel.get_partial_message(message_id))
        dshell_cached_messages.set(cached_messages)
        return cached_messages[message_id]

    raise Exception(f"Message must be an integer or a string, not {type(message)} !")


async def utils_fetch_partial_message(partial_message: Union[Message, PartialMessage]) -> Message:
    """
    Fetch le message et renvoie une instance de Message s'il existe
    :param ctx:
    :param partial_message:
    :return:
    """

    if not isinstance(partial_message, PartialMessage):
        if isinstance(partial_message, Message):
            return partial_message
        raise Exception(f"Expected a PartialMessage or Message, got '{type(partial_message)}' !")

    try:
        message = await partial_message.fetch()
    except NotFound:
        raise Exception(f"Message '{partial_message.id}' not found !")
    except Forbidden:
        raise Exception(f"I don't have the permission to fetch the message '{partial_message.id}' !")
    except HTTPException:
        raise Exception(f"An internal error occurred when i try to fetch the message '{partial_message.id}'. Please, contact the support if this problem persists !")
    return message


def utils_autorised_mentions(global_mentions: Optional[BoolNode] = None,
                            everyone_mention: BoolNode = BoolNode(1),
                            roles_mentions: BoolNode = BoolNode(1),
                            users_mentions: BoolNode = BoolNode(1),
                            reply_mention: BoolNode = BoolNode(0)) -> Union[BoolNode, 'AllowedMentions']:
    """
    Crée un objet AllowedMentions pour contrôler les mentions Discord autorisées.
    
    Cette fonction configure les types de mentions autorisées dans un message Discord.
    Si global_mentions est défini (True/False), il surcharge tous les autres paramètres.
    Sinon, chaque type de mention peut être contrôlé individuellement.
    
    :param global_mentions: Active (True) ou désactive (False) toutes les mentions, surcharge les autres paramètres si défini
    :type global_mentions: bool | None
    :param everyone_mention: Autorise les mentions @everyone et @here
    :type everyone_mention: bool
    :param roles_mentions: Autorise les mentions de rôles
    :type roles_mentions: bool
    :param users_mentions: Autorise les mentions d'utilisateurs
    :type users_mentions: bool
    :param reply_mention: Mentionne l'auteur du message auquel on répond
    :type reply_mention: bool
    :return: Objet AllowedMentions configuré
    :rtype: AllowedMentions
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> # Autoriser uniquement les mentions d'utilisateurs
        >>> mentions = utils_autorised_mentions(
        ...     everyone_mention=False,
        ...     roles_mentions=False,
        ...     users_mentions=True
        ... )
        >>> # Désactiver toutes les mentions
        >>> mentions = utils_autorised_mentions(global_mentions=False)
    """
    _CMD = "autorised_mentions"

    _validate_optional_bool(global_mentions, "Mention parameter", _CMD)

    _validate_required_bool(everyone_mention, "Everyone mention parameter", _CMD)

    _validate_required_bool(roles_mentions, "Roles mention parameter", _CMD)

    _validate_required_bool(users_mentions, "Users mention parameter", _CMD)

    _validate_required_bool(reply_mention, "Reply mention parameter", _CMD)

    if global_mentions:
        return AllowedMentions.all()

    elif not global_mentions:
        return AllowedMentions.none()

    else:
        return AllowedMentions(everyone=everyone_mention,
                               roles=roles_mentions,
                               users=users_mentions,
                               replied_user=reply_mention)


