from Dshell.full_import import (Message, MISSING, PermissionOverwrite, _MissingSentinel, Union)

from .._DshellParser.ast_nodes import ListNode
from .utils.utils_global import utils_build_colour
from .utils.utils_type_validation import (_validate_optional_string,
                                          _validate_optional_int,
                                          _validate_optional_bool,
                                          _validate_optional_dict,
                                          _validate_required_int,
                                          _validate_missing_or_type)

__all__ = [
    'dshell_create_role',
    'dshell_delete_roles',
    'dshell_edit_role'

]

async def dshell_create_role(ctx: Message,
                             name: str = MISSING,
                             permissions: dict[None, PermissionOverwrite] = MISSING,
                             color: Union[ListNode, int] = MISSING,
                             hoist: bool = MISSING,
                             mentionable: bool = MISSING,
                             reason: str = None):
    """
    Creates a role on the server.
    """
    _CMD = "cr"

    _validate_missing_or_type(name, "Name", str, _CMD)

    _validate_missing_or_type(permissions, "Permissions", dict, _CMD)

    _validate_missing_or_type(color, "Color", ListNode, int, _CMD)
    if not isinstance(color, _MissingSentinel):
        color = utils_build_colour(color)

    _validate_missing_or_type(hoist, "Hoist", bool, _CMD)

    _validate_missing_or_type(mentionable, "Mentionable", bool, _CMD)
    
    _validate_optional_string(reason, "Reason", _CMD)

    if isinstance(permissions, dict):
        if None in permissions:
            allow, deny = permissions[None].pair()
            permissions = allow

    created_role = await ctx.guild.create_role(name=name,
                                               permissions=permissions,
                                               colour=color,
                                               hoist=hoist,
                                               mentionable=mentionable,
                                               reason=str(reason))

    return created_role.id


async def dshell_delete_roles(ctx: Message, roles: Union["ListNode", int], reason: str=None):
    """
    Delete the role on the server
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

        await role_to_delete.delete(reason=str(reason))

    return role_to_delete.id


async def dshell_edit_role(ctx: Message,
                           role: int,
                           name: str=None,
                           permissions: dict[None, PermissionOverwrite]=None,
                           color: Union["ListNode", int]=None,
                           hoist: bool=None,
                           mentionable: bool=None,
                           position: int=None,
                           reason: str=None,):
    """
    Edit the current role
    """
    _CMD = "er"

    _validate_required_int(role, "Role", _CMD)
    _validate_optional_string(name, "Name", _CMD)
    _validate_optional_dict(permissions, "Permissions", _CMD)
    _validate_optional_string(reason, "Reason", _CMD)
    
    role_to_edit = ctx.guild.get_role(role)

    if isinstance(permissions, dict):
        if None in permissions:
            allow, deny = permissions[None].pair()
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
