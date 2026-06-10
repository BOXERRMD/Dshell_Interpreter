__all__ = [
    "utils_help",
    "utils_get_size",
    "utils_make_mention",
    "utils_len",
    "utils_random",
    "utils_get_name",
    "utils_get_id",
    "utils_get_roles",
    "utils_what_discord_type_is",
    "utils_build_colour",
    "DiscordType"
]

from Dshell.full_import import *

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
                           get,
                           getsizeof)

from Dshell.full_import import (random,
                            choice)

from ...DshellParser.ast_nodes import ListNode, StrNode, IntNode, FloatNode

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

async def utils_help(ctx: Message, command: StrNode) -> StrNode:
    """
    Renvoie l'aide associé à une commande
    :param ctx:
    :param command:
    :return:
    """
    _CMD = "help"

    _validate_required_string(command, "command", _CMD)

    from inspect import signature, Parameter
    from ...DshellTokenizer.dshell_keywords import dshell_commands

    if command not in dshell_commands:
        raise ValueError(f"[HELP] command not found : '{command}'")

    sig = signature(dshell_commands[command])
    result = StrNode("## HELP `{command}`")

    for nom, param in sig.parameters.items():
        if nom == "ctx":
            continue

        result += StrNode(f"""
  --{nom} [{param.default if param.default != Parameter.empty else "REQUIRED"}] -> {param.annotation}
""")
    return result

async def utils_get_size(ctx: Message, target: Any):
    """
    Récupère la taille de l'objet
    :param ctx:
    :param target:
    :return:
    """

    return IntNode(getsizeof(target))

def utils_what_discord_type_is(ctx: Union[Message, Guild], value: IntNode) -> tuple[StrNode, Union[Member, Role, TextChannel, VoiceChannel, CategoryChannel, ForumChannel, Thread, None]]:
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

    _validate_required_int(value, "value", "what_discord_type_is")

    if member := guild.get_member(value):
        return StrNode(DiscordType.MEMBER), member

    if role := guild.get_role(value):
        return StrNode(DiscordType.ROLE), role

    channel = guild.get_channel(value)

    if channel is not None:

         if isinstance(channel, TextChannel):
            return StrNode(DiscordType.TEXT_CHANNEL), channel

         elif isinstance(channel, VoiceChannel):
            return StrNode(DiscordType.VOICE_CHANNEL), channel

         elif isinstance(channel, CategoryChannel):
            return StrNode(DiscordType.CATEGORY_CHANNEL), channel

         elif isinstance(channel, ForumChannel):
            return StrNode(DiscordType.FORUM_CHANNEL), channel

         elif isinstance(channel, Thread):
            return StrNode(DiscordType.THREAD), channel

    return StrNode(DiscordType.UNKNOWN), None

async def utils_make_mention(ctx: Message, value: IntNode) -> StrNode:
    """
    Crée une mention Discord à partir d'un ID.

    Génère une chaîne de caractères de mention pour un membre, un rôle ou un canal
    en fonction de l'ID fourni. Vérifie dans l'ordre: membres, rôles, puis canaux.

    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: L'ID Discord de l'élément à mentionner
    :type value: int
    :return: La chaîne de mention Discord correspondante, ou une chaîne vide si non trouvé
    :rtype: str

    Example:
        >>> await utils_make_mention(ctx, 123456789)
        "<@123456789>"  # Si c'est un membre
        "<@&123456789>"  # Si c'est un rôle
        "<#123456789>"  # Si c'est un canal
    """
    _validate_required_int(value, "value", "make_mention")

    if (target := utils_what_discord_type_is(ctx, value)) != DiscordType.UNKNOWN:
        return StrNode(target[1].mention)
    else:
        return StrNode("")

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
    if not isinstance(value, (StrNode, ListNode)):
        raise TypeError(f"value must be a list or a string in len command, not {type(value)}")

    return IntNode(len(value))

async def utils_random(ctx: Message, value: Optional[ListNode] = None):
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
        return FloatNode(random())
    return choice(value)

async def utils_get_name(ctx : Message, value: int) -> Union[StrNode, None]:
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

    return StrNode(result)

async def utils_get_id(ctx : Message, value: StrNode) -> Union[IntNode, None]:
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
        result = IntNode(role.id)

    elif member := get(guild.members, name=value):
        result = IntNode(member.id)

    if channel := get(guild.channels, name=value):
        result = IntNode(channel.id)

    return result

async def utils_get_roles(ctx: Message, value: IntNode) -> ListNode:
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

    return ListNode([IntNode(i.id) for i in member.roles])


def utils_build_colour(color: Union[IntNode, ListNode]) -> Union[Colour, IntNode]:
    """
    Builds a Colour object from an integer or a ListNode.
    :param color: The color to build.
    :return: A Colour object.
    """
    if isinstance(color, IntNode):
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

def utils_refactor_emoji(emoji: Union[StrNode, None]) -> Union[StrNode, None]:
    """
    Refactorise une chaine de caractère contenant un emoji pour enlever tous les espaces.
    :param emoji: La chaine de caractère à refactoriser.
    :return: La chaine de caractère refactorisée, ou None si l'emoji est None.
    """
    return StrNode(emoji).replace(" ", "") if emoji else None