buffer = ''
while True:
    line = raw_input()

    if not line: break

    buffer += " " + line

print "You entered: "
buffer = buffer.replace(" ", "\n")
print buffer

print "-----------------"

# Blank list
classes = []

numb = int(raw_input('How many classes have you taken? '))
for x in range(numb):
	classes.append(raw_input(('Name of class #' + `x+1` + ' ')))