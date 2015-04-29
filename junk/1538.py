def time24hr(tstr): 
	min = (tstr.split(":"))[1]
	
	if "am" in tstr:
		if (tstr.split(":"))[0] == '01' or (tstr.split(":"))[0] == '1':
			hours = 01
		if (tstr.split(":"))[0] == '02' or (tstr.split(":"))[0] == '2':
			hours = 02
		if (tstr.split(":"))[0] == '03' or (tstr.split(":"))[0] == '3':
			hours = 03
		if (tstr.split(":"))[0] == '04' or (tstr.split(":"))[0] == '4':
			hours = 04
		if (tstr.split(":"))[0] == '05' or (tstr.split(":"))[0] == '5':
			hours = 05
		if (tstr.split(":"))[0] == '06' or (tstr.split(":"))[0] == '6':
			hours = 06
		if (tstr.split(":"))[0] == '07' or (tstr.split(":"))[0] == '7':
			hours = 07
		if (tstr.split(":"))[0] == '08' or (tstr.split(":"))[0] == '8':
			hours = '08'
		if (tstr.split(":"))[0] == '09' or (tstr.split(":"))[0] == '9':
			hours = '09'
		if (tstr.split(":"))[0] == '10':
			hours = 10
		if (tstr.split(":"))[0] == '11':
			hours = 11
		if (tstr.split(":"))[0] == '12':
			hours = '00'
		min = min.replace("am", "hr")
	else:
		if (tstr.split(":"))[0] == '01' or (tstr.split(":"))[0] == '1':
			hours = 13
		if (tstr.split(":"))[0] == '02' or (tstr.split(":"))[0] == '2':
			hours = 14
		if (tstr.split(":"))[0] == '03' or (tstr.split(":"))[0] == '3':
			hours = 15
		if (tstr.split(":"))[0] == '04' or (tstr.split(":"))[0] == '4':
			hours = 16
		if (tstr.split(":"))[0] == '05' or (tstr.split(":"))[0] == '5':
			hours = 17
		if (tstr.split(":"))[0] == '06' or (tstr.split(":"))[0] == '6':
			hours = 18
		if (tstr.split(":"))[0] == '07' or (tstr.split(":"))[0] == '7':
			hours = 19
		if (tstr.split(':'))[0] == '08' or (tstr.split(":"))[0] == '8':
			hours = 20
		if (tstr.split(":"))[0] == '09' or (tstr.split(":"))[0] == '9':
			hours = 21
		if (tstr.split(":"))[0] == '10':
			hours = 22
		if (tstr.split(":"))[0] == '11':
			hours = 23
		if (tstr.split(":"))[0] == '12':
			hours = 12
		min = min.replace("pm", "hr")
		
			
	print '%s%s' % (hours, min )

age = int(input("Insert decimal number: "))
time24hr(age)