def matrixDimensions(m):
	test = []
	y = len(m)
	for x in m:
		lol = len(x)
		test.append(lol)
		eq = test[1:] == test[:-1]
	if eq is False:
		print "This is not a valid matrix."
	else:
		print 'This is a %dx%u matrix.' % (y,lol)
		
def combine(la, lb):
	new = []
	#for x, y in map(None, la, lb):
		
	#	print y
	#	new.extend([x, y])
	#print sorted(new)
	for x in la:
		new.append(x)
	for y in lb:
		new.append(y)
	return sorted(new)
import random
	
p1 = random.randint(1,1000)
p2 = random.randint(1,1000)
p3 = random.randint(1,1000)
p4 = random.randint(1,1000)
k1 = random.randint(1,1000)
k2 = random.randint(1,1000)
k3 = random.randint(1,1000)
k4 = random.randint(1,1000)
i1 = random.randint(1,1000)
i2 = random.randint(1,1000)
i3 = random.randint(1,1000)
i4 = random.randint(1,1000)
h1 = random.randint(1,1000)
h2 = random.randint(1,1000)
h3 = random.randint(1,1000)
h4 = random.randint(1,1000)


matrix = [[p1,p2,p3,p4], [p1,p2,p3,p4], [i1,i2,i3,i4], [h1,h2,h3,h4]]
def transpose(matrix):
	new2 = []
	for eq in matrix:
		leneq = len(eq)
		new2.append(leneq)
	xeq = new2[1:] == new2[:-1]
	if xeq is False:
		return
	else:
		new = []
		new1 = []
		k = 0
		p = 0
		while k < len(matrix):
			ele = matrix[k]
			new.extend(ele)
			k += 1
		lennew = len(new)
		j = 0
		while j < lennew - (lennew/2):
			para = lennew / 2
			ele1 = new[j]
			ele2 = new[para+j]
			if lennew == 0:
				new1 = matrix
			elif lennew == 1:
				new1.append([ele1])
			elif lennew == 2:
				new1.append([ele1])
				new1.append([ele2])
			else:
				new1.append([ele1, ele2])
			j +=1
		print new1
transpose(matrix)