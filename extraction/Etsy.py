
# coding: utf-8

# In[1]:

import urllib2, json, getpass, time
from pymongo import MongoClient
from pprint import pprint
import numpy as np
from datetime import date, timedelta, datetime


# In[2]:

apiKey = 'l1g165k002v7w3gtzaa683qp'

apiCnt = 0

baseURI = 'https://openapi.etsy.com/v2'

myShopID = 9816366

limit = 100

offset = 0

count = 1

favorsMin = 0

minDate = date.today() - timedelta(days=180)


# In[3]:

userNm = 'tfische'
passWd = getpass.getpass()
opener = urllib2.build_opener(urllib2.ProxyHandler({'https': 'https://tfische:' + passWd + '@proxy-newyork.aexp.com:8080'}))
proxyFlag = 1;

apiParams = {
    'baseURI': baseURI, 
    'key': None, 
    'apiKey': apiKey, 
    'limit': limit, 
    'offset': offset, 
    'opener': opener, 
    'proxyFlag': proxyFlag
    }


client = MongoClient('localhost', 27017)
db = client.etsy

def getJson(uri, opener, proxyFlag):
    global apiCnt
    apiCnt = apiCnt + 1
    
    time.sleep( .1 )

    if proxyFlag == 1:
        response = opener.open(uri)
        return json.loads(response.read())
    else:
        response = urllib2.urlopen(uri)
        return json.loads(response.read())

# Get existing listings
myListings = []
cursor = db.shops.distinct("listings.listingID", {})
myListings = list(cursor)

# Get existing user ids from edges
existingUsers = set(db.edges.distinct("user_id", {}))

# Get max create date from edges
results = db.edges.aggregate([{"$group": {"_id": "null", "value": {"$max": "$create_date"}}}])
maxCreateDt = datetime.fromtimestamp(results.next()['value']).date()


# cursor = db.shops.aggregate([{ "$match": {"shopID": myShopID} }, { "$unwind": "$listings" }, { "$group": { "_id": "null", "value": { "$max": "$listings.modifyDt"}}}])
# cursorList = list(cursor)
# if len(cursorList) > 0:
#     dateMin = datetime.fromtimestamp(cursorList[0]['value']).date()

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

# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/favoritelisting)
# findAllUserFavoriteListings

# In[13]:

#def getUserFavoriteListings(baseURI, userID, apiKey, limit, offset, opener, proxyFlag):
def getUserFavoriteListings(apiParams):
    uri = str(apiParams['baseURI'] + 
        '/users/' + str(apiParams['key']) + 
        '/favorites/listings?api_key=' + apiParams['apiKey'] + 
        "&limit=" + str(apiParams['limit']) + 
        "&offset=" + str(apiParams['offset']))
    print uri
    # exit()
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
                        edge['relatedShops'] = [myShopID]
                        if edge['listing_id'] in myListings:
                            edge['shopID'] = myShopID
                        else: edge['shopID'] = None
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

edges = []
edges = getEdges(existingUsers, maxCreateDt, apiParams)
edges = edges + getEdges(newUsers, minDate, apiParams)

# In[18]:
#Load edges into mongoDB
for e in edges:
    results = db.edges.update_one(
        {'$and': [{"listing_id": e['listing_id']}, {"user_id": e['user_id']}]},
        {'$setOnInsert': {
            "listing_id": e['listing_id'],
            "create_date": e['create_date'],
            "shopID": e['shopID'],
            "listing_state": e['listing_state'],
            "user_id": e['user_id'],
            "relatedShops": e['relatedShops']
            }
        },
        upsert = True
    )
    if results.upserted_id is None:
        db.edges.update_one(
            {'$and': [{"listing_id": e['listing_id']}, {"user_id": e['user_id']}]},
            {'$set': {
                "create_date": e['create_date'],
                "shopID": e['shopID'],
                "listing_state": e['listing_state']
                }
            },
            {'$addToSet': {"relatedShops": e['relatedShops']}}
        )

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
                {'$addToSet': {'relatedShops': s}}
            )

updateEdges(db)
exit()

# In[ ]:

print len(listings)
sortedListings = sorted(listings, key=listings.get, reverse=True)


# In[ ]:

z = myListings
for item in sortedListings:
    if item not in z:
        print "https://www.etsy.com/listing/" + str(item) +"?nbrOfUsers="+ str(listings[item])


# In[ ]:

l = []
for item in userFavorites:
    l.append(len(item))
print reduce(lambda x, y: x + y, l) / len(l)
len(userFavorites)


# In[ ]:

from sklearn.feature_extraction import DictVectorizer
v = DictVectorizer()
X = v.fit_transform(userFavorites)

from sklearn.metrics.pairwise import cosine_similarity
for key in myListings:
    i = v.vocabulary_.get(key)
    distMatrix = cosine_similarity(X[:,i].transpose(), X.transpose())
    maxIndex = np.argmax(distMatrix)
    maxListing = v.feature_names_[maxIndex]
    print str(key) +" "+ str(maxIndex) +" "+ str(maxListing) +" "+ str(distMatrix[0,maxIndex])


# In[ ]:

print np.argmax(distMatrix)
print distMatrix.argmax(axis=0)


# In[ ]:

np.savetxt("/Users/tfische/Desktop/distMatrix.csv", distMatrix, delimiter=",")


# In[ ]:

print distMatrix.shape
maxIndex = np.argmax(distMatrix)
print v.feature_names_[maxIndex]


# In[ ]:



