from Dshell.full_import import (Message, MISSING, PermissionOverwrite, _MissingSentinel, Union, Optional)

from ..DshellParser.ast_nodes import ListNode, StrNode, PermissionNode
from .utils.utils_global import utils_build_colour
from .utils.utils_type_validation import (_validate_optional_string,
                                          _validate_optional_int,
                                          _validate_optional_bool,
                                          _validate_optional_permission,
                                          _validate_required_int,
                                          _validate_missing_or_type)

__all__ = [
    'dshell_create_role',
    'dshell_delete_roles',
    'dshell_edit_role'

]

async def dshell_create_role(ctx: Message,
                             name: StrNode = MISSING,
                             permissions: PermissionOverwrite = MISSING,
                             color: Union[ListNode, int] = MISSING,
                             hoist: bool = MISSING,
                             mentionable: bool = MISSING,
                             reason: Optional[StrNode] = None):
    """
    Crée un nouveau rôle sur le serveur Discord.
    
    Cette fonction permet de créer un rôle avec des paramètres personnalisés
    incluant le nom, les permissions, la couleur, et d'autres propriétés.
    Tous les paramètres sont optionnels sauf le contexte.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param name: Le nom du rôle (optionnel)
    :type name: str | MISSING
    :param permissions: Dictionnaire de permissions du rôle (optionnel)
    :type permissions: dict[None, PermissionOverwrite] | MISSING
    :param color: Couleur du rôle (entier RGB ou ListNode[r,g,b]) (optionnel)
    :type color: Union[ListNode, int] | MISSING
    :param hoist: Si True, affiche les membres de ce rôle séparément dans la liste (optionnel)
    :type hoist: bool | MISSING
    :param mentionable: Si True, permet de mentionner le rôle (optionnel)
    :type mentionable: bool | MISSING
    :param reason: Raison de la création (apparaît dans les logs Discord) (optionnel)
    :type reason: str | None
    :return: L'ID du rôle créé
    :rtype: int
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> # Créer un rôle simple
        >>> await dshell_create_role(ctx, name="Modérateur")
        123456789
        >>> # Créer un rôle avec couleur RGB
        >>> await dshell_create_role(ctx, name="VIP", color=ListNode([255, 0, 0]), hoist=True)
        987654321
    """
    _CMD = "cr"

    _validate_missing_or_type(name, "Name", StrNode, _CMD)

    _validate_optional_permission(permissions, "Permissions", _CMD)

    _validate_missing_or_type(color, "Color", ListNode, int, _CMD)
    if not isinstance(color, _MissingSentinel):
        color = utils_build_colour(color)

    _validate_missing_or_type(hoist, "Hoist", bool, _CMD)

    _validate_missing_or_type(mentionable, "Mentionable", bool, _CMD)
    
    _validate_optional_string(reason, "Reason", _CMD)

    if isinstance(permissions, PermissionNode):
        if None in permissions:
            allow, deny = permissions.none().value.pair()
            permissions = allow

    created_role = await ctx.guild.create_role(name=name,
                                               permissions=permissions,
                                               colour=color,
                                               hoist=hoist,
                                               mentionable=mentionable,
                                               reason=str(reason))

    return created_role.id


async def dshell_delete_roles(ctx: Message, roles: Union[ListNode, int], reason: Optional[StrNode]=None):
    """
    Supprime un ou plusieurs rôles du serveur Discord.
    
    Cette fonction permet de supprimer des rôles en fournissant soit un ID unique,
    soit une liste (ListNode) d'IDs de rôles. Tous les rôles spécifiés seront
    supprimés du serveur.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param roles: L'ID d'un rôle unique ou une ListNode d'IDs de rôles
    :type roles: Union[ListNode, int]
    :param reason: Raison de la suppression (apparaît dans les logs Discord) (optionnel)
    :type reason: str | None
    :return: L'ID du dernier rôle supprimé
    :rtype: int
    :raises Exception: Si un rôle n'est pas trouvé dans le serveur
    :raises Exception: Si le type de roles est invalide
    
    Example:
        >>> # Supprimer un rôle unique
        >>> await dshell_delete_roles(ctx, 123456789, reason="Rôle obsolète")
        123456789
        >>> # Supprimer plusieurs rôles
        >>> await dshell_delete_roles(ctx, ListNode([111, 222, 333]))
        333
    """
    _CMD = "dr"

    if roles is not None and not isinstance(roles, (int, ListNode)):
        raise Exception(f"Roles must be a int, role mention or NodeList of both, not {type(roles)} !")

    _validate_optional_string(reason, "Reason", _CMD)

    roles: Union[int, ListNode]
    if not isinstance(roles, (int, ListNode)):
        raise Exception(f"Role must be a int, role mention or NodeList of both, not {type(roles)} !")

    if isinstance(roles, int):
        roles: tuple = (roles, )

    for i in roles:
        role_to_delete = ctx.guild.get_role(i)

        if role_to_delete is None:
            raise Exception(f'Role {i} not found in the server !')

        await role_to_delete.delete(reason=StrNode(reason))

    return role_to_delete.id


async def dshell_edit_role(ctx: Message,
                           role: int,
                           name: Optional[StrNode]=None,
                           permissions: Optional[dict[None, PermissionOverwrite]]=None,
                           color: Union[ListNode, int]=None,
                           hoist: Optional[bool]=None,
                           mentionable: Optional[bool]=None,
                           position: Optional[int]=None,
                           reason: Optional[StrNode]=None,):
    """
    Modifie les propriétés d'un rôle existant sur le serveur Discord.
    
    Cette fonction permet de modifier un ou plusieurs attributs d'un rôle.
    Seuls les paramètres fournis (non None) seront modifiés, les autres
    conserveront leurs valeurs actuelles.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param role: L'ID du rôle à modifier
    :type role: int
    :param name: Nouveau nom du rôle (optionnel)
    :type name: str | None
    :param permissions: Nouvelles permissions du rôle (optionnel)
    :type permissions: dict[None, PermissionOverwrite] | None
    :param color: Nouvelle couleur du rôle (entier RGB ou ListNode[r,g,b]) (optionnel)
    :type color: Union[ListNode, int] | None
    :param hoist: Afficher les membres séparément (optionnel)
    :type hoist: bool | None
    :param mentionable: Autoriser les mentions (optionnel)
    :type mentionable: bool | None
    :param position: Nouvelle position dans la hiérarchie des rôles (optionnel)
    :type position: int | None
    :param reason: Raison de la modification (apparaît dans les logs Discord) (optionnel)
    :type reason: str | None
    :return: L'ID du rôle modifié
    :rtype: int
    :raises TypeError: Si les types des paramètres sont incorrects
    
    Example:
        >>> # Renommer un rôle
        >>> await dshell_edit_role(ctx, 123456789, name="Super Modérateur")
        123456789
        >>> # Changer la couleur en rouge
        >>> await dshell_edit_role(ctx, 123456789, color=ListNode([255, 0, 0]))
        123456789
    """
    _CMD = "er"

    _validate_required_int(role, "Role", _CMD)
    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_permission(permissions, "Permissions", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    
    role_to_edit = ctx.guild.get_role(role)

    if isinstance(permissions, PermissionNode):
        if None in permissions:
            allow, deny = permissions.none().value.pair()
            permissions = allow

    if color is not None:
        color = utils_build_colour(color)

    _validate_optional_bool(hoist, "Hoist", _CMD)

    _validate_optional_bool(mentionable, "Mentionable", _CMD)

    _validate_optional_int(position, "Position", _CMD)

    await role_to_edit.edit(name=name if name is not None else role_to_edit.name,
                            permissions=permissions if permissions is not None else role_to_edit.permissions,
                            colour=color if color is not None else role_to_edit.colour,
                            hoist=hoist if hoist is not None else role_to_edit.hoist,
                            mentionable=mentionable if mentionable is not None else role_to_edit.mentionable,
                            position=position if position is not None else role_to_edit.position,
                            reason=str(reason))

    return role_to_edit.id
