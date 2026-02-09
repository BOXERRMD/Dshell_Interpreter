"""
Type validation utility functions for Discord commands.
These functions provide reusable type checking for optional parameters.
"""

__all__ = [
    "_validate_optional_string",
    "_validate_optional_int",
    "_validate_optional_bool",
    "_validate_optional_number",
    "_validate_optional_dict",
    "_validate_optional_embed",
    "_validate_optional_view",
    "_validate_optional_code_node",
    "_validate_optional_list_node",
    "_validate_required_bool",
    "_validate_required_list_node",
    "_validate_required_int",
    "_validate_required_string",
    "_validate_required_dict",
    "_validate_missing_or_type",
    "_validate_missing_or_bool",
    "_validate_missing_or_int",
    "_validate_missing_or_string",
    "_validate_missing_or_dict",
]


def _validate_optional_string(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is a string type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a string
    """
    if value is not None and not isinstance(value, str):
        if command_name:
            raise Exception(f"{param_name} must be a string, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be a string, not {type(value)} !")


def _validate_optional_int(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is an integer type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not an integer
    """
    if value is not None and not isinstance(value, int):
        if command_name:
            raise Exception(f"{param_name} must be an integer, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be an integer, not {type(value)} !")


def _validate_optional_bool(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is a boolean type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a boolean
    """
    if value is not None and not isinstance(value, bool):
        if command_name:
            raise Exception(f"{param_name} must be a boolean, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be a boolean, not {type(value)} !")


def _validate_optional_number(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is a number (int or float) type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a number
    """
    if value is not None and not isinstance(value, (int, float)):
        if command_name:
            raise Exception(f"{param_name} parameter must be a number (seconds) or None, not {type(value)} !")
        else:
            raise Exception(f"{param_name} parameter must be a number (seconds) or None, not {type(value)} !")


def _validate_optional_dict(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is a dict type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a dict
    """
    if value is not None and not isinstance(value, dict):
        if command_name:
            raise Exception(f"{param_name} must be a PermissionNode, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be a PermissionNode, not {type(value)} !")


def _validate_optional_embed(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is an Embed or ListNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not an Embed or ListNode
    """
    from Dshell.full_import import Embed
    from ..._DshellParser.ast_nodes import ListNode
    
    if value is not None and not isinstance(value, (ListNode, Embed)):
        if command_name:
            raise Exception(f"{param_name} must be a list of Embed objects or a single Embed object, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be a list of Embed objects or a single Embed object, not {type(value)} !")


def _validate_optional_view(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is an EasyModifiedViews type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not an EasyModifiedViews
    """
    from Dshell.full_import import EasyModifiedViews
    
    if value is not None and not isinstance(value, EasyModifiedViews):
        if command_name:
            raise Exception(f"{param_name} must be an UI or None, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be an UI or None, not {type(value)} !")


def _validate_optional_code_node(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is a CodeNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not None and not a CodeNode
    """
    from ..._DshellParser.ast_nodes import CodeNode
    
    if value is not None and not isinstance(value, CodeNode):
        if command_name:
            raise TypeError(f"{param_name} must be a CodeNode or None, not {type(value)}")
        else:
            raise TypeError(f"{param_name} must be a CodeNode or None, not {type(value)}")


def _validate_optional_list_node(value, param_name: str, command_name: str = None):
    """
    Validate that an optional value is a ListNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not None and not a ListNode
    """
    from ..._DshellParser.ast_nodes import ListNode
    
    if value is not None and not isinstance(value, ListNode):
        if command_name:
            raise TypeError(f"{param_name} must be a list in {command_name} command, not {type(value)}")
        else:
            raise TypeError(f"{param_name} must be a list, not {type(value)}")


# Required parameter validation functions

def _validate_required_bool(value, param_name: str, command_name: str = None):
    """
    Validate that a required value is a boolean type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not a boolean
    """
    if not isinstance(value, bool):
        if command_name:
            raise Exception(f"{param_name} must be a boolean in {command_name} command, not {type(value)} !")
        else:
            raise Exception(f"{param_name} must be a boolean, not {type(value)} !")


def _validate_required_list_node(value, param_name: str, command_name: str = None):
    """
    Validate that a required value is a ListNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not a ListNode
    """
    from ..._DshellParser.ast_nodes import ListNode
    
    if not isinstance(value, ListNode):
        if command_name:
            raise TypeError(f"{param_name} must be a list in {command_name} command, not {type(value)}")
        else:
            raise TypeError(f"{param_name} must be a list, not {type(value)}")


def _validate_required_int(value, param_name: str, command_name: str = None):
    """
    Validate that a required value is an integer type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not an integer
    """
    if not isinstance(value, int):
        if command_name:
            raise TypeError(f"{param_name} must be an int in {command_name} command, not {type(value)}")
        else:
            raise TypeError(f"{param_name} must be an int, not {type(value)}")


def _validate_required_string(value, param_name: str, command_name: str = None):
    """
    Validate that a required value is a string type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not a string
    """
    if not isinstance(value, str):
        if command_name:
            raise TypeError(f"{param_name} must be a str in {command_name} command, not {type(value)}")
        else:
            raise TypeError(f"{param_name} must be a str, not {type(value)}")


def _validate_required_dict(value, param_name: str, command_name: str = None):
    """
    Validate that a required value is a dict type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not a dict
    """
    if not isinstance(value, dict):
        if command_name:
            raise TypeError(f"{param_name} must be a permission bloc in {command_name} command, not {type(value)}")
        else:
            raise TypeError(f"{param_name} must be a dict, not {type(value)}")


# Validation functions for _MissingSentinel or other types

def _validate_missing_or_type(value, param_name: str, allowed_types: tuple, type_description: str = None):
    """
    Validate that a value is either _MissingSentinel or one of the allowed types.
    This is useful for parameters that can be omitted (using MISSING sentinel) or have a specific type.
    
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param allowed_types: Tuple of allowed types (e.g., (int,), (str,), (bool,))
    :param type_description: Human-readable description of allowed types (e.g., "an integer", "a string")
    :raises Exception: If the value is not _MissingSentinel and not one of the allowed types
    """
    from Dshell.full_import import _MissingSentinel
    
    if not isinstance(value, (_MissingSentinel,) + allowed_types):
        if type_description is None:
            type_names = " or ".join(t.__name__ for t in allowed_types)
            type_description = type_names
        raise Exception(f"{param_name} must be {type_description}, not {type(value)} !")


def _validate_missing_or_bool(value, param_name: str):
    """
    Validate that a value is either _MissingSentinel or a boolean.
    
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :raises Exception: If the value is not _MissingSentinel and not a boolean
    """
    from Dshell.full_import import _MissingSentinel
    
    if not isinstance(value, (_MissingSentinel, bool)):
        raise Exception(f"{param_name} must be a boolean, not {type(value)} !")


def _validate_missing_or_int(value, param_name: str):
    """
    Validate that a value is either _MissingSentinel or an integer.
    
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :raises Exception: If the value is not _MissingSentinel and not an integer
    """
    from Dshell.full_import import _MissingSentinel
    
    if not isinstance(value, (_MissingSentinel, int)):
        raise Exception(f"{param_name} must be an integer, not {type(value)} !")


def _validate_missing_or_string(value, param_name: str):
    """
    Validate that a value is either _MissingSentinel or a string.
    
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :raises Exception: If the value is not _MissingSentinel and not a string
    """
    from Dshell.full_import import _MissingSentinel
    
    if not isinstance(value, (_MissingSentinel, str)):
        raise Exception(f"{param_name} must be a string, not {type(value)} !")


def _validate_missing_or_dict(value, param_name: str):
    """
    Validate that a value is either _MissingSentinel or a dict.
    
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :raises Exception: If the value is not _MissingSentinel and not a dict
    """
    from Dshell.full_import import _MissingSentinel
    
    if not isinstance(value, (_MissingSentinel, dict)):
        raise Exception(f"{param_name} must be a PermissionNode, not {type(value)} !")
