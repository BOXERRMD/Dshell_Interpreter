from re import sub, search

print(sub(f"(?<![a-zA-Z])p(?![a-zA-Z])", "debug", "{p*2}"))