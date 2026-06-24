from contextlib import contextmanager
from typing import Any, Optional, Dict, Set, Union
from random import random

# manage all scope with one unique ID by scope to separate the interpreter and scopes
context_scope: dict[str, tuple[int, "Scope"]] = {}

def generate_scope_id() -> str:
    """
    generate a new scope code unused
    :return:
    """
    while (_id := (str(random()) + str(random()))) in context_scope: pass
    return _id


def get_scope(_id: str) -> Union["Scope", None]:
    """
    Get the current scope linked with an ID
    :param _id:
    :return: the scope link with the id, or None if the scope id is not found
    """
    x = context_scope.get(_id, None)
    return x[1] if x is not None else x

def get_usage_scope(_id: str) -> Union[int, None]:
    """
    Get the usage number for a scope
    :param _id: An integer, or None if the scope id is not found
    :return:
    """
    x = context_scope.get(_id, None)
    return x[0] if x is not None else x

class Scope:
    """
    Represents a variable scope with optional parent scope for nested scoping.
    """
    def __init__(self, parent: Optional[str] = None):
        self.parent: Optional[str] = parent
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
            if self.parent in context_scope:
                return context_scope[self.parent][1].get(name)
            raise Exception(f"Scope {self.parent} not found [get] !")
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
            if self.parent in context_scope:
                return context_scope[self.parent][1].contains(name)
            Exception(f"Scope {self.parent} not found [contains] !")
        return False

    def keys(self) -> Set[str]:
        """
        Get all variable names from this scope and parent scopes.
        :return: Set of variable names
        """
        keys = set(self.vars.keys())
        if self.parent:
            if self.parent in context_scope:
                keys.update(context_scope[self.parent][1].keys())
            else:
                Exception(f"Scope {self.parent} not found [keys] !")
        return keys

    def clear(self) -> None:
        """Clear all variables in this scope (does not affect parent)."""
        self.vars.clear()


def create_scope() -> str:
    """
    Create a new scope and return the scope code
    :return:
    """
    _id = generate_scope_id()
    scope = Scope()
    context_scope[_id] = (1, scope)
    return _id

def update_nbr_usage_scope(scope_id: str, nbr_usage: int):
    """
    Update the usage number for a scope
    :param nbr_usage:
    :return:
    """
    if scope_id not in context_scope:
        raise Exception(f"Scope {scope_id} not found [update nbr usage scope] !")

    new_usage = get_usage_scope(scope_id)+nbr_usage

    if new_usage <= 0:
        del context_scope[scope_id]
        return

    new = (new_usage, context_scope[scope_id][1])

    del context_scope[scope_id]
    context_scope[scope_id] = new


@contextmanager
def new_scope(interpreter, initial_vars: Optional[Dict[str, Any]] = None):
    """
    Context manager for creating a new scope temporarily.
    :param interpreter: The interpreter instance
    :param initial_vars: Optional initial variables for the new scope
    """
    parent = interpreter.scope_id

    new_scope_id: str = generate_scope_id()
    context_scope[new_scope_id] = (1, Scope(parent))

    interpreter.scope_id = new_scope_id
    interpreter.env = get_scope(new_scope_id)

    if initial_vars:
        interpreter.env.update(initial_vars)
    try:
        yield
    finally:
        interpreter.clear()
        interpreter.env = get_scope(parent)
        interpreter.scope_id = parent

