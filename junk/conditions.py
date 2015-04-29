def pairwiseScore12(seqA, seqB): 

	seq_a, seq_b, diff_list, last_list = [], [], [], []
	ind, score, lol, lol_new = 0, 0, 0, 0
	
	for a in seqA:
		seq_a.append(a)
	for b in seqB:
		seq_b.append(b)
	
	while ind < len(seq_a):
		a_list = seq_a[ind]
		b_list = seq_b[ind]
		if a_list == b_list:
			diff_list.append(ind)
		else:
			score = score - 1
		ind = ind + 1

	while lol < len(diff_list):
		first_num = diff_list[lol]
		second_num = diff_list[lol+1]
		
		if second_num - first_num == 1:
			print "lol"
		else: 
			print "nothing"
		
		#print '%d - %d' % (first_num, second_num)
		lol = lol + 1

def pairwiseScore(seqA, seqB): 
	score = 0
	seqPos = 0
	isConsecutive = False
	str1 = ''
	for i in seqA:
		if i == seqB[seqPos:seqPos + 1]:
			if isConsecutive == True:
				score += 3
			else:
				score += 1
			isConsecutive = True
			str1 += "|"
		else:
			score -= 1     
			isConsecutive = False
		str1 += " "
		seqPos += 1
	score = str(score)
	print(seqA + '\n' + str1 + '\n' + seqB + '\nScore: ' + score)

pairwiseScore('ATCG', 'ATCG')
pairwiseScore('CATTCATCATGCAA', 'GATAAATCTGGTCT')