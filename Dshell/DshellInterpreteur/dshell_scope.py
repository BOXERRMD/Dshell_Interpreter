from contextlib import contextmanager
from typing import Any, Optional, Dict, Set

class Scope:
    """
    Represents a variable scope with optional parent scope for nested scoping.
    """
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent: Optional['Scope'] = parent
        self.vars: Dict[str, Any] = {}

    def get(self, name: str) -> Any:
        """
        Get a variable value from this scope or parent scopes.
        :param name: Variable name
        :return: Variable value
        :raises KeyError: If variable not found in any scope
        """
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise KeyError(name)

    def set(self, name: str, value: Any) -> None:
        """
        Set a variable in this scope.
        :param name: Variable name
        :param value: Variable value
        """
        self.vars[name] = value

    def update(self, mapping: Dict[str, Any]) -> None:
        """
        Update multiple variables in this scope.
        :param mapping: Dictionary of variable names and values
        """
        self.vars.update(mapping)

    def contains(self, name: str) -> bool:
        """
        Check if a variable exists in this scope or parent scopes.
        :param name: Variable name
        :return: True if variable exists, False otherwise
        """
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.contains(name)
        return False

    def keys(self) -> Set[str]:
        """
        Get all variable names from this scope and parent scopes.
        :return: Set of variable names
        """
        keys = set(self.vars.keys())
        if self.parent:
            keys.update(self.parent.keys())
        return keys

    def clear(self) -> None:
        """Clear all variables in this scope (does not affect parent)."""
        self.vars.clear()

@contextmanager
def new_scope(interpreter, initial_vars: Optional[Dict[str, Any]] = None):
    """
    Context manager for creating a new scope temporarily.
    :param interpreter: The interpreter instance
    :param initial_vars: Optional initial variables for the new scope
    """
    parent = interpreter.env
    interpreter.env = Scope(parent)
    if initial_vars:
        interpreter.env.update(initial_vars)
    try:
        yield
    finally:
        interpreter.env.clear()
        interpreter.env = parent
