from regex import search, findall

print(findall(r"\{([^{}]|(?R))*\}", "debug  {{A+B} + {d+c}} "))