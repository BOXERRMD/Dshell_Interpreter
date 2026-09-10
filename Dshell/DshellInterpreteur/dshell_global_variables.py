

MAX_STR_SIZE = 10_000 # bytes
MAX_LIST_SIZE = 64_000 # bytes
MAX_FILE_SIZE = 250_000 # bytes
# Constants for sleep time limits
MAX_SLEEP_TIME_SECONDS = 3_600  # 1 hour
MIN_SLEEP_TIME_SECONDS = 1

MAX_WAIT_MESSAGE_TIMEOUT = 300

LIMIT_MEMORY = 625_000  # 8 MB

class Nothing:
    """
    Do nothing.
    Used if None is a usable value.
    """