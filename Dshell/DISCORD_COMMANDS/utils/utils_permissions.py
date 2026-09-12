from Dshell.full_import import (Member,
                            Role,
                            PermissionOverwrite,
                            Permissions,
                            Message)

from Dshell.full_import import Union, TYPE_CHECKING, Optional

from ...DshellParser.ast_nodes import ListNode, PermissionNode, IntNode, ASTNode, AllowedPermissionNode, DeniedPermissionNode, ConstructPermissionNode

from ...DshellInterpreteur.dshell_scope import new_scope
from ...DshellInterpreteur.utils_interpreter import eval_expression

from .utils_global import utils_what_discord_type_is, DiscordType

from .utils_type_validation import (_validate_required_permission,
                                    _validate_required_list_node,
                                    _validate_required_int)

if TYPE_CHECKING:
    from ...DshellInterpreteur.dshell_interpreter import DshellInterpreteur

async def utils_get_member_or_role(ctx: Message, target: Optional[IntNode]) -> Optional[Union[Member, Role]]:
    """
    Récupère un membre ou un rôle à partir d'un identifiant ou d'un objet Discord.

    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param target: L'identifiant ou l'objet Discord du membre ou du rôle
    :type target: Union[Member, Role, int]
    :return: L'objet Discord correspondant au membre ou au rôle
    :rtype: Union[Member, Role]
    :raises ValueError: Si le type de cible n'est pas valide ou si le membre/role n'est pas trouvé

    Example:
        >>> member = await utils_get_member_or_role(ctx, 123456789012345678)
        <Member id=123456789012345678 name='User'>

        >>> role = await utils_get_member_or_role(ctx, 987654321098765432)
        <Role id=987654321098765432 name='Admin'>
    """

    if target is None:
        return None

    _validate_required_int(target, "target", "get_member_or_role")

    discord_type = utils_what_discord_type_is(ctx, target)

    if discord_type[0] not in (DiscordType.MEMBER, DiscordType.ROLE):
        raise ValueError(f"The type of target provided ({discord_type[0]}) is neither a member nor a role.")

    if discord_type[1] is None:
        raise ValueError(f"The {discord_type[0]} with ID {target} was not found in the server.")

    return discord_type[1]


async def utils_create_allowed_denied_permissions(ctx: Message,
                                                  targets: Union[ListNode, IntNode],
                                                  permissions: Optional[Union[ListNode, IntNode]],
                                                  allowed: bool = True) -> PermissionNode:
    """
    Crée une PermissionNode à partir des cibles et des permissions fournies.
    Les targets peuvent-être une ListNode s'il y a plusieurs cibles ou un IntNode si il n'y a qu'une seule cible.
    Les targets peuvent-être des membres ou des rôles mélangers.

    Les permissions peuvent-être une ListNode s'il y a plusieurs permissions ou un IntNode si il n'y a qu'une seule permission.
    S'il n'y a pas de permissions, la valeur par défaut est 0 (aucune permission).
    Si les permissions fournies sont un IntNode, la permission s'appliquera à toutes les cibles.
    Si les permissions fournies sont une ListNode, chaque permission s'appliquera à la cible correspondante dans l'ordre.
    Si le nombre de permissions est inférieur au nombre de cibles, les cibles restantes auront la valeur par défaut (0).

    :param ctx:
    :param targets:
    :param permissions:
    :param allowed: Si True, les permissions seront autorisées, sinon elles seront refusées.
    :return:
    """
    _CMD = "create_allowed_denied_permissions"

    if isinstance(targets, IntNode):
        targets = ListNode([targets])

    _validate_required_list_node(targets, "targets", _CMD)

    if isinstance(permissions, IntNode):
        permissions = ListNode([permissions])

    if permissions is None:
        permissions = ListNode([IntNode(0)])

    _validate_required_list_node(permissions, "permissions", _CMD)

    permissions_dict: dict[Union[Member, Role, None], PermissionOverwrite] = {}

    for i, target in enumerate(targets):
        member_or_role = await utils_get_member_or_role(ctx, target)

        if i < len(permissions):
            permission_value = permissions[i]
        else:
            if len(permissions) > 0:
                permission_value = permissions[len(permissions)-1]
            else:
                permission_value = IntNode(0)  # Valeur par défaut si aucune permission n'est fournie

        make_permission = (Permissions(permission_value), Permissions(0)) if allowed else (Permissions(0), Permissions(permission_value))

        permission_overwrite = PermissionOverwrite.from_pair(*make_permission)
        permissions_dict[member_or_role] = permission_overwrite

    return PermissionNode(permissions_dict)




async def utils_update_permissions(ctx: Message,
                                   permission1: PermissionNode,
                                   permission2: PermissionNode) -> PermissionNode:
    """
    Fusionne deux dictionnaires de permissions Discord.
    
    Cette fonction met à jour le premier dictionnaire de permissions avec les valeurs
    du second, permettant de combiner facilement plusieurs ensembles de permissions.
    
    :param ctx: Le contexte du message Discord
    :type ctx: Message
    :param permission1: Le dictionnaire de permissions de base
    :type permission1: dict[Union[Member, Role, None], PermissionOverwrite]
    :param permission2: Le dictionnaire de permissions à ajouter
    :type permission2: dict[Union[Member, Role, None], PermissionOverwrite]
    :return: Le dictionnaire de permissions fusionné
    :rtype: dict
    :raises TypeError: Si les paramètres ne sont pas des dictionnaires
    
    Example:
        >>> perms1 = {member1: PermissionOverwrite(send_messages=True)}
        >>> perms2 = {member2: PermissionOverwrite(read_messages=True)}
        >>> await utils_update_permissions(ctx, perms1, perms2)
        {member1: ..., member2: ...}
    """
    _CMD = "update_perms"
    _validate_required_permission(permission1, "permission1", _CMD)

    _validate_required_permission(permission2, "permission2", _CMD)

    permission1.update(permission2)

    return permission1


async def build_permission(body: list[ASTNode], interpreter: "DshellInterpreteur") -> PermissionNode:
    """
    Builds a dictionary of PermissionOverwrite objects from the command information.
    """
    _CMD = "permission"

    permissions_result = PermissionNode({})

    await interpreter.execute(body)

    permissions: ListNode[Union[AllowedPermissionNode, DeniedPermissionNode]] = interpreter.env.get("__permissions__", None)

    if permissions is None:
        raise ValueError(f"Missing permissions in [PERMISSION] node.")

    for permission in permissions:
        if not isinstance(permission, (AllowedPermissionNode, DeniedPermissionNode)):
            raise TypeError(f"Invalid permission type in [PERMISSION] node: {type(permission)}. Expected PermissionNode.")

        if isinstance(permission, AllowedPermissionNode):
            permissions_result.update(
                await utils_create_allowed_denied_permissions(
                    interpreter.ctx,
                    await interpreter.eval_data_token(permission.targets),
                    await interpreter.eval_data_token(permission.permissions),
                    allowed=True
                )
            )
        else:
            permissions_result.update(
                await utils_create_allowed_denied_permissions(
                    interpreter.ctx,
                    await interpreter.eval_data_token(permission.targets),
                    await interpreter.eval_data_token(permission.permissions),
                    allowed=False
                )
            )

    interpreter.env.set("__permissions__", ListNode([]))

    return permissions_result