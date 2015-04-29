aList = ['Hello', 0, 20.0, 'World']
aList = ['Hello']
aList.append(0)
aList.append(20.0)
aList.append('World')
aList = ['hello', 'i', 'love', 'python', 'programming']
aList.remove('i')
aList.remove('love')

#Write a function addNumbersInList(numbers) to add all the numbers in a list. To access each element in a list, 
#you can use the statement 'for num in numbers:
def addNumbersInList(numbers): 
	sum = 0
	for x in numbers:
		sum += x
	return sum
	
#Write a function addOddNumbers(numbers) to add all the odd numbers in a list. To access each element in a list, 
#you can use the statement 'for num in numbers:'
def addOddNumbers(numbers): 
	sum = 0
	for x in numbers:
		odd = x % 2
		if odd == 1:
			sum += x
	return sum
	
#Write a function countOddNumbers(numbers) to count the number of odd numbers in a list.
def countOddNumbers(numbers): 
	y = 0
	test = []
	sum = 0
	for x in numbers:
		odd = x % 2
		if odd == 1:
			test.append(x)
	return len(test)

#Write a function getEvenNumbers(numbers) to return all the even numbers in a list.
def getEvenNumbers(numbers): 
	y = 0
	test = []
	sum = 0
	for x in numbers:
		odd = x % 2
		if odd == 0:
			test.append(x)
	return test
	
#Write a function removeFirstAndLast(list) that takes in a list as an argument and remove
#the first and last elements from the list. The function will return a list with the remaining items.
def removeFirstAndLast(numbers):
	if len(numbers) == 0:
		return
	else:
		del numbers[0]
	
	if len(numbers) <= 0:
		return numbers
	else:
		del numbers[len(numbers)-1]
		return numbers
#Write a function getMaxNumber(numbers) that returns the maximum number in a list.
def getMaxNumber(numbers):
	if len(numbers) == 0:
		return 'N.A'
	else: 
		m = max(numbers)
		return m

#Write a function removeFirstAndLast(list) that takes in a list as an argument and remove the 
#first and last elements from the list. The function will return a list with the remaining items.
def removeFirstAndLast(numbers):
	if len(numbers) == 0:
		return
	else:
		del numbers[0]
		
	if len(numbers) <= 0:
		return numbers
	else:
		del numbers[len(numbers)-1]
		return numbers

#Write a function getMaxNumber(numbers) that returns the maximum number in a list.
def getMaxNumber(numbers):
	if len(numbers) == 0:
		return 'N.A'
	else: 
		m = max(numbers)
		return m
		
#Write a function getMinNumber(numbers) that returns the minimum number in a list.
def getMinNumber(numbers):
	if len(numbers) == 0:
		return 'N.A'
	else: 
		m = min(numbers)
		return m
		
#A mxn matrix, m rows and n columns, can be represented using nested lists. Write a function that returns the diminensions of a matrix.
def matrixDimensions(m):
	test = []
	y = len(m)
	for x in m:
		lol = len(x)
		test.append(lol)
		eq = test[1:] == test[:-1]
	if eq is False:
		return "This is not a valid matrix."
	else:
		return 'This is a %dx%u matrix.' % (y,lol)




