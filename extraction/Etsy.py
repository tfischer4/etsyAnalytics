
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

dateMin = date.today() - timedelta(days=180)


# In[3]:

userNm = 'tfische'
passWd = getpass.getpass()
opener = urllib2.build_opener(urllib2.ProxyHandler({'https': 'https://tfische:' + passWd + '@proxy-newyork.aexp.com:8080'}))
proxyFlag = 1;


# In[4]:

client = MongoClient('localhost', 27017)
db = client.etsy


# In[5]:

def getJson(uri, opener, proxyFlag):
    global apiCnt
    apiCnt = apiCnt + 1
    
    if proxyFlag == 1:
        response = opener.open(uri)
        return json.loads(response.read())
    else:
        response = urllib2.urlopen(uri)
        return json.loads(response.read())


# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/shop)
# getShop

# In[6]:

def getShop(baseURI, shopID, apiKey, opener, proxyFlag):
    uri = baseURI + '/shops/' + str(shopID) + '?api_key=' + apiKey
    return getJson(uri, opener, proxyFlag)


# In[7]:

from collections import OrderedDict
shopDict = OrderedDict()
data = getShop(baseURI, myShopID, apiKey, opener, proxyFlag)
#Add error handling for not finding shop

shopDict['shopID'] = data['results'][0]['shop_id']
shopDict['listings'] = []
#Maybe add more attributes in the future if needed


# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/listing)
# findAllShopListingsActive
# 

# In[8]:

def getShopListings(baseURI, shopID, apiKey, limit, offset, opener, proxyFlag):
    uri = baseURI + '/shops/' + str(shopID) + '/listings/active?api_key=' + apiKey + "&limit=" + str(limit) + "&offset=" + str(offset)
    return getJson(uri, opener, proxyFlag)


# In[9]:

myListings = {}
offset = 0
count = 1
while (offset < count):
    data = getShopListings(baseURI, myShopID, apiKey, limit, offset, opener, proxyFlag)
    #pprint(data)

    count = data["count"]
    effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))

    for i in range(0,effective_limit):
        if "listing_id" in data["results"][i]:
            if data["results"][i]["num_favorers"] >= favorsMin:
                myListings[data["results"][i]["listing_id"]] = data["results"][i]["num_favorers"]
                shopDict['listings'].append({"listingID": data["results"][i]["listing_id"], 
                                        "createDt": data["results"][i]["original_creation_tsz"],
                                        "modifyDt": data["results"][i]["last_modified_tsz"],
                                        "tags": data["results"][i]["tags"]})
    offset = offset + limit


# In[10]:

#Load shopDict into mongoDB
db.shops.count()
db.shops.insert_one(shopDict)
db.shops.count()
db.shops.find_one({"shopID": myShopID})


# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/favoritelisting)
# findAllListingFavoredBy

# In[11]:

def getListingsFavoredBy(baseURI, listingID, apiKey, limit, offset, opener, proxyFlag):
    uri = baseURI + '/listings/' + str(listingID) + '/favored-by?api_key=' + apiKey + "&limit=" + str(limit) + "&offset=" + str(offset)
    return getJson(uri, opener, proxyFlag)


# In[12]:

users = set()
for key in myListings:
    count = 1
    offset = 0
    while (offset < count):
        data = getListingsFavoredBy(baseURI, key, apiKey, limit, offset, opener, proxyFlag)
        #pprint(data)
        if apiCnt % 50 == 0: print str(apiCnt) + " " + str(len(users))
      
    
        count = data["count"]
        effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))

        for i in range(0,effective_limit):
            if "user_id" in data["results"][i] and "create_date" in data["results"][i]:
                if datetime.fromtimestamp(data["results"][i]["create_date"]).date() > dateMin:
                    users.add(data["results"][i]["user_id"])
            
        offset = offset + limit


# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/favoritelisting)
# findAllUserFavoriteListings

# In[13]:

def getUserFavoriteListings(baseURI, userID, apiKey, limit, offset, opener, proxyFlag):
    uri = baseURI + '/users/' + str(userID) + '/favorites/listings?api_key=' + apiKey + "&limit=" + str(limit) + "&offset=" + str(offset)
    return getJson(uri, opener, proxyFlag)


# In[17]:

userFavorites = []
edges = []
#listings = set()
from collections import defaultdict
listings = defaultdict(int)
j = 0
for key in users:
    count = 1
    offset = 0
    userFavorites.insert(j, {'user_id':key})
    while (offset < count):
        data = getUserFavoriteListings(baseURI, key, apiKey, limit, offset, opener, proxyFlag)
        #pprint(data)
        if apiCnt % 100 == 0: print str(apiCnt) +" "+ str(len(users)) +" "+ str(len(userFavorites))
        
        count = data["count"]
        if count >= 1000:
            j = j - 1
            break
            
        effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))

        for i in range(0,effective_limit):
            edge = {}
            if "listing_id" in data["results"][i] and "create_date" in data["results"][i]:
                if datetime.fromtimestamp(data["results"][i]["create_date"]).date() > dateMin:
                    userFavorites[j][data["results"][i]["listing_id"]] = 1
                    #listings.add(data["results"][i]["listing_id"])
                    listings[data["results"][i]["listing_id"]] += 1
                    edge = data["results"][i]
                    edge['relatedShops'] = [myShopID]
                    if edge['listing_id'] in myListings.keys():
                        edge['shopID'] = myShopID
                    else: edge['shopID'] = None
                    edges.append(edge)
            
        offset = offset + limit
        
    j = j + 1


# In[18]:

#Load edges into mongoDB
db.edges.count()
db.edges.insert_many(edges)
db.edges.count()


# In[19]:

db.edges.find_one()


# In[ ]:

print len(listings)
sortedListings = sorted(listings, key=listings.get, reverse=True)


# In[ ]:

z = myListings.keys()
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



