import urllib, os, re
from urllib import urlretrieve
user_profile = os.environ['USERPROFILE']
wallbase_dir = user_profile + "\wallbase"

print wallbase_dir

if not os.path.exists(wallbase_dir):
	os.makedirs(wallbase_dir)
	print "Creating directory ", wallbase_dir
    
y = 2038550
while y < 2038560:
	index = (y)
	new_page = "http://wallbase.cc/wallpaper/{0}".format(index)
	print "Parsing page \t", new_page
	source = urllib.urlopen(new_page)
	page = source.readlines()
	for x in page:
		if " alt=" in x:
			try:
				x = re.search('<img src="(.*)" alt="(\.*)', x)
				link = x.group(1)
				if "ovh.net" in link:
					print "Found link ", link
					wall_name = (link.split('/'))[5]
					wallbase_dir = user_profile + "\wallbase"
					location = "%s\%s" % (wallbase_dir, wall_name )
					urlretrieve(link, location)
				else:
					print "Bad link!"
			except AttributeError:
					print "HTTP error"
	y = y + 1