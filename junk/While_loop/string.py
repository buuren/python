
def changeCase(word):
	for x in word:
		if x.isupper() == True:
			y = x.lower()
			word = word.replace(x, y)
		else:
			y = x.upper()
			word = word.replace(x, y)
			
	return word


def piApprox(num):
	y = 0
	i = 1
	pi = 0.00
	arr = []
	minus = []
	plus = []
	while i < num:
		if i % 2 == 0:
			x = 1
		else:
			arr.append(i)
		i += 1
	
	for x in arr:
		ind = arr.index(x)
		if ind % 2 == 0:
			plus.append(1.00/x)
		else:
			minus.append(-1 * 1.00/x)

	if len(plus) == 0:
		test = 0
	else:
		test = 1
		plus.remove(1.0)
		
	min_sum = sum(minus)
	plus_sum = sum(plus)
	
	pi = 4.00 * (1.00 + plus_sum + min_sum)
	print pi





