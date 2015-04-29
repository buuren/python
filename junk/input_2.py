def main():
	n=input("Enter an integer:")
	num=1
	numArrays=1
	array=[]
	subArray=[]
	while num<factorial(n):
		while numArrays<(factorial(n-1)-1):
			subArray.append(num)
			numArrays+=1
			num+=1
		array.append(subArray)
	print array
		
def factorial(n):
	sum=1
	i=2
	while i<=n:
		sum*=i
	return sum

def method1():
    return 'hello world'

def method2(methodToRun):
    result = methodToRun()
    return result
	
aList = ['Hello']

for i in [2, 3, 4]:
	aList.append(i)

for l in aList:
	print l


#print aList