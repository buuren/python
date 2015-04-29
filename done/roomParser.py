# -*- coding: utf-8 -*-

# https://bitbucket.org/goghAta/flatparser/src

import glob
import logging
import sys
from time import localtime, strftime
import os
from urllib import FancyURLopener, quote_plus
from lxml.html import parse
import re
import sqlite3
import time
import json
import math

class UrlOpener(FancyURLopener, object):
	version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
	pass

def delay(sleepCycleCount):
	sleepCycleWeight = 0.5 # in secs
	sleepSecondCount = sleepCycleCount * sleepCycleWeight
	logging.info('Delaying %f secs...' % (sleepSecondCount))
	time.sleep(sleepSecondCount)

def getFlatLocation(flatPageName, flatAddress, mode, geoDBCursor):
	logging.info('Retrieving geo code info for flat \'%s\' (mode \'%s\')...' % (flatPageName, mode))
	flatFullAddress = (flatBaseAddress + flatAddress).encode('utf8')
	
	geoCodeResult = ''
	isGeoCodeResultCached = 1
	geoDBCursor.execute("SELECT geoCode FROM %s WHERE address = ?" % ("GeoG" if mode == 'G' else "GeoY"), (flatFullAddress,))
	geoCodeResultRow = geoDBCursor.fetchone()
	if geoCodeResultRow is not None:
		geoCodeResult = geoCodeResultRow[0]

	if geoCodeResult is None or len(geoCodeResult) == 0:
		isGeoCodeResultCached = 0
		geoCodeURL = ('http://maps.google.com/maps/api/geocode/json?sensor=false&address=' if mode == "G" else 'http://geocode-maps.yandex.ru/1.x/?format=json&geocode=') + quote_plus(flatFullAddress)
		urlOpener = UrlOpener()
		geoCodeResult = urlOpener.open(geoCodeURL).read()

	if geoCodeResult is None:
		geoCodeResult = ''

	logging.info('Geo code result for flat \'%s\' was fetched (mode \'%s\', from cache - %d)' % (flatPageName, mode, isGeoCodeResultCached))

	flatLocation = 0
	geoCodeJson = json.loads(geoCodeResult)
	if geoCodeJson is not None and (len(geoCodeJson['results']) if mode == 'G' else len(geoCodeJson['response'])):
		if isGeoCodeResultCached == 0:
			geoDBCursor.execute("INSERT INTO %s VALUES (?, ?)" % ("GeoG" if mode == 'G' else "GeoY"), (flatFullAddress, geoCodeResult))
		if mode == "G":
			geoCodeLocation = geoCodeJson['results'][0]['geometry']['location']
			flatLocation = {'lat': float(geoCodeLocation['lat']), 'lng': float(geoCodeLocation['lng'])}
		else:
			geoCodeLocation = geoCodeJson['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
			(flatLocationLng, flatLocationLat) = re.search('(.*) (.*)', geoCodeLocation).group(1, 2)
			flatLocation = {'lat': float(flatLocationLat), 'lng': float(flatLocationLng)}
		
		logging.info('Geo code info for flat \'%s\' was retrieved (mode \'%s\')' % (flatPageName, mode))
	else:
		logging.warning('Geo code info for flat \'%s\' was NOT retrieved (mode \'%s\')' % (flatPageName, mode))

	return (flatLocation, isGeoCodeResultCached)

def calculateDistance(location1, location2):
	# haversine formula, see http://www.movable-type.co.uk/scripts/latlong.html for details
	R = 6371 * 1000 # Radius of the Earth in m
	dLat = (location2['lat'] - location1['lat']) * (math.pi / 180)
	dLng = (location2['lng'] - location1['lng']) * (math.pi / 180) 
	a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(location1['lat'] * (math.pi / 180)) * math.cos(location2['lat'] * (math.pi / 180)) * math.sin(dLng / 2) * math.sin(dLng / 2) 
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = R * c
	return d

def getFlatDistanceInfo(flatLocation):
	flatSubwayStationDistances = map(lambda subwayStationInfo: calculateDistance(flatLocation, subwayStationInfo['location']), subwayStationInfos)
	flatNearestSubwayStationDistance = min(flatSubwayStationDistances)
	flatNearestSubwayStationName = subwayStationInfos[flatSubwayStationDistances.index(flatNearestSubwayStationDistance)]['name']
	flatTownCenterDistance = flatSubwayStationDistances[0]
	return (flatNearestSubwayStationName, flatNearestSubwayStationDistance, flatTownCenterDistance)

rootWorkingDirectoryPath = os.getcwd() + '/FP/'
rootWorkingDirectoryPath = rootWorkingDirectoryPath.replace("\\", "/")

workingDirectoryPath = ''
#workingDirectoryPath = 'F:/Work/_Projects/4Fun/FlatParser/FP/16.03.2013 15-35-11/'

flatsDeepParseMode = 1
geoCodeFetchMode = 1
flatPriceParseThreshold = 100

flatsPageContentMinimumAllowedLength = 80 * 1024
flatsPageDownloadAttemptMaximumCount = 5

flatPageContentMinimumAllowedLength = 20 * 1024
flatPageDownloadAttemptMaximumCount = 5

subwayStationInfos = [
	# Center of town, should be the first element in array
	{'name': u'Октябрьская', 'location': {'lat': 53.9018129, 'lng': 27.5607115}},

	{'name': u'Спортивная', 'location': {'lat': 53.9084306, 'lng': 27.4793762}},
	{'name': u'Фрунзенская', 'location': {'lat': 53.9056244, 'lng': 27.5378537}},
	{'name': u'Якуба Коласа пл.', 'location': {'lat': 53.9153569, 'lng': 27.5828397}},
	{'name': u'Борисовский тракт', 'location': {'lat': 53.9388635, 'lng': 27.6670396}},
	{'name': u'Московская', 'location': {'lat': 53.9279837, 'lng': 27.6278204}},
	{'name': u'Первомайская', 'location': {'lat': 53.8936547, 'lng': 27.5701582}},
	{'name': u'Восток', 'location': {'lat': 53.9344835, 'lng': 27.6513112}},
	{'name': u'Могилевская', 'location': {'lat': 53.8623126, 'lng': 27.674346}},
	{'name': u'Автозаводская', 'location': {'lat': 53.8690346, 'lng': 27.6474166}},
	{'name': u'Уручье', 'location': {'lat': 53.94535219999999, 'lng': 27.687875}},
	{'name': u'Победы пл.', 'location': {'lat': 53.9091227, 'lng': 27.5747555}},
	{'name': u'Молодежная', 'location': {'lat': 53.9064619, 'lng': 27.5213796}},
	{'name': u'Парк Челюскинцев', 'location': {'lat': 53.9241648, 'lng': 27.6133633}},
	{'name': u'Кунцевщина', 'location': {'lat': 53.9065756, 'lng': 27.4545872}},
	{'name': u'Немига', 'location': {'lat': 53.9054617, 'lng': 27.5544432}},
	{'name': u'Пролетарская', 'location': {'lat': 53.8896343, 'lng': 27.5856077}},
	{'name': u'Пушкинская', 'location': {'lat': 53.9095682, 'lng': 27.4985433}},
	{'name': u'Институт культуры', 'location': {'lat': 53.8864055, 'lng': 27.53721}},
	{'name': u'Партизанская', 'location': {'lat': 53.8768861, 'lng': 27.6268709}},
	{'name': u'Каменная горка', 'location': {'lat': 53.9073688, 'lng': 27.4351037}},
	{'name': u'Ленина пл.', 'location': {'lat': 53.8926937, 'lng': 27.5477886}},
	{'name': u'Академия наук', 'location': {'lat': 53.9211795, 'lng': 27.5977689}},
	{'name': u'Тракторный завод', 'location': {'lat': 53.889564, 'lng': 27.6156753}},
	{'name': u'Грушевка', 'location': {'lat': 53.886617, 'lng': 27.51454}},
	{'name': u'Михалово', 'location': {'lat': 53.877179, 'lng': 27.496664}},
	{'name': u'Петровщина', 'location': {'lat': 53.864256, 'lng': 27.484763}},
	{'name': u'Малиновка', 'location': {'lat': 53.849539, 'lng': 27.474661}}
]

flatBaseAddress = u'Беларусь, Минск, '

workingDirectoryNamePattern = '.+/(\d+\.\d+\.\d+ \d+\-\d+\-\d+)'
workingDirectoryNameFormat = '%d.%m.%Y %H-%M-%S'

flatsReparseMode = 0
if len(workingDirectoryPath) == 0:
	flatsReparseMode = 0
	workingDirectoryPath = rootWorkingDirectoryPath + strftime(workingDirectoryNameFormat, localtime()) + '/'
	os.makedirs(workingDirectoryPath)
else:
	flatsReparseMode = 1

workingDirectoryPaths = glob.glob(rootWorkingDirectoryPath + '*')
workingDirectoryPaths = map(lambda x: x.replace("\\", "/"), workingDirectoryPaths)
workingDirectoryPaths = filter(lambda x: re.match(workingDirectoryNamePattern, x), workingDirectoryPaths)
workingDirectoryPaths = map(lambda x: x + '/', workingDirectoryPaths)
workingDirectoryPaths = filter(lambda x: x != workingDirectoryPath, workingDirectoryPaths)
workingDirectoryPaths.sort(key = lambda x: time.strptime(re.search(workingDirectoryNamePattern, x).group(1), workingDirectoryNameFormat), reverse = True)

oldWorkingDirectoryPath = ''
if len(workingDirectoryPaths):
	oldWorkingDirectoryPath = workingDirectoryPaths[0]

logFormat = '[%(asctime)s]-%(levelname)-8s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=logFormat, filename = workingDirectoryPath + 'Log.log')
stdoutStreamHandler = logging.StreamHandler(sys.stdout)
stdoutStreamHandler.setFormatter(logging.Formatter(logFormat))
logging.getLogger('').addHandler(stdoutStreamHandler)

logging.info('FlatParser 2.4.3 started')
logging.info('Working direcory - \'%s\'' % workingDirectoryPath)
logging.info('Old working direcory - \'%s\'' % oldWorkingDirectoryPath)
logging.info('Flats reparse mode - %d' % flatsReparseMode)
logging.info('Flats deep parse mode - %d' % flatsDeepParseMode)
logging.info('Geo code fetch mode - %d' % geoCodeFetchMode)

FLATS_PAGE_INDEX_TOKEN = '{PAGE_INDEX}';

# Flats should be sorted by price (ascending)
# Minsk, 1-1 rooms
#flatsURL = 'http://realt.by/sale/flats/show/database/page/' + FLATS_PAGE_INDEX_TOKEN + '/?search=eJwryS%2FPi89MiU6NtTU1NDBSK8rPzy0G8qINY20NETwjEC%2B%2BOLWktCC6OL%2BoJD6pEqykoCgzORUmUZSaHF%2BQWhRfkJgONM7YAAD1qiE%2F'

# Minsk, 2-2 rooms
#flatsURL = 'http://realt.by/sale/flats/show/database/page/' + FLATS_PAGE_INDEX_TOKEN + '/?search=eJwryS%2FPi89MiU6NtTU1NDBSK8rPzy0G8qINY22ReEYgXnxxaklpQXRxflFJfFIlWElBUWZyKkyiKDU5viC1KL4gMR1onLEBAPYcIUE%3D'

# Minsk, 2-3 rooms
flatsURL = 'http://realt.by/sale/flats/show/database/page/' + FLATS_PAGE_INDEX_TOKEN + '/?search=eJwryS%2FPi89MiU6NtTU1NDBSK8rPzy0G8qINY22ReEaxtsZq8cWpJaUF0cX5RSXxSZVgJQVFmcmpMImi1OT4gtSi%2BILEdKBxxgYA9k4hQg%3D%3D'

# Minsk, 4-4 rooms
#flatsURL = 'http://realt.by/sale/flats/show/database/page/' + FLATS_PAGE_INDEX_TOKEN + '/?search=eJwryS%2FPi89MiU6NtTU1NDBSK8rPzy0G8qINY21NEDwjEC%2B%2BOLWktCC6OL%2BoJD6pEqykoCgzORUmUZSaHF%2BQWhRfkJgONM7YAAD3ACFF'

logging.info('Flats DB URL - \'%s\'', flatsURL)

parsedFlatTotalCount = 0

try:
	flatsPagesDirectoryPath = workingDirectoryPath + '/FlatsPages/'
	if not os.path.exists(flatsPagesDirectoryPath):
		os.makedirs(flatsPagesDirectoryPath)
		
	flatPagesDirectoryPath = workingDirectoryPath + '/FlatPages/'
	if not os.path.exists(flatPagesDirectoryPath):
		os.makedirs(flatPagesDirectoryPath)

	geoDBDirectoryPath = workingDirectoryPath + '../Geo/'
	if not os.path.exists(geoDBDirectoryPath):
		os.makedirs(geoDBDirectoryPath)

	if geoCodeFetchMode:
		geoDBFilePath = geoDBDirectoryPath + 'Geo.sqlite'
		geoDBConnection = sqlite3.connect(geoDBFilePath)
		geoDBConnection.text_factory = str
		geoDBCursor = geoDBConnection.cursor()
		geoDBCursor.execute('''CREATE TABLE IF NOT EXISTS GeoG(address text, geoCode text)''')
		geoDBCursor.execute('''CREATE TABLE IF NOT EXISTS GeoY(address text, geoCode text)''')

	flatsDBFileName = 'Flats.sqlite'
	flatsDBFilePath = workingDirectoryPath + flatsDBFileName

	oldFlatsDBFilePath = ''
	if len(oldWorkingDirectoryPath):
		oldFlatsDBFilePath = oldWorkingDirectoryPath + flatsDBFileName

	if flatsReparseMode:
		os.remove(flatsDBFilePath)
	
	flatsDBConnection = sqlite3.connect(flatsDBFilePath)
	flatsDBCursor = flatsDBConnection.cursor()
	flatsDBCursor.execute('''CREATE TABLE Flats(flatPageURL text, flatPictureCount integer, flatRoomCount integer, flatWholeRoomCount integer, flatAddress text, flatNearestSubwayStationNameG text, flatNearestSubwayStationDistanceG real, flatTownCenterDistanceG real, flatNearestSubwayStationNameY text, flatNearestSubwayStationDistanceY real, flatTownCenterDistanceY real, flatFloorNumber integer, flatFloorType text, flatHouseFloorCount integer, flatHouseType text, flatWholeSquare real, flatLivingSquare real, flatKitchenSquare real, flatBathroomInfo text, flatBalconyInfo text, flatBirthInfo text, flatSellModeInfo text, flatPriceInfo real, isFlatInfoUpdated integer, flatPriceDelta real)''')

	if len(oldFlatsDBFilePath):
		oldFlatsDBConnection = sqlite3.connect(oldFlatsDBFilePath)
		oldFlatsDBCursor = oldFlatsDBConnection.cursor()

	urlOpener = UrlOpener()

	flatsPageIndex = 1
	while 1:
		flatsPageFilePath = flatsPagesDirectoryPath + 'Page%d.html' % flatsPageIndex
		
		if not flatsReparseMode:
			########################################################
			flatsPageURL = flatsURL.replace(FLATS_PAGE_INDEX_TOKEN, '%d' % flatsPageIndex)
			for flatsPageDownloadAttemptNumber in xrange(1, flatsPageDownloadAttemptMaximumCount):
				logging.info('Downloading flats page #%d (attempt #%d)...' % (flatsPageIndex, flatsPageDownloadAttemptNumber))
				flatsPageContent = urlOpener.open(flatsPageURL).read()
				logging.info('Flats page #%d was downloaded (length - %d)' % (flatsPageIndex, len(flatsPageContent)))
				########################################################
				logging.info('Saving flats page #%d...' % flatsPageIndex)
				with open(flatsPageFilePath, "w") as flatsPageFile:
					flatsPageFile.write(flatsPageContent)
				logging.info('Flats page #%d was saved' % flatsPageIndex)
				########################################################
				if len(flatsPageContent) >= flatsPageContentMinimumAllowedLength:
					delay(1)
					break
				else:
					logging.info('Downloaded flats page is smaller than minimum allowed length %d! Reattempting...' % (flatsPageContentMinimumAllowedLength))
					delay(20 * flatsPageDownloadAttemptNumber)
			########################################################

		########################################################
		logging.info('Parsing flats page #%d...' % flatsPageIndex)
		parsedFlatCount = 0
		shouldStop = 0
		flatsPageDocument = parse(flatsPageFilePath).getroot()
		if flatsPageDocument is not None:
			flatsTables = flatsPageDocument.xpath('//*[@id="list"]')
			if flatsTables is not None and len(flatsTables) > 0:
				flatsTable = flatsTables[0]
				if flatsTable is not None:
					flatRows = flatsTable.xpath('./tr[starts-with(@class, "text-row ")]')
					if flatRows is not None and len(flatRows) > 0:
						for flatRow in flatRows:
							flatInfoCeils = flatRow.xpath('./td')

							flatPageURL = flatInfoCeils[0].xpath('./a')[0].get('href').strip()
							flatPageName = re.search('/(\d+)/$', flatPageURL).group(1) + '.html'
							flatPageFilePath = flatPagesDirectoryPath + flatPageName
							if not flatsReparseMode and flatsDeepParseMode:
								########################################################
								for flatPageDownloadAttemptNumber in xrange(1, flatPageDownloadAttemptMaximumCount):
									logging.info('Downloading flat page #%d from \'%s\' (attempt #%d)...' % ((parsedFlatTotalCount + 1), flatPageURL, flatPageDownloadAttemptNumber))
									flatPageContent = urlOpener.open(flatPageURL).read()
									logging.info('Flat page \'%s\' downloaded (length - %d)' % (flatPageName, len(flatPageContent)))
									########################################################
									logging.info('Saving flat page \'%s\'...' % flatPageName)
									with open(flatPageFilePath, "w") as flatPageFile:
										flatPageFile.write(flatPageContent)
									logging.info('Flat page \'%s\' saved' % flatPageName)
									########################################################
									if len(flatPageContent) >= flatPageContentMinimumAllowedLength:
										delay(1)
										break
									else:
										logging.info('Downloaded flat page is smaller than minimum allowed length %d! Reattempting...' % (flatPageContentMinimumAllowedLength))
										delay(20 * flatPageDownloadAttemptNumber)
								########################################################

							(flatRoomCount, flatWholeRoomCount) = map(lambda x: x.strip(), re.search('(.*)\/(.*)', flatInfoCeils[1].xpath('./strong')[0].text).group(1, 2))
							if len(flatRoomCount) == 0:
								flatRoomCount = '-1'
							if len(flatWholeRoomCount) == 0:
								flatWholeRoomCount = '-1'
                            
							flatAddress = flatInfoCeils[3].xpath('./a')[0].text.strip()
							(flatFloorNumber, flatFloorType, flatHouseFloorCount, flatHouseType) = map(lambda x: x.strip(), re.search('(\d*)(.*)\/(\d*)(.*)', flatInfoCeils[4].text).group(1, 2, 3, 4))
							if len(flatFloorNumber) == 0:
								flatFloorNumber = '-1'
							if len(flatHouseFloorCount) == 0:
								flatHouseFloorCount = '-1'

							(flatWholeSquare, flatLivingSquare, flatKitchenSquare) = map(lambda x: x.strip(), re.search('(.*)\/(.*)\/(.*)', flatInfoCeils[5].text).group(1, 2, 3))
							if len(flatWholeSquare) == 0:
								flatWholeSquare = '-1'
							if len(flatLivingSquare) == 0:
								flatLivingSquare = '-1'
							if len(flatKitchenSquare) == 0:
								flatKitchenSquare = '-1'

							flatBalconyInfo = flatInfoCeils[6].text.strip()
							flatBirthInfo = flatInfoCeils[8].text.strip()
							flatPriceInfo = flatInfoCeils[9].xpath('./strong')[0].text.strip()
							if len(flatPriceInfo) == 0:
								flatPriceInfo = '-1'

							flatPictureCount = 0
							flatBathroomInfo = 'N/A'
							flatSellModeInfo = 'N/A'
							if flatsDeepParseMode:
								########################################################
								logging.info('Parsing flat page #%d (\'%s\')...' % ((parsedFlatTotalCount + 1), flatPageName))
								flatPageDocument = parse(flatPageFilePath).getroot()
								if flatPageDocument is not None:
									flatBathroomInfoRows = flatPageDocument.xpath(u'//tr[td/text()[contains(., "Сан/узел")]]')
									if flatBathroomInfoRows is not None and len(flatBathroomInfoRows) > 0:
										flatBathroomInfoRow = flatBathroomInfoRows[0]
										if flatBathroomInfoRow is not None:
											flatBathroomInfo = flatBathroomInfoRow.xpath('./td')[1].text
									flatSellModeInfoRows = flatPageDocument.xpath(u'//tr[td/text()[contains(., "Условия продажи")]]')
									if flatSellModeInfoRows is not None and len(flatSellModeInfoRows) > 0:
										flatSellModeInfoRow = flatSellModeInfoRows[0]
										if flatSellModeInfoRow is not None:
											flatSellModeInfo = flatSellModeInfoRow.xpath('./td')[1].text
									flatPageContent = ''
									with open(flatPageFilePath, "r") as flatPageFile:
										flatPageContent = flatPageFile.read()
									try:
										flatPictureCount = flatPageContent.count('class="fancybox"', flatPageContent.index('<!-- ###SUBPART_PICTURES### start -->'), flatPageContent.rindex('<!-- ###SUBPART_PICTURES### end -->'))
									except ValueError:
										pass

							flatNearestSubwayStationNameG = 'N/A'
							flatNearestSubwayStationDistanceG = -1
							flatTownCenterDistanceG = -1
							flatNearestSubwayStationNameY = 'N/A'
							flatNearestSubwayStationDistanceY = -1
							flatTownCenterDistanceY = -1
							if geoCodeFetchMode:
								########################################################
								(flatLocationG, isGeoCodeResultCachedG) = getFlatLocation(flatPageName, flatAddress, "G", geoDBCursor)
								if flatLocationG:
									(flatNearestSubwayStationNameG, flatNearestSubwayStationDistanceG, flatTownCenterDistanceG) = getFlatDistanceInfo(flatLocationG)

								(flatLocationY, isGeoCodeResultCachedY) = getFlatLocation(flatPageName, flatAddress, "Y", geoDBCursor)
								if flatLocationY:
									(flatNearestSubwayStationNameY, flatNearestSubwayStationDistanceY, flatTownCenterDistanceY) = getFlatDistanceInfo(flatLocationY)
									
								if flatsReparseMode and (isGeoCodeResultCachedG == 0 or isGeoCodeResultCachedY == 0):
									delay(1)
								########################################################

							isFlatInfoUpdated = 0
							flatPriceDelta = 0
							if len(oldFlatsDBFilePath):
								oldFlatsDBCursor.execute('''SELECT flatPriceInfo FROM Flats WHERE flatPageURL = ? AND flatAddress = ? AND flatWholeSquare = ? AND flatLivingSquare  = ? AND flatKitchenSquare = ?''', (flatPageURL, flatAddress, flatWholeSquare, flatLivingSquare, flatKitchenSquare,))
								oldFlatInfoRow = oldFlatsDBCursor.fetchone()
								if oldFlatInfoRow is not None and oldFlatInfoRow[0] is not None:
									isFlatInfoUpdated = 1
									oldFlatPriceInfo = oldFlatInfoRow[0]
									try:
										flatPriceDelta = float(flatPriceInfo) - float(oldFlatPriceInfo)
									except ValueError:
										pass

							flatsDBCursor.execute('''INSERT INTO Flats VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % (flatPageURL, flatPictureCount, flatRoomCount, flatWholeRoomCount, flatAddress, flatNearestSubwayStationNameG, flatNearestSubwayStationDistanceG, flatTownCenterDistanceG, flatNearestSubwayStationNameY, flatNearestSubwayStationDistanceY, flatTownCenterDistanceY, flatFloorNumber, flatFloorType, flatHouseFloorCount, flatHouseType, flatWholeSquare, flatLivingSquare, flatKitchenSquare, flatBathroomInfo, flatBalconyInfo, flatBirthInfo, flatSellModeInfo, flatPriceInfo, isFlatInfoUpdated, flatPriceDelta))

							parsedFlatCount += 1
							parsedFlatTotalCount += 1
							
							try:
								if float(flatPriceInfo) > flatPriceParseThreshold:
									logging.info('Found flat\'s price (%f) greater than parse threshold (%f)! Stopping...' % (float(flatPriceInfo), flatPriceParseThreshold))
									shouldStop = 1
									break
							except ValueError:
								pass
							
		logging.info('Flats page #%d was parsed (parsed flat count - %d)' % (flatsPageIndex, parsedFlatCount))

		if parsedFlatCount == 0 or shouldStop:
			break
		########################################################

		if geoCodeFetchMode:
			geoDBConnection.commit()

		flatsDBConnection.commit()
		flatsPageIndex += 1

	if geoCodeFetchMode:
		geoDBConnection.commit()
		geoDBCursor.close()

	if len(oldFlatsDBFilePath):
		logging.info('Checking removed flats...')
		flatsDBConnection.commit()
		removedFlatCount = 0
		oldFlatsDBCursor.execute('''SELECT * FROM Flats WHERE 1=1''')
		while 1:
			oldFlatInfoRow = oldFlatsDBCursor.fetchone()
			if oldFlatInfoRow is not None and oldFlatInfoRow[0] is not None and oldFlatInfoRow[0] != 'del':
				flatsDBCursor.execute('''SELECT * FROM Flats WHERE flatPageURL = ? AND flatAddress = ? AND flatWholeSquare = ? AND flatLivingSquare  = ? AND flatKitchenSquare = ?''', (oldFlatInfoRow[0], oldFlatInfoRow[4], oldFlatInfoRow[15], oldFlatInfoRow[16], oldFlatInfoRow[17],))
				flatInfoRow = flatsDBCursor.fetchone()
				if flatInfoRow is None:
					flatsDBCursor.execute('''INSERT INTO Flats VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % ('del', oldFlatInfoRow[1], oldFlatInfoRow[2], oldFlatInfoRow[3], oldFlatInfoRow[4], oldFlatInfoRow[5], oldFlatInfoRow[6], oldFlatInfoRow[7], oldFlatInfoRow[8], oldFlatInfoRow[9], oldFlatInfoRow[10], oldFlatInfoRow[11], oldFlatInfoRow[12], oldFlatInfoRow[13], oldFlatInfoRow[14], oldFlatInfoRow[15], oldFlatInfoRow[16], oldFlatInfoRow[17], oldFlatInfoRow[18], oldFlatInfoRow[19], oldFlatInfoRow[20], oldFlatInfoRow[21], oldFlatInfoRow[22], oldFlatInfoRow[23], oldFlatInfoRow[24]))
					removedFlatCount += 1
			else:
				break
		logging.info('Removed flat count - %d' % removedFlatCount)
		oldFlatsDBCursor.close()

	flatsDBConnection.commit()
	flatsDBCursor.close()

except IOError as error:
	logging.error("I/O error '{0}': '{1}'".format(error.errno, error.strerror))
except:
	logging.error("Unexpected error: '{0}'".format(sys.exc_info()[0]))
	raise

logging.info('FlatParser stopped (parsed flat total count - %d)' % parsedFlatTotalCount)
