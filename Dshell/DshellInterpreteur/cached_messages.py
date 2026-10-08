from ..full_import import ContextVar

# Message objects are scoped to one interpreter execution context.
dshell_cached_messages = ContextVar('dshell_cached_messages')


def start_message_cache() -> object:
    """Create a cache and return the token needed to restore the previous one."""
    return dshell_cached_messages.set({})


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


def reset_message_cache(token: object) -> None:
    """Release this execution context and restore its parent context."""
    dshell_cached_messages.reset(token)