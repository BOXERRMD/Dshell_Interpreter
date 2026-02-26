from re import findall

print(findall(r"`.*?`", "debug {`len [0,1,2]` + {`len [0]`}}"))