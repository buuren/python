import time

def factorial(num):
	product = 1
	i = num
	while i > 0: 
		product = product * i
		i = i - 1
	return product
	
def doubleFactorial(num):
	product = 1 
	i = 0
	k = 1
	while k < num:
		k = 2 * i + 1
		product *= k 
		i += 1
	return product 

def primeNumbers(num):
	primes = [] 
	i = 2
	while i <= num:
		k = 2
		isPrime = True
		while k < i:
			if i % k ==0:
				isPrime = False
			k = k + 1
		if isPrime:
			primes.append(i)
		i = i + 1
	a = 0
	while a < 10000:
		print primes
		time.sleep(1)
		a = a + 1
	
primeNumbers(15000)