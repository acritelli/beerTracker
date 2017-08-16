# Imports all breweries and beers from a CSV file
# CSV file should be formatted as: Brewery, Beer 1, Beer 2, ..., Beer N
# IF brewery has no listed beer, then format: Brewery,

from pymongo import MongoClient
client = MongoClient()
db = client.beerexpo
collection = db.defBeers

f = open('flour_city_list.txt')

for line in f:
    line = line.strip('\n')
    lineArr = line.split(',')

    document = {}
    document['beers'] = []
    i = 0
    while i < len(lineArr): 
        item = lineArr[i].lstrip()
        # Remove . and $ characters from brewery and beer, since they're keys in Mongo
        item = item.replace('.', '')
        item = item.replace('$', '')
        
        if item == '':
            next

        if i == 0:
            document['name'] = item
        else:
            document['beers'].append(item)
        i += 1
    collection.insert_one(document)
