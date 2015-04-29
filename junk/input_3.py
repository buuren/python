#stored_words = []
from __future__ import division
#for word in words:
#	answer = raw_input("Please enter a %s:" % word)
#	stored_words.append(answer)
#print stored_words

def maximum(x, y):
	c = x + y
	return c

#print maximum(2, 3)


# Note: Return a string of 1 decimal place.
def BMI(weight, height):
	b = float(weight) / (float(height) * float(height))
	c = '%.1f' % b
	return c
	
def getSumOfLastDigits(numList):
	array_c = []
	for c in numList:
		c = c % 10
		array_c.append(c)
	print sum(array_c)
	#return sum(numList)
	
#getSumOfLastDigits([1, 23, 456])


def introduce(name, age=0):
    msg = "My name is %s. " % name
    if age == 0:
       msg += "My age is secret."
    else:
       msg += "I am %s" % age +  " years old."
    return msg 
print "-----------------------------"

def addFirstAndLast(x):
	arr = len(x)
	
	if arr == 0:
		return 0
	if arr == 1:
		return x[0]
	if arr == 2:
		return x[0] + x[1]
	
	if arr > 2:
		first = x[0]
		last = x[arr - 1]
		return first + last

#addFirstAndLast([2, 7, 3])

# Complete the 'lambda' expression so that it returns True if the argument is an even number, and False otherwise.
even = lambda x: x % 2 == 0

def addOne(x):
	return x + 1
        
def useFunction(func, num):
	print addOne(func) + num

# Write a function, given a string of characters, return the string together with '_'s of the same length.
def underline(title): 
	a = len(title)
	return title + ("\n") +("_")*a