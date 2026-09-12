from contextlib import contextmanager
from typing import Any, Optional, Dict, Set
from .dshell_global_variables import Nothing, LIMIT_MEMORY
from ..full_import import getsizeof


class Scope:
    """
    Represents a variable scope with optional parent scope for nested scoping.
    """
    def __init__(self, parent: Optional["Scope"] = None):
        self.parent: Optional[Scope] = parent
        self.vars: Dict[str, Any] = {}
        self.size: int = 0 # the byte size of the scope, used for memory management

    def is_limit_memory_reached(self) -> bool:
        """
        Check if the memory limit for this scope has been reached.
        :return: False if the memory limit has not been reached, Raise an error if the memory limit has been reached
        """
        if self.size >= LIMIT_MEMORY:
            raise MemoryError(f"Memory limit reached ! You are trying to use {self.size} bytes, but the limit is {LIMIT_MEMORY} bytes.")
        return False

    def get(self, name: str, default: Any = Nothing()) -> Any:
        """
        Get a variable value from this scope or parent scopes.
        :param name: Variable name
        :param default: The default variable to return if nothing was found
        :return: Variable value
        :raises KeyError: If variable not found in any scope
        """
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        if not isinstance(default, Nothing):
            return default
        del default
        raise KeyError(name)

    def set(self, name: str, value: Any, size_memory: bool = True) -> None:
        """
        Set a variable in this scope.
        :param name: Variable name
        :param value: Variable value
        :param size_memory: Whether to count the size of the variable in memory management
        """
        if name in self.vars:
            self.size -= getsizeof(self.vars[name])  # Remove the size of the old value

        if size_memory:
            self.size += getsizeof(value)  # Update the size of the scope

        self.is_limit_memory_reached()
        self.vars[name] = value

    def update(self, mapping: Dict[str, Any], size_memory: bool = True) -> None:
        """
        Update multiple variables in this scope.
        :param mapping: Dictionary of variable names and values
        :param size_memory: Whether to count the size of the variables in memory management
        """
        for key, value in mapping.items():
            self.set(key, value, size_memory)
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
def new_scope(interpreter, initial_vars: Optional[Dict[str, Any]] = None, size_memory: bool = True):
    """
    Context manager for creating a new scope temporarily.
    :param interpreter: The interpreter instance
    :param initial_vars: Optional initial variables for the new scope
    :param size_memory: Whether to count the size of the variables in memory management
    """
    parent = interpreter.env

    new_scope: Scope = Scope(parent=parent)
    new_scope.size = parent.size # inherit the size from the parent scope

    interpreter.env = new_scope

    if initial_vars:
        interpreter.env.update(initial_vars, size_memory=size_memory)
    try:
        yield
    finally:
        interpreter.clear()
        interpreter.env = parent

