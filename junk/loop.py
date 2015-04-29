def generateNumber(start, end, step):

	if step < 0:
		step = step * (-1)
	else:
		step = step

	m = []
	
	if start < end:

		m.append(start)
		while start < end:
			x = start + step
			if x > end:
				a = 5
			else:
				m.append(x)
			start = start + step
	elif start > end:

		m.append(start)
		while start > end:
			x = start - step
			if x < end:
				a = 5
			else:
				m.append(x)
			start = start - step
	else:
		m.append(start)
	print m

def addNumbers(start, end):
	if start > 0 and end > 0:
		print "lol"
		m = []
		m.append(end)
		while end > start:
			x = end - 1
			m.append(x)
			end = end - 1
	print sum(m)

def addEvenNumbers(start, end):
	if start > 0 and end > 0:
		print "lol"
		m = []
		if end % 2 == 0:
			m.append(end)
		else:
			a = 5
		while end > start:
			x = end - 1
			if x % 2 == 0:
				m.append(x)
			else:
				a = 5
			end = end - 1
	return sum(m)

addEvenNumbers(3, 7)