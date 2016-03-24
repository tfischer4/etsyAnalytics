import urllib2, json, getpass, time
from pymongo import MongoClient
from pprint import pprint
import numpy as np
from datetime import date, timedelta, datetime


apiKey = 'l1g165k002v7w3gtzaa683qp'
apiCnt = 0
baseURI = 'https://openapi.etsy.com/v2'
myShopID = 9816366
limit = 100
offset = 0
count = 1
favorsMin = 0
dateMin = date.today() - timedelta(days=180)

userNm = 'tfische'
passWd = getpass.getpass()
opener = urllib2.build_opener(urllib2.ProxyHandler({'https': 'https://tfische:' + passWd + '@proxy-newyork.aexp.com:8080'}))
proxyFlag = 1;

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


# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/shop)
# getShop
def getShop(baseURI, shopID, apiKey, opener, proxyFlag):
    uri = baseURI + '/shops/' + str(shopID) + '?api_key=' + apiKey
    return getJson(uri, opener, proxyFlag)

from collections import OrderedDict
shopDict = OrderedDict()
data = getShop(baseURI, myShopID, apiKey, opener, proxyFlag)
#Add error handling for not finding shop

shopDict['shopID'] = data['results'][0]['shop_id']
shopDict['listings'] = []
#Maybe add more attributes in the future if needed


# [Etsy API Doc](https://www.etsy.com/developers/documentation/reference/listing)
# findAllShopListingsActive
def getShopListings(baseURI, shopID, apiKey, limit, offset, opener, proxyFlag):
    uri = baseURI + '/shops/' + str(shopID) + '/listings/active?api_key=' + apiKey + "&limit=" + str(limit) + "&offset=" + str(offset)
    return getJson(uri, opener, proxyFlag)

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
#db.shops.insert_one(shopDict)
#db.shops.find_one({"shopID": myShopID})
result = db.shops.update_one(
        {"shopID": shopDict['shopID']},
        {'$set': shopDict},
        upsert = True
    )
