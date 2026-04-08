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
    "_validate_optional_eval_group_node",
    "_validate_required_bool",
    "_validate_required_list_node",
    "_validate_required_int",
    "_validate_required_string",
    "_validate_required_dict",
    "_validate_missing_or_type",
    "_validate_not_none",
    "_validate_has_attribute",
]


def _validate_optional_string(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a string type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a string
    """
    if value is not None and not isinstance(value, str):
        raise TypeError(f"[{command_name}] -> {param_name} must be a string, not {type(value).__name__} !")


def _validate_optional_int(value, param_name: str, command_name: str):
    """
    Validate that an optional value is an integer type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not an integer
    """
    if value is not None and not isinstance(value, int):
        raise TypeError(f"[{command_name}] -> {param_name} must be an integer, not {type(value).__name__} !")


def _validate_optional_bool(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a boolean type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a boolean
    """
    if value is not None and not isinstance(value, bool):
        raise TypeError(f"[{command_name}] -> {param_name} must be a boolean, not {type(value).__name__} !")


def _validate_optional_number(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a number (int or float) type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a number
    """
    if value is not None and not isinstance(value, (int, float)):
        raise TypeError(f"[{command_name}] -> {param_name} parameter must be a number (seconds) or None, not {type(value).__name__} !")


def _validate_optional_dict(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a dict type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not a dict
    """
    if value is not None and not isinstance(value, dict):
        raise TypeError(f"[{command_name}] -> {param_name} must be a PermissionNode, not {type(value).__name__} !")


def _validate_optional_embed(value, param_name: str, command_name: str):
    """
    Validate that an optional value is an Embed or ListNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not an Embed or ListNode
    """
    from Dshell.full_import import Embed
    from ...DshellParser.ast_nodes import ListNode
    
    if value is not None and not isinstance(value, (ListNode, Embed)):
        raise TypeError(f"[{command_name}] -> {param_name} must be a list of Embed objects or a single Embed object, not {type(value).__name__} !")


def _validate_optional_view(value, param_name: str, command_name: str):
    """
    Validate that an optional value is an EasyModifiedViews type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not None and not an EasyModifiedViews
    """
    from Dshell.full_import import EasyModifiedViews
    
    if value is not None and not isinstance(value, EasyModifiedViews):
        raise TypeError(f"[{command_name}] -> {param_name} must be an UI or None, not {type(value).__name__} !")


def _validate_optional_code_node(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a CodeNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not None and not a CodeNode
    """
    from ...DshellParser.ast_nodes import CodeNode
    
    if value is not None and not isinstance(value, CodeNode):
        raise TypeError(f"[{command_name}] -> {param_name} must be a CodeNode or None, not {type(value).__name__}")

def _validate_optional_eval_group_node(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a EvalNode type.
    :param value:
    :param param_name:
    :param command_name:
    :return:
    """
    from ...DshellParser.ast_nodes import EvalGroupNode

    if value is not None and not isinstance(value, EvalGroupNode):
        raise TypeError(f"[{command_name}] -> {param_name} must be an EvalGroupNode or None, not {type(value).__name__}")

def _validate_optional_list_node(value, param_name: str, command_name: str):
    """
    Validate that an optional value is a ListNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not None and not a ListNode
    """
    from ...DshellParser.ast_nodes import ListNode
    
    if value is not None and not isinstance(value, ListNode):
        raise TypeError(f"[{command_name}] -> {param_name} must be a list, not {type(value).__name__}")


# Required parameter validation functions

def _validate_required_bool(value, param_name: str, command_name: str):
    """
    Validate that a required value is a boolean type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises Exception: If the value is not a boolean
    """
    if not isinstance(value, bool):
        raise TypeError(f"[{command_name}] -> {param_name} must be a boolean, not {type(value).__name__} !")


def _validate_required_list_node(value, param_name: str, command_name: str):
    """
    Validate that a required value is a ListNode type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not a ListNode
    """
    from ...DshellParser.ast_nodes import ListNode
    
    if not isinstance(value, ListNode):
        raise TypeError(f"[{command_name}] -> {param_name} must be a list, not {type(value).__name__}")


def _validate_required_int(value, param_name: str, command_name: str):
    """
    Validate that a required value is an integer type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not an integer
    """
    if not isinstance(value, int):
        raise TypeError(f"[{command_name}] -> {param_name} must be an int, not {type(value).__name__}")


def _validate_required_string(value, param_name: str, command_name: str):
    """
    Validate that a required value is a string type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"[{command_name}] -> {param_name} must be a str, not {type(value).__name__}")


def _validate_required_dict(value, param_name: str, command_name: str):
    """
    Validate that a required value is a dict type.
    :param value: The value to validate
    :param param_name: The parameter name for error messages
    :param command_name: The command name for error messages (optional)
    :raises TypeError: If the value is not a dict
    """
    if not isinstance(value, dict):
        raise TypeError(f"[{command_name}] -> {param_name} must be a dict, not {type(value).__name__}")


# Validation functions for _MissingSentinel or other types

def _validate_missing_or_type(value, value_name: str, *types_and_command):
    """
    Validate that a value is either _MissingSentinel or one of the specified types.
    This is useful for parameters that can be omitted (using MISSING sentinel) or have a specific type.
    
    The _MissingSentinel is automatically included in the validation, so you only need to pass
    the other allowed types.
    
    :param value: The value to validate
    :param value_name: The parameter name for error messages
    :param types_and_command: Variable number of allowed types (e.g., int, str, bool) followed optionally by command_name (str) as last parameter
    :raises Exception: If the value is not _MissingSentinel and not one of the specified types
    
    Example:
        _validate_missing_or_type(position, "Position", int, "command_name")
        _validate_missing_or_type(value, "Value", int, str, float, "command_name")
    """
    from Dshell.full_import import _MissingSentinel
    
    # Check if last parameter is a string (command_name), otherwise it's a type
    types = types_and_command
    command_name = ""
    
    if types_and_command and isinstance(types_and_command[-1], str):
        # Last argument is command_name
        types = types_and_command[:-1]
        command_name = f"[{types_and_command[-1]}] -> "
    
    # Include _MissingSentinel in the allowed types
    allowed_types = (_MissingSentinel,) + types
    
    if not isinstance(value, allowed_types):
        # Build error message dynamically
        type_names = [_MissingSentinel.__name__] + [t.__name__ for t in types]
        type_description = " or ".join(type_names)
        raise Exception(f"{command_name}{value_name} must be {type_description}, not {type(value).__name__} !")


def _validate_not_none(value, error_message: str):
    """
    Validate that a value is not None.
    
    This is a generic function to check if a value is None and raise a custom error message.
    Useful for validating that objects (like channels, messages, etc.) were found/retrieved successfully.
    
    :param value: The value to check
    :param error_message: Custom error message to raise if value is None
    :raises Exception: If the value is None
    
    Example:
        channel = ctx.channel.guild.get_channel(channel_id)
        _validate_not_none(channel, f"Channel {channel_id} not found !")
    """
    if value is None:
        raise Exception(error_message)


def _validate_has_attribute(obj, attr_name: str, error_message: str):
    """
    Validate that an object has a specific attribute.
    
    This is a generic function to check if an object has an attribute using hasattr()
    and raise a custom error message if it doesn't.
    Useful for checking if objects have expected attributes (e.g., text channel has 'topic').
    
    :param obj: The object to check
    :param attr_name: The name of the attribute to check for
    :param error_message: Custom error message to raise if attribute is missing
    :raises Exception: If the object doesn't have the specified attribute
    
    Example:
        _validate_has_attribute(channel, 'topic', f"Channel {channel_id} is not a text channel !")
    """
    if not hasattr(obj, attr_name):
        raise Exception(error_message)

