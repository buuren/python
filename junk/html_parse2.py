#spellpower = 1
#haste 		= 0.98
#crit 		= 0.76
#int 		= 0.22
#spirit 	= 0.59

import urllib
import re
grand_spell_sum = grand_int_sum = grand_stam_sum = grand_hit_sum = grand_res_sum = grand_crit_sum = grand_haste_sum = grand_sp_pen_sum = grand_spi_sum = 0

grand_stamina = []
grand_intellect = []
grand_spellpower = []
grand_hitrating = []
grand_critrating = []
grand_resilience = []
grand_haste = []
grand_spellpen = []
grand_spirit = []
	
pages = ['51512', '51486']
for page in pages:
	index = (page)
	new_page = "http://wotlk.openwow.com/?item={0}".format(index)
	print "Parsing page \t", new_page
	source = urllib.urlopen(new_page)
	page = source.readlines()

	stamina = []
	intellect = []
	spellpower = []
	hitrating = []
	critrating = []
	resilience = []
	haste = []
	spellpen = []
	spirit = []
	for x in page:
		if "Stamina" in x:
			new = x.split('<br />')
			for l in new:
				if "Stamina" in l and "class" not in l:
					l = l.replace('Stamina', '')
					l = l.replace('+', '')
					l = l.replace(' ', '')
					stamina.append(l)
				if "Intellect" in l and "class" not in l:
					l = l.replace('Intellect', '')
					l = l.replace('+', '')
					l = l.replace(' ', '')
					intellect.append(l)
				if "Spirit" in l and "class" not in l:
					l = l.replace('Spirit' , '')
					l = l.replace('+', '')
					spirit.append(l)	
				if "spell power" in l:
					l = l.replace('</td></tr></table><table><tr><td><span class="q2">Equip: Improves spell power by', '')
					l = l.replace('.</span>', '')
					l = l.replace(' ', '')
					spellpower.append(l)
				try:
					if "hit rating" in l:
						l = l.replace('<span class="q2">Equip: Increases your hit rating by ', '')
						l = re.search('(.*)&nbsp;<small>(\.*)', l)
						l_ = l.group(1)
						hitrating.append(l_)
				except AttributeError:
						a = 1
				try:
					if isinstance(l, str) and "resilience" in l:
						l = l.replace('<span class="q2">Equip: Improves your resilience rating by ', '')
						l = re.search('(.*)&nbsp;<small>(\.*)', l)
						l_ = l.group(1)
						resilience.append(l_)
				except AttributeError:
						a = 1
				try:
					if isinstance(l, str) and "haste" in l:
						l = l.replace('<span class="q2">Equip: Improves haste rating by ', '')
						l = re.search('(.*)&nbsp;<small>(\.*)', l)
						l_ = l.group(1)
						haste.append(l_)
				except AttributeError:
						a = 1
				try:
					if isinstance(l, str) and "critical strike" in l:
						l = l.replace('<span class="q2">Equip: Increases your critical strike rating by ', '')
						l = re.search('(.*)&nbsp;<small>(\.*)', l)
						l_ = l.group(1)
						critrating.append(l_)
				except AttributeError:
						a = 1
				if isinstance(l, str) and "Red socket" in l:
					spellpower.append('23')
				if isinstance(l, str) and "Blue socket" in l:
					spellpower.append('12')
					spellpen.append('13')
				if isinstance(l, str) and "Yellow socket" in l:
					spellpower.append('12')
					haste.append('10')

				if isinstance(l, str) and "Socket Bonus" in l:
					print "-------------------FOUND SOCKET BONUS-------------------------------"
					if "Spell" in l:
						print "-------------------SOCKET BONUS = SPELL-------------------------------"
						l = l.replace('<span class="q0">Socket Bonus: +', '')
						l = l.replace('Spell Power</span>', '')
						spellpower.append(l)
					if "Intellect" in l:
						print "-------------------SOCKET BONUS = INTELLECT -------------------------------"
						l = l.replace('<span class="q0">Socket Bonus: +', '')
						l = l.replace('Intellect</span>', '')
						intellect.append(l)
					if "Stamina" in l:
						print "-------------------SOCKET BONUS = STAMINA-----------------------------------"
						l = l.replace('<span class="q0">Socket Bonus: +', '')
						l = l.replace('Stamina</span>', '')
						stamina.append(l)
					if "Critical" in l:
						print "-------------------SOCKET BONUS = CRITICAL-------------------------------"
						l = l.replace('<span class="q0">Socket Bonus: +', '')
						l = l.replace('Critical Strike Rating</span>', '')
						critrating.append(l)
					if "Resilience Rating" in l:
						print "-------------------SOCKET BONUS = RESILIENCE -------------------------------"
						l = l.replace('<span class="q0">Socket Bonus: +', '')
						l = l.replace('Resilience Rating</span>', '')
						resilience.append(l)
					if "Spirit" in l:
						print "-------------------SOCKET BONUS = SPIRIT -------------------------------"
						l = l.replace('<span class="q0">Socket Bonus: +', '')
						l = l.replace('Spirit</span>', '')
						spirit.append(l)

	spell_sum = int_sum = stam_sum = hit_sum = res_sum = crit_sum = haste_sum = sp_pen_sum = spi_sum = 0		
	new_spellpower = []

	for s in spellpower:
		if s.find("span") == -1:
			new_spellpower.append(s)
	for s in new_spellpower:
		spell_sum += int(s)
	for s in intellect:
		int_sum += int(s)
	for s in stamina:
		stam_sum += int(s)
	for s in hitrating:
		hit_sum += int(s)
	for s in resilience:
		res_sum += int(s)
	for s in critrating:
		crit_sum += int(s)
	for s in haste:
		haste_sum += int(s)
	for s in spellpen:
		sp_pen_sum += int(s)
	for s in spirit:
		spi_sum += int(s)
	
	print "Item Total spellpower \t", spell_sum
	grand_spellpower.append(spell_sum)
	print "Item Total intellect \t", int_sum
	grand_intellect.append(int_sum)
	print "Item Total stamina   \t", stam_sum
	grand_stamina.append(stam_sum)
	print "Item Total hit.rating \t", hit_sum
	grand_hitrating.append(hit_sum)
	print "Item Total resilience \t", res_sum
	grand_resilience.append(res_sum)
	print "Item Total crit.rating \t", crit_sum
	grand_critrating.append(crit_sum)
	print "Item Total haste \t", haste_sum
	grand_haste.append(haste_sum)
	print "Item Total spell.pen \t", sp_pen_sum
	grand_spellpen.append(sp_pen_sum)
	print "Item Total spirit     \t", spi_sum
	grand_spirit.append(spi_sum)
print ":::::::::::::::::::::::::::::::::::::::::::: CACLULATING GRAND TOTAL ::::::::::::::::::::::::::::::::::::::::::::"

for s in grand_spellpower:
	grand_spell_sum += int(s)
for s in grand_intellect:
	grand_int_sum += int(s)
for s in grand_stamina:
	grand_stam_sum += int(s)
for s in grand_hitrating:
	grand_hit_sum += int(s)
for s in grand_resilience:
	grand_res_sum += int(s)
for s in grand_critrating:
	grand_crit_sum += int(s)
for s in grand_haste:
	grand_haste_sum += int(s)
for s in grand_spellpen:
	grand_sp_pen_sum += int(s)
for s in grand_spirit:
	grand_spi_sum += int(s)

print "Grand Total spellpower \t", grand_spell_sum
print "Grand Total intellect \t", grand_int_sum
print "Grand Total stamina   \t", grand_stam_sum
print "Grand Total hit.rating \t", grand_hit_sum
print "Grand Total resilience \t", grand_res_sum
print "Grand Total critrating \t", grand_crit_sum
print "Grand Total haste \t", grand_haste_sum
print "Grand Total spell.pen \t", grand_sp_pen_sum
print "Grand Total spirit     \t", grand_spi_sum


gs = grand_spell_sum + (grand_haste_sum * 0.98) + (grand_crit_sum * 0.76) + (grand_int_sum * 0.22) + (grand_spi_sum * 0.59)

print gs

#spellpower = 1
#haste 		= 0.98
#crit 		= 0.76
#int 		= 0.22
#spirit 	= 0.59
