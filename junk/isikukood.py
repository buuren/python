isikukood = raw_input("Enter txt file location: ")
print "you entered ", isikukood
txt_path = isikukood

read_txt = open(txt_path)
for line in read_txt:
	sugu = line[0]
	
	if sugu == "3":
		sugu_out = "mees"
		vek_out = "19"
	if sugu == "4":
		sugu_out = "naine"
		vek_out = "19"
	if sugu == "5":
		sugu_out = "mees"
		vek_out = "20"
	if sugu == "6":
		sugu_out = "naine"
		vek_out = "20"
	
	desjat_out = line[1]
	god_out = line[2]
	year = '%s%s%s' % (vek_out,desjat_out,god_out)
	
	mesjac_1 = line[3]
	mesjac_2 = line[4]
	mesjac = '%s%s' % (mesjac_1, mesjac_2)
	
	den_1 = line[5]
	den_2 = line[6]
	den = '%s%s' % (den_1,den_2)
	
	data = '%s.%s.%s' % (den, mesjac, year)
	result = '%s - %s - %s' % (line, data, sugu_out)
	
	print result.replace("\n", "")

