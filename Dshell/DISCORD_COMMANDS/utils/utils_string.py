__all__ = [
    "utils_split_string",
    "utils_upper_string",
    "utils_lower_string",
    "utils_title_string",
    "utils_strip_string",
    "utils_replace_string",
    "utils_regex_findall",
    "utils_regex_sub",
    "utils_regex_search",
    "utils_regex_group"
]

from Dshell.full_import import Message
from ..._DshellParser.ast_nodes import ListNode
from Dshell.full_import import (search,
                            sub,
                            findall)


def _validate_string_type(value, param_name: str, command_name: str):
    """
    Validate that a value is a string type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages
    :raises TypeError: If the value is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"{param_name} must be a str in {command_name} command, not {type(value)}")


async def utils_split_string(ctx: Message, value: str, separator: str = ' ') -> ListNode:
    """
    Divise une chaîne de caractères en une liste de sous-chaînes.
    
    Sépare la chaîne en utilisant le séparateur spécifié (espace par défaut).
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La chaîne à diviser
    :type value: str
    :param separator: Le séparateur à utiliser (par défaut: espace)
    :type separator: str
    :return: Liste des sous-chaînes résultantes
    :rtype: ListNode
    :raises TypeError: Si value ou separator ne sont pas des chaînes
    
    Example:
        >>> await utils_split_string(ctx, "a,b,c", ",")
        ListNode(["a", "b", "c"])
    """
    _validate_string_type(value, 'value', 'split')
    _validate_string_type(separator, 'separator', 'split')
    return ListNode(value.split(separator))


async def utils_upper_string(ctx: Message, value: str) -> str:
    """
    Convertit une chaîne en majuscules.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La chaîne à convertir
    :type value: str
    :return: La chaîne en majuscules
    :rtype: str
    :raises TypeError: Si value n'est pas une chaîne
    
    Example:
        >>> await utils_upper_string(ctx, "bonjour")
        "BONJOUR"
    """
    _validate_string_type(value, 'value', 'upper')
    return value.upper()


async def utils_lower_string(ctx: Message, value: str) -> str:
    """
    Convertit une chaîne en minuscules.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La chaîne à convertir
    :type value: str
    :return: La chaîne en minuscules
    :rtype: str
    :raises TypeError: Si value n'est pas une chaîne
    
    Example:
        >>> await utils_lower_string(ctx, "BONJOUR")
        "bonjour"
    """
    _validate_string_type(value, 'value', 'lower')
    return value.lower()


async def utils_title_string(ctx: Message, value: str) -> str:
    """
    Convertit une chaîne en format titre (première lettre de chaque mot en majuscule).
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La chaîne à convertir
    :type value: str
    :return: La chaîne au format titre
    :rtype: str
    :raises TypeError: Si value n'est pas une chaîne
    
    Example:
        >>> await utils_title_string(ctx, "bonjour le monde")
        "Bonjour Le Monde"
    """
    _validate_string_type(value, 'value', 'title')
    return value.title()


async def utils_strip_string(ctx: Message, value: str) -> str:
    """
    Supprime les espaces au début et à la fin d'une chaîne.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La chaîne à nettoyer
    :type value: str
    :return: La chaîne sans espaces aux extrémités
    :rtype: str
    :raises TypeError: Si value n'est pas une chaîne
    
    Example:
        >>> await utils_strip_string(ctx, "  bonjour  ")
        "bonjour"
    """
    _validate_string_type(value, 'value', 'strip')
    return value.strip()


async def utils_replace_string(ctx: Message, value: str, old: str, new: str) -> str:
    """
    Remplace toutes les occurrences d'une sous-chaîne par une autre.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param value: La chaîne dans laquelle effectuer le remplacement
    :type value: str
    :param old: La sous-chaîne à remplacer
    :type old: str
    :param new: La chaîne de remplacement
    :type new: str
    :return: La chaîne avec les remplacements effectués
    :rtype: str
    :raises TypeError: Si les paramètres ne sont pas des chaînes
    
    Example:
        >>> await utils_replace_string(ctx, "Hello World", "World", "Discord")
        "Hello Discord"
    """
    _validate_string_type(value, 'value', 'replace')
    _validate_string_type(old, 'old', 'replace')
    _validate_string_type(new, 'new', 'replace')
    return value.replace(old, new)


async def utils_regex_findall(ctx: Message, regex: str, content: str = None) -> ListNode:
    """
    Trouve toutes les occurrences d'une expression régulière dans une chaîne.
    
    Recherche toutes les correspondances du pattern regex dans le contenu.
    Si content n'est pas fourni, utilise le contenu du message Discord.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param regex: Le pattern d'expression régulière
    :type regex: str
    :param content: Le texte dans lequel chercher (par défaut: contenu du message)
    :type content: str | None
    :return: Liste de listes contenant les groupes capturés pour chaque correspondance
    :rtype: ListNode
    :raises TypeError: Si regex ou content ne sont pas des chaînes
    
    Example:
        >>> await utils_regex_findall(ctx, r"\\d+", "J'ai 3 pommes et 5 bananes")
        ListNode([["3"], ["5"]])
    """
    _validate_string_type(regex, 'regex', 'regex_findall')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_findall')

    result = findall(regex, content if content is not None else ctx.content)
    return ListNode([ListNode(list(i)) for i in result])


async def utils_regex_sub(ctx: Message, regex: str, replace: str, content: str = None) -> str:
    """
    Remplace toutes les occurrences d'une expression régulière par une chaîne.
    
    Utilise une expression régulière pour trouver et remplacer des patterns
    dans le contenu. Si content n'est pas fourni, utilise le contenu du message.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param regex: Le pattern d'expression régulière
    :type regex: str
    :param replace: La chaîne de remplacement
    :type replace: str
    :param content: Le texte dans lequel chercher (par défaut: contenu du message)
    :type content: str | None
    :return: La chaîne avec les remplacements effectués
    :rtype: str
    :raises TypeError: Si les paramètres ne sont pas des chaînes
    
    Example:
        >>> await utils_regex_sub(ctx, r"\\d+", "X", "J'ai 3 pommes")
        "J'ai X pommes"
    """
    _validate_string_type(regex, 'regex', 'regex_sub')
    _validate_string_type(replace, 'replacement', 'regex_sub')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_sub')

    return sub(regex, replace, content if content is not None else ctx.content)


async def utils_regex_search(ctx: Message, regex: str, content: str = None) -> str:
    """
    Recherche la première occurrence d'une expression régulière.
    
    Retourne la première correspondance trouvée, ou une chaîne vide si aucune.
    Si content n'est pas fourni, utilise le contenu du message Discord.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param regex: Le pattern d'expression régulière
    :type regex: str
    :param content: Le texte dans lequel chercher (par défaut: contenu du message)
    :type content: str | None
    :return: La chaîne correspondante, ou chaîne vide si aucune correspondance
    :rtype: str
    :raises TypeError: Si regex ou content ne sont pas des chaînes
    
    Example:
        >>> await utils_regex_search(ctx, r"\\d+", "Prix: 42 euros")
        "42"
    """
    _validate_string_type(regex, 'regex', 'regex_search')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_search')

    result = search(regex, content if content is not None else ctx.content)
    return result.group() if result else ''


async def utils_regex_group(ctx: Message, regex: str, content: str = None) -> ListNode:
    """
    Recherche une expression régulière et retourne les groupes capturés.
    
    Retourne tous les groupes capturés par les parenthèses dans le pattern regex.
    Si content n'est pas fourni, utilise le contenu du message Discord.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param regex: Le pattern d'expression régulière (avec groupes de capture)
    :type regex: str
    :param content: Le texte dans lequel chercher (par défaut: contenu du message)
    :type content: str | None
    :return: Liste des groupes capturés, ou liste vide si aucune correspondance
    :rtype: ListNode
    :raises TypeError: Si regex ou content ne sont pas des chaînes
    
    Example:
        >>> await utils_regex_group(ctx, r"(\d+)-(\d+)", "Code: 123-456")
        ListNode(["123", "456"])
    """
    _validate_string_type(regex, 'regex', 'regex_group')
    if content is not None:
        _validate_string_type(content, 'content', 'regex_group')

    result = search(regex, content if content is not None else ctx.content)
    return ListNode(list(result.groups())) if result else ListNode([])