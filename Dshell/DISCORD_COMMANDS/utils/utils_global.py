__all__ = [
    "utils_len",
    "utils_random",
    "utils_get_name",
    "utils_get_id",
    "utils_get_roles",
    "utils_what_discord_type_is",
    "utils_build_colour",
    "DiscordType"
]

from Dshell.full_import import StrEnum

from Dshell.full_import import (Union,
                            Optional)

from Dshell.full_import import (Message,
                           Guild,
                           Member,
                           Role,
                           TextChannel,
                           VoiceChannel,
                           CategoryChannel,
                           ForumChannel,
                           Thread,
                           Colour,
                           get)

from Dshell.full_import import (random,
                            choice)

from ..._DshellParser.ast_nodes import ListNode

from .utils_type_validation import (_validate_optional_list_node,
                                    _validate_required_int,
                                    _validate_required_string)


class DiscordType(StrEnum):
    MEMBER = "member"
    ROLE = "role"
    TEXT_CHANNEL = "text_channel"
    VOICE_CHANNEL = "voice_channel"
    CATEGORY_CHANNEL = "category_channel"
    FORUM_CHANNEL = "forum_channel"
    THREAD = "thread"
    UNKNOWN = "unknown"

def utils_what_discord_type_is(ctx: Union[Message, Guild], value: int) -> tuple[str, Union[Member, Role, TextChannel, VoiceChannel, CategoryChannel, ForumChannel, Thread, None]]:
    """
    Identifie le type Discord d'un ID et retourne l'objet correspondant.
    
    Cette fonction utilitaire détermine si un ID correspond à un membre, un rôle,
    un canal (textuel, vocal, catégorie, forum) ou un thread, et retourne
    l'objet Discord correspondant avec son type.
    
    :param ctx: Le contexte (Message ou Guild)
    :type ctx: Union[Message, Guild]
    :param value: L'ID Discord à identifier
    :type value: int
    :return: Tuple (type_discord, objet) où type_discord est une valeur DiscordType et objet est l'instance Discord ou None
    :rtype: tuple[str, Union[Member, Role, TextChannel, VoiceChannel, CategoryChannel, ForumChannel, Thread, None]]
    
    Example:
        >>> discord_type, obj = utils_what_discord_type_is(ctx, 123456789)
        >>> if discord_type == DiscordType.MEMBER:
        ...     print(f"C'est un membre: {obj.name}")
    """
    guild = ctx if isinstance(ctx, Guild) else ctx.guild

    if member := guild.get_member(value):
        return DiscordType.MEMBER, member

    elif role := guild.get_role(value):
        return DiscordType.ROLE, role

    elif (channel := guild.get_channel(value)) and isinstance(channel, TextChannel):
        return DiscordType.TEXT_CHANNEL, channel

    elif (channel := guild.get_channel(value)) and isinstance(channel, VoiceChannel):
        return DiscordType.VOICE_CHANNEL, channel

    elif (channel := guild.get_channel(value)) and isinstance(channel, CategoryChannel):
        return DiscordType.CATEGORY_CHANNEL, channel

    elif (channel := guild.get_channel(value)) and isinstance(channel, ForumChannel):
        return DiscordType.FORUM_CHANNEL, channel

    elif (channel := guild.get_channel(value)) and isinstance(channel, Thread):
        return DiscordType.THREAD, channel
    else:
        return DiscordType.UNKNOWN, None

async def utils_len(ctx: Message, value):
    """
    Retourne la longueur d'une liste ou d'une chaîne de caractères.
    
    Fonction utilitaire équivalente à len() de Python mais compatible avec
    les objets Dshell (ListNode) et les chaînes de caractères.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La liste (ListNode) ou chaîne dont calculer la longueur
    :type value: Union[str, ListNode]
    :return: Le nombre d'éléments ou de caractères
    :rtype: int
    :raises TypeError: Si value n'est ni une chaîne ni une ListNode
    
    Example:
        >>> await utils_len(ctx, "Bonjour")
        7
        >>> await utils_len(ctx, ListNode([1, 2, 3]))
        3
    """
    if not isinstance(value, (str, ListNode)):
        raise TypeError(f"value must be a list or a string in len command, not {type(value)}")

    return len(value)

async def utils_random(ctx: Message, value: Optional["ListNode"] = None):
    """
    Retourne un élément aléatoire d'une liste ou un nombre aléatoire.
    
    Si une liste est fournie, retourne un élément aléatoire de cette liste.
    Si aucune valeur n'est fournie, retourne un nombre aléatoire entre 0 et 1.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: Liste optionnelle dont extraire un élément aléatoire
    :type value: Optional[ListNode]
    :return: Un élément aléatoire de la liste ou un nombre aléatoire
    :raises TypeError: Si value n'est pas None ou ListNode
    
    Example:
        >>> await utils_random(ctx, ListNode([1, 2, 3, 4, 5]))
        3  # Un élément aléatoire
        >>> await utils_random(ctx)
        0.742  # Nombre aléatoire entre 0 et 1
    """
    _CMD = "random"
    _validate_optional_list_node(value, "value", _CMD)

    if value is None:
        return random()
    return choice(value)

