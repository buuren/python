#Create a function generateNumbers(num) that takes in a positive number as argument and returns a list of
#number from 0 to that number inclusive. Note: The function range(5) will return a list of number [0, 1, 2, 3, 4].
def generateNumber(num):
	m = []
	new = num + 1
	while new > 0:
		x = new - 1
		m.append(x)
		new = new - 1
	m.reverse()
	return m	

#Create a function generateNumbers(start, end) that takes in two numbers as arguments and returns a list of
#numbers starting from start to the end number (inclusive) specified in the arguments. Note: The function range(x, y) 
#can takes in 2 arguments. For example, range(1, 5) will return a list of numbers [1,2,3,4].
def generateNumber(start, end):
	m = []
	new = end + 1
	while new > start:
		x = new - 1
		m.append(x)
		new = new - 1
	m.reverse()
	return m

#Create a function generateNumbers(start, end, step) that takes in three numbers as arguments and returns 
#a list of numbers ranging from start to the end number (inclusive)and skipping numbers based on the step
#specified in the arguments. Note: The function range(x, y, z) can takes in 3 arguments. For example, range(1, 11, 2)
# will return a list of numbers [1,3,5,7,9].
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
	return m
	
#Create a function addNumbers(num) that takes in a positive number as argument and returns the sum of all 
#the number between 0 and that number (inclusive).
def addNumbers(num):
	if num < 0:
		a = 5
	else:
		m = []
		m.append(num)
		while num > 0:
			x = num - 1
			m.append(x)
			num = num - 1
	return sum(m)

#Create a function addNumbers(start, end) that takes in two positive numbers as arguments and returns the sum 
#of all the number between the start and end number (inclusive).
def addNumbers(start, end):
	if start > 0 and end > 0:
		print "lol"
		m = []
		m.append(end)
		while end > start:
			x = end - 1
			m.append(x)
			end = end - 1
	return sum(m)
	
#Create a function addNumbers(start, end) that takes in two positive numbers as arguments and returns the sum of all 
#the number between the start and end number (inclusive)
def addNumbers(start, end):
	if start > 0 and end > 0:
		print "lol"
		m = []
		m.append(end)
		while end > start:
			x = end - 1
			m.append(x)
			end = end - 1
	return sum(m)
	
#Create a function addEvenNumbers(start, end) that takes in two positive numbers as arguments and returns the sum of all 
#the even numbers between the start and end number (inclusive). Note: x % 2 returns 0 if x is an even number.
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