#Write a function to convert temperature from Celsius to Fahrenheit scale.
#oC to oF Conversion: Multipy by 9, then divide by 5, then add 32.
# Note: Return a string of 2 decimal places.
def Cel2Fah(temp): 
	c = (temp * 9) / 5 + 32
	b = '%.2f' % c
	return b
	
#Python provides many built-in modules with many useful functions. One such module is the math module. The math module 
#provides many useful functions such as sqrt(x), pow(x, y), ceil(x), floor(x) etc. You will need to do a "import math" 
#before you are allowed to use the functions within the math module.
import math
# Calculate the square root of 16 and stores it in the variable a
a = math.sqrt(16)
# Calculate 3 to the power of 5 and stores it in the variable b
b = math.pow(3, 5)
# Calculate area of circle with radius = 3.0 by making use of the math.pi constant and store it in the variable c
c = math.pi * math.pow(3, 2)

#Write a function getSumofLastDigits() that takes in a list of positive numbers and returns the sum of all the last digits in the list.
def getSumOfLastDigits(numList):
	array_c = []
	for c in numList:
		c = c % 10
		array_c.append(c)
	return sum(array_c)
	
#Write a function percent(value, total) that takes in two numbers as arguments, and returns the percentage value as an integer.
def percent(value, total):
	return 100 * value / total
	
#The Pythagoras' Theorem for a right-angle triangle can be written as a2+b2 = c2, where a and b are sides of the right angle and 
#c is the hypotenuse. Write a function to compute the hypotenuse given sides a and b of the triangle.
# Hint: You can use math.sqrt(x) to compute the square root of x.
import math
def hypotenuse(a, b): 
	temp = a*a + b*b
	return math.sqrt(temp)
	
#Define a function calls addFirstAndLast(x) that takes in a list of numbers and returns the sum of the first and last numbers.
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

#lambda can be considered to be an anonymous and/or inline function. It takes the form of "lambda args : expression."
# Complete the 'lambda' expression so that it returns True if the argument is an even number, and False otherwise.
even = lambda x: x % 2 == 0

#The first string statement after a function definition is the docstring. It can be accessed by the __doc__ keyword.
# Add in the documentation string which gives the same output shown in the example.
def getScore(data):
    "A function that computes and returns the final score."
    return score 
	
#Write a function calDistance(x1, y1, x2, y2) to calculate the distance between two points represented by Point 1 (x1, y1) 
#and Point 2 (x2, y2). The formula for calculating distance is given below:
#     distance = v (x2-x1)2 +  (y2-y1)2
import math
def calDistance (x1, y1, x2, y2):
	x = math.pow((x2-x1), 2)
	y = math.pow((y2-y1), 2)
	z = math.pow((x + y), 0.5)
	return z

