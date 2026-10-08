from functools import wraps

from ..full_import import ContextVar, Callable

# Message objects are scoped to one interpreter execution context.
dshell_cached_messages = ContextVar('dshell_cached_messages', default=None)


def get_cached_messages() -> dict:
    """Return the cache belonging to the current interpreter context."""
    try:
        cached_messages = dshell_cached_messages.get()
    except LookupError as error:
        raise RuntimeError("Message cache used outside an interpreter context") from error

    if cached_messages is None:
        raise RuntimeError("Message cache has already been released")
    return cached_messages


def cache_message(message) -> None:
    """Keep a message available for subsequent commands in this context."""
    get_cached_messages()[message.id] = message


def with_message_cache(function: Callable) -> Callable:
    """Give one top-level interpreter execution an isolated message cache."""
    @wraps(function)
    async def execute_with_cache(*args, **kwargs):
        if dshell_cached_messages.get() is not None:
            return await function(*args, **kwargs)

        token = dshell_cached_messages.set({})
        try:
            return await function(*args, **kwargs)
        finally:
            dshell_cached_messages.reset(token)

    return execute_with_cache