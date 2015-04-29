def fromDectoOctHex(number):
	print '-----------------------------------------------'
	w = []
	w_start = 0
	a = 1
	w.append(number)
	if number == 8 or number == 9:
		print 'Invalid number'
	else:
		len_number = len(str(abs(number)))
		int(len_number)
		while w_start < len_number:
			m_name = '0' * (len_number)
			k = '1%s' % m_name
			while a < int(k):
				last_num = number / a
				remind = last_num % 8
				w.append(remind)
				a = a * 8
			w_start = w_start + 1
		del w[0]
		if len(w) % 2 != 0 and len(w) < 7 or len(w) == 2:
			last_ele = len(w) - 1
			del w[last_ele]
			
		x = ''.join( map( str, reversed(w) ))
		print 'Octal number is \t%s' % x
	print '-----------------------------------------------'
	w_hex = []
	bin_number = number
	while 1 < bin_number:
		hex_reminder = bin_number % 16
		w_hex.append(hex_reminder)
		bin_number = bin_number/ 16
	for n,i in enumerate(w_hex):
		if i==10:
			w_hex[n]='A'
		elif i==11:
			w_hex[n]='B'
		elif i==12:
			w_hex[n]='C'
		elif i==13:
			w_hex[n]='D'
		elif i==14:
			w_hex[n]='E'
		elif i==15:
			w_hex[n]='F'
	y = ''.join( map( str, reversed(w_hex) ))
	print 'Hex number is \t\t%s' % y
	print '-----------------------------------------------'
	w_bin = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2028, 4096, 8192, 16384, 32768, 65536]
	dec_bin = []
	for x in w_bin:
		if number > x:
			dec_bin.append(x)
	#print dec_bin
	for k in reversed(dec_bin):
		rem_bin = number - k
		#print dec_bin.index(k)
		if rem_bin  > 0:
			h = 1
			new_num = rem_bin - k
		#print '%s - %s = %s' % (number, k, rem_bin)
		#print p
	bStr = ''
	while number > 0:
		bStr = str(number % 2) + bStr
	number = number >> 1
	return bStr
age = int(input("Insert decimal number: "))
fromDectoOctHex(age)