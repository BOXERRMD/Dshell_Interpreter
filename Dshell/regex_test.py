from regex import search, findall

print(findall(r"""(?P<brace>\{(?:[^{}]+|(?&brace))*\})""", "debug  {{A+B{.}} + {d+c}} + {test} ", overlapped=False))