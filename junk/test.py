import urllib2
import re


response = urllib2.urlopen('http://www.molten-wow.com')
html = response.read(20000)


a = re.finditer('<span style="padding-left:4px;">(.+?)</span></p><div class="counter" style="width:118px;text-align:center;">', html)
b = re.finditer('<div class="players"><span>(.+?)</span>', html)
c = re.finditer('<span class="infoL">Experience rates:</span>(.+?)</div>', html)
d = re.finditer('<div class="infoR"><span class="infoL">Uptime:</span>(.+?)<br /><span class="infoL">', html)


for realm, players, uptime, rates in map(None, a, b, d, c):
	if "color:#ffcc00" in players.group(1):
		line = players.group(1)
		newplayers = line.replace('<span style="color:#ffcc00;">', '')
	else:
		newplayers = players.group(1)
	
	line_rates = rates.group(1)
	new_rates = line_rates.replace(' ', '')
	
	print realm.group(1), "\t", newplayers, "\t", "Uptime: ", uptime.group(1), "\t", new_rates