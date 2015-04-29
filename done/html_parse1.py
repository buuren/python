import urllib
import re

source = urllib.urlopen('http://armory.molten-wow.com/character-profile/Chea/Ragnaros/')
page = source.readlines()
# arrays
spellpower = []
haste = []
intellect = []
spirit = []
crit_raw = []
# arrays_end

for x in page:
	new = x.split('</div>')
	for l in new:
		if 'script language="javascript"' in l:
			l = re.search('<script language="javascript" type="text/javascript">(.*)</script>', l)
			l_ = l.group(1)
			script_content = l_.split(';')
			for y in script_content:
				#print y
				if 'Strength' in y:
					y = y.replace("tab_carac[1]['Strength:'] = '", '')
					y = y.replace("'", '')
					#print y
				if 'Agility' in y:
					y = y.replace("tab_carac[1]['Agility:'] = '", '')
					y = y.replace("'", '')
					#print y
				if 'Stamina' in y:
					y = y.replace("tab_carac[1]['Stamina:'] = '", '')
					y = y.replace("'", '')
					#print y
				if 'Intellect' in y:
					y = y.replace("tab_carac[1]['Intellect:'] = '", '')
					y = y.replace("'", '')
					intellect.append(y)
				if 'Spirit' in y:
					y = y.replace("tab_carac[1]['Spirit:'] = '", '')
					y = y.replace("'", '')
					spirit.append(y)
					#print y
				if "tab_carac[2]['Hit Rating:']" in y:
					y = y.replace("tab_carac[2]['Hit Rating:'] = '", '')
					y = y.replace("'", '')
					#print y
				if 'Bonus Damage' in y:
					y = y.replace("tab_carac[4]['Bonus Damage:'] = '", '')
					y = y.replace("'", '')
					spellpower.append(y)
					#print y
				if "tab_carac[4]['Crit Chance:']" in y:
					y = y.replace("tab_carac[4]['Crit Chance:'] = ", '')
					y = y.replace("'", '')
					y = y.replace("%", '')
					crit_raw.append(y)
					#print y
				if 'Haste' in y:
					y = y.replace("tab_carac[4]['Haste Rating:'] = '", '')
					y = y.replace("'", '')
					haste.append(y)
					#print y
				if 'Resilience' in y:
					y = y.replace("tab_carac[5]['Resilience:'] = '", '')
					y = y.replace("'", '')
					#print y

#spellpower = 1
#haste 		= 0.98
#crit 		= 0.89
#int 		= 0.22
#spirit 	= 0.57
spell_sum = haste_sum = int_sum = spirit_sum = crit_sum = 0

for s in spellpower:
	spell_sum += int(s)
for s in haste:
	haste_sum += int(s)
for s in intellect:
	int_sum += int(s)
for s in spirit:
	spirit_sum += int(s)
for s in crit_raw:
	crit_sum += float(s)
	
crit_sum = crit_sum * 45.9

gs = spell_sum + haste_sum * 0.98 + int_sum * 0.22 + spirit_sum * 0.59 + crit_sum * 0.76
print gs
