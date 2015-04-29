#Create a function addNumbers(x) that takes a number as an argument and adds all the integers between 1 and the number (inclusive)
#and returns the total number.
def addNumbers(num):
	total = 0
	i = 1
	while i <= num:
		print i
		total = total + i
		i = i + 1
	return total

#Create a function addNumbers(start, end) that adds all the integers between the start and end value (inclusive) and returns the total sum.
def addNumbers(start, end):
	total = 0
	while start <= end:	
		total = total + start
		start = start  + 1
	return total

#Create a function countPages(x) that takes the number of pages of a book as an argument and counts the number of times the digit '1' appears
#in the page number.
def countPages(num):
	total = 0
	i = 1
	while i <= num:
		page_no = str(i)
		total += page_no.count('1')
		i = i + 1
	return total 