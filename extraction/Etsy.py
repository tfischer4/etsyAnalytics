
# coding: utf-8

# In[1]:

import urllib2, json, getpass, time
from pymongo import MongoClient
from pprint import pprint
import numpy as np
from datetime import date, timedelta, datetime

def getJson(uri, opener, proxyFlag):
    global apiCnt
    apiCnt = apiCnt + 1
    
    time.sleep( .1 )

    if proxyFlag == 1:
        try:
            response = opener.open(uri)
            return json.loads(response.read())
        except urllib2.HTTPError, e:
            return None
    else:
        try:
            response = urllib2.urlopen(uri)
            return json.loads(response.read())
        except urllib2.HTTPError, e:
            return None

# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/favoritelisting)
# findAllListingFavoredBy

#def getListingsFavoredBy(baseURI, listingID, apiKey, limit, offset, opener, proxyFlag):
def getListingsFavoredBy(apiParams):
    uri = str(apiParams['baseURI'] + 
        '/listings/' + str(apiParams['key']) + 
        '/favored-by?api_key=' + apiParams['apiKey'] + 
        "&limit=" + str(apiParams['limit']) + 
        "&offset=" + str(apiParams['offset']))
    return getJson(uri, apiParams['opener'], apiParams['proxyFlag'])

# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/favoritelisting)
# findAllUserFavoriteListings
def getUserFavoriteListings(apiParams):
    uri = str(apiParams['baseURI'] + 
        '/users/' + str(apiParams['key']) + 
        '/favorites/listings?api_key=' + apiParams['apiKey'] + 
        "&limit=" + str(apiParams['limit']) + 
        "&offset=" + str(apiParams['offset']))
    
    return getJson(uri, apiParams['opener'], apiParams['proxyFlag'])


def getEdges(users, minDate, apiParams):
    edges = []

    j = 0
    for key in users:
        count = 1
        offset = 0
        dtBool = True
        while (offset < count):
            #data = getUserFavoriteListings(baseURI, key, apiKey, limit, offset, opener, proxyFlag)
            apiParams['key'] = key
            apiParams['offset'] = offset
            data = getUserFavoriteListings(apiParams)
            if data is None: break

            if apiCnt % 100 == 0: print str(apiCnt) +" "+ str(len(users)) 
            
            count = data["count"]
            if count >= 1000:
                j = j - 1
                break
                
            effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))

            for i in range(0,effective_limit):
                edge = {}
                if "listing_id" in data["results"][i] and "create_date" in data["results"][i]:
                    if datetime.fromtimestamp(data["results"][i]["create_date"]).date() > minDate:
                        edge = data["results"][i]
                        edge['relatedShops'] = []
                        edge['shopID'] = None
                        edges.append(edge)
                    else:
                        dtBool = False
                        break

            if dtBool:
                offset = offset + limit
            else:
                break
            
        j = j + 1
    return edges

def updateEdges(db):
    shops = db.shops.aggregate([{"$group": {"_id": "$shopID", "listings": {"$push": "$listings.listingID"}}}])
    shops = list(shops)

    for s in shops:
        shopID = s['_id']
        db.edges.update_many(
            {'listing_id': {'$in': s['listings'][0]}},
            {'$set': {'shopID': shopID}}
        )
        users = db.edges.distinct("user_id", {"shopID": shopID})
        for u in users:
            db.edges.update_many(
                {'user_id': u, 'shopID': {'$ne': shopID}},
                {'$addToSet': {'relatedShops': shopID}}
            )

# Set default parameters for script
apiKey = 'l1g165k002v7w3gtzaa683qp'
apiCnt = 0
baseURI = 'https://openapi.etsy.com/v2'
myShopID = 9816366
limit = 100
offset = 0
count = 1
favorsMin = 0
minDate = date.today() - timedelta(days=180)
maxCreateDt = minDate


# Configure proxy
userNm = 'tfische'
passWd = getpass.getpass()
opener = urllib2.build_opener(urllib2.ProxyHandler({'https': 'https://tfische:' + passWd + '@proxy-newyork.aexp.com:8080'}))
proxyFlag = 1;

# Set default parameters for API
apiParams = {
    'baseURI': baseURI, 
    'key': None, 
    'apiKey': apiKey, 
    'limit': limit, 
    'offset': offset, 
    'opener': opener, 
    'proxyFlag': proxyFlag
    }

# Initialize Mongodb
client = MongoClient('localhost', 27017)
db = client.etsy


# Get existing listings
myListings = []
cursor = db.shops.distinct("listings.listingID", {})
myListings = list(cursor)

# Get existing user ids from edges
existingUsers = set(db.edges.distinct("user_id", {}))

# Get max create date from edges
results = db.edges.aggregate([{"$group": {"_id": "null", "value": {"$max": "$create_date"}}}])
for r in results:
    maxCreateDt = datetime.fromtimestamp(r['value']).date()


print "Get all new and existing users"
users = set()
for key in myListings:
    count = 1
    offset = 0
    dtBool = True
    while (offset < count):
        #data = getListingsFavoredBy(baseURI, key, apiKey, limit, offset, opener, proxyFlag)
        apiParams['key'] = key
        apiParams['offset'] = offset
        data = getListingsFavoredBy(apiParams)

        if apiCnt % 50 == 0: print str(apiCnt) + " " + str(len(users))      
    
        count = data["count"]
        effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))

        for i in range(0,effective_limit):
            if "user_id" in data["results"][i] and "create_date" in data["results"][i]:
                if datetime.fromtimestamp(data["results"][i]["create_date"]).date() > maxCreateDt:
                    users.add(data["results"][i]["user_id"])
                else:
                    dtBool = False
                    break
            
        if dtBool: 
            offset = offset + limit
        else:
            break

newUsers = users.difference(existingUsers)
users = users.union(existingUsers)

print "Get all edges"
edges = []
edges = getEdges(existingUsers, maxCreateDt, apiParams)
edges = edges + getEdges(newUsers, minDate, apiParams)


#Load edges into mongoDB
print "Load edges into database"
# for e in edges:
#     results = db.edges.update_one(
#         {'$and': [{"listing_id": e['listing_id']}, {"user_id": e['user_id']}]},
#         {'$setOnInsert': {
#             "listing_id": e['listing_id'],
#             "create_date": e['create_date'],
#             "shopID": e['shopID'],
#             "listing_state": e['listing_state'],
#             "user_id": e['user_id'],
#             "relatedShops": e['relatedShops']
#             }
#         },
#         upsert = True
#     )
#     if results.upserted_id is None:
#         db.edges.update_one(
#             {'$and': [{"listing_id": e['listing_id']}, {"user_id": e['user_id']}]},
#             {'$set': {
#                 "create_date": e['create_date'],
#                 "shopID": e['shopID'],
#                 "listing_state": e['listing_state']
#                 }
#             },
#             {'$addToSet': {"relatedShops": e['relatedShops']}}
#         )
db.edges.insert(edges)

print "Update edges"
updateEdges(db)
exit()