async def utils_get_name(ctx : Message, value: int) -> Union[str, None]:
    """
    Récupère le nom d'un rôle, membre ou canal à partir de son ID.
    
    Recherche dans le serveur Discord l'élément correspondant à l'ID fourni
    et retourne son nom. Vérifie dans l'ordre: rôles, membres, puis canaux.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: L'ID Discord de l'élément
    :type value: int
    :return: Le nom de l'élément, ou None si non trouvé
    :rtype: Union[str, None]
    :raises TypeError: Si value n'est pas un entier
    
    Example:
        >>> await utils_get_name(ctx, 123456789)
        "Modérateur"  # Si c'est un rôle
    """
    _CMD = "name"
    _validate_required_int(value, "value", _CMD)

    guild = ctx.guild
    result = None

    if role := guild.get_role(value):
        result = role.name

    elif member := guild.get_member(value):
        result = member.name

    if channel := guild.get_channel(value) :
        result = channel.name

    return result

async def utils_get_id(ctx : Message, value: str) -> Union[int, None]:
    """
    Récupère l'ID d'un rôle, membre ou canal à partir de son nom.
    
    Recherche dans le serveur Discord l'élément correspondant au nom fourni
    et retourne son ID. Vérifie dans l'ordre: rôles, membres, puis canaux.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: Le nom de l'élément à rechercher
    :type value: str
    :return: L'ID Discord de l'élément, ou None si non trouvé
    :rtype: Union[int, None]
    :raises TypeError: Si value n'est pas une chaîne
    
    Example:
        >>> await utils_get_id(ctx, "Modérateur")
        123456789  # L'ID du rôle "Modérateur"
    """
    _CMD = "id"
    _validate_required_string(value, "value", _CMD)

    guild = ctx.guild
    result = None

    if role := get(guild.roles, name=value):
        result = role.id

    elif member := get(guild.members, name=value):
        result = member.id

    if channel := get(guild.channels, name=value) :
        result = channel.id

    return result

async def utils_get_roles(ctx: Message, value: int):
    """
    Récupère la liste des rôles d'un membre.
    
    Retourne tous les rôles attribués à un membre du serveur Discord,
    sous forme de ListNode contenant les IDs des rôles.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: L'ID du membre dont récupérer les rôles
    :type value: int
    :return: Liste (ListNode) des IDs de rôles du membre
    :rtype: ListNode
    :raises ValueError: Si le membre n'est pas trouvé
    :raises TypeError: Si value n'est pas un ID de membre valide
    
    Example:
        >>> await utils_get_roles(ctx, 123456789)
        ListNode([111, 222, 333])  # IDs des rôles du membre
    """
    _CMD = "roles"
    _validate_required_int(value, "value", _CMD)

    guild = ctx.guild

    what_is, member = utils_what_discord_type_is(ctx, value)

    if what_is == DiscordType.UNKNOWN:
        raise ValueError(f"{value} member not found in guild {guild.name}")

    if what_is != DiscordType.MEMBER:
        raise TypeError(f"value must be a member id in roles command, not {what_is}")

    return ListNode([i.id for i in member.roles])


def utils_build_colour(color: Union[int, "ListNode"]) -> Union[Colour, int]:
    """
    Builds a Colour object from an integer or a ListNode.
    :param color: The color to build.
    :return: A Colour object.
    """
    if isinstance(color, int):
        return color
    elif isinstance(color, (ListNode, list)):
        r, g, b = color[0], color[1], color[2]

        if not len(color) == 3:
            raise ValueError(f"Color must be a list of 3 integers, not {len(color)} elements !")
        elif not (isinstance(r, int) and isinstance(g, int) and isinstance(b, int)):
            raise TypeError(f"Color must be an integer or a ListNode of integers !")
        elif not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise Exception(f"Color ListNode integer must be between 0 <= x <= 255")
        else:
            return Colour.from_rgb(*color)
    else:
        raise TypeError(f"Color must be an integer or a ListNode, not {type(color)} !")

def utils_refactor_emoji(emoji: Union[str, None]) -> Union[str, None]:
    """
    Refactorise une chaine de caractère contenant un emoji pour enlever tous les espaces.
    :param emoji: La chaine de caractère à refactoriser.
    :return: La chaine de caractère refactorisée, ou None si l'emoji est None.
    """
    return emoji.replace(" ", "") if emoji else None