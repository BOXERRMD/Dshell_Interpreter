from sys import getsizeof

MAX_STR_SIZE = 5000*getsizeof(str)
MAX_LIST_SIZE = 10000*getsizeof(str)
# Constants for sleep time limits
MAX_SLEEP_TIME_SECONDS = 3600  # 1 hour
MIN_SLEEP_TIME_SECONDS = 1