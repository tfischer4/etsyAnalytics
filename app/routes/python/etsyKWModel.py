#!/usr/bin/python

import sys
import urllib, urllib2, json, getpass, time
from pprint import pprint
import numpy as np
from datetime import date, timedelta, datetime
from stop_words import get_stop_words
import re, string
import HTMLParser
html_parser = HTMLParser.HTMLParser()
stop_words = get_stop_words('en')

if len(sys.argv) < 2:
    print 'ERROR: Tag parameter not passed--', sys.argv
    sys.exit(2)

input = sys.argv[1]
baseURI = sys.argv[2]
apiKey = sys.argv[3]
proxyURI = sys.argv[4]
proxyFlag = int(sys.argv[5])

limit = 100
offset = 0
sortOn = 'score' #'created'
sortOrder = 'down' #'up'
apiCnt = 0

# AXP Proxy Details
# passWd = getpass.getpass()
opener = urllib2.build_opener(urllib2.ProxyHandler({'https': proxyURI}))

# Call Etsy API and get JSON
def getJson(uri, opener, proxyFlag):
    global apiCnt
    apiCnt = apiCnt + 1
    
    if proxyFlag == 1:
        response = opener.open(uri)
        return json.loads(response.read())
    else:
        response = urllib2.urlopen(uri)
        return json.loads(response.read())


# Etsy API request
def getListingsFromTag(baseURI, tag, apiKey, limit, offset, opener, proxyFlag):
    uri = baseURI + '/listings/active?api_key=' + apiKey + "&limit=" + str(limit) + "&offset=" + str(offset) + "&keywords=" + tag + "&sort_on=" + sortOn + "&sort_order=" + sortOrder
    return getJson(uri, opener, proxyFlag)

def cleanString(l):
    ulist = []
    for x in l:
        x = html_parser.unescape(x)
        x = x.lower()
        x = re.sub(r'[^\w\s]', ' ', x).strip()
        if (x in stop_words): continue
        ulist.append(x)
    return ulist

def find_ngrams(input_list, n):
    if n > 1:
        return set(zip(*[input_list[i:] for i in range(n)]))
    else: return set(input_list)


tag = urllib.quote_plus(input)
kwList = []
nGrams = []
viewScore = []
rankScore = []
favorerScore = []
priceList = []
idList = []

nbrListings = 300
j = 0
while (j < nbrListings):
    data = getListingsFromTag(baseURI, tag, apiKey, limit, offset, opener, proxyFlag)
    effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))
    for i in range(0, effective_limit):
        if ("title" in data["results"][i] and "description" in data["results"][i]):
            kwList = cleanString(data["results"][i]["description"].split())
            t = (find_ngrams(kwList, 1).union(find_ngrams(kwList, 2))).union(find_ngrams(kwList, 3))
            cnt = len(t)
            listOfOnes = [1] * cnt
            nGrams.append(dict(zip(t, listOfOnes)))

            rankScore.append(((float(data["pagination"]["effective_page"]) - 1) * limit) + i + 1)
            viewScore.append(float(data["results"][i]["views"]))
            favorerScore.append(float(data["results"][i]["num_favorers"]))
            priceList.append(float(data["results"][i]["price"]) / float(data["results"][i]["quantity"]))
            idList.append(str(data["results"][i]["listing_id"]))

            
    j = j + limit
    if data["count"] < j: break
    offset = offset + limit


# Convert list of dicts containing tags to a sparse matrix

from sklearn.feature_extraction import DictVectorizer
v = DictVectorizer()
X = v.fit_transform(nGrams)


# # Fit a model for the rank which assumes sort_on=score is set on API request

from sklearn import linear_model
clfFV = linear_model.Lasso(alpha = 0.1)
Y = favorerScore
#Y = [(1000 * a/b) if b > 0 else 0 for (a, b) in zip(favorerScore, viewScore)]
clfFV.fit(X, Y)
sFV = clfFV.coef_


A = np.squeeze(np.asarray(X.sum(axis=0)))
t = [ (a,b) for (a,b,c) in zip(v.get_feature_names(), sFV, A) if c >= 10 ]
t.sort(key=lambda tup: tup[1],reverse=True) 


t = list(enumerate(t,1))

minScore = min(sFV)
maxScore = max(sFV)
#results = list(({'tag': y[0], 'score': (y[1] - minScore)/(maxScore - minScore), 'rank': x}) for x, y in t[:min(50, len(t))])
#hist, edges = np.histogram(priceList)

priceHist = zip(idList, priceList)
priceHist.insert(0, ['listingID', 'price'])
viewHist = zip(idList, viewScore)
viewHist.insert(0, ['listingID', 'views'])
favHist = zip(idList, favorerScore)
favHist.insert(0, ['listingID', 'favorers'])

tags = list(({'tag': y[0], 'score': (y[1] - minScore)/(maxScore - minScore), 'rank': x}) for x, y in t[:min(50, len(t))])
priceChart = {'min': np.min(priceList), 'max': np.max(priceList), 'median': np.median(priceList), 'hist': priceHist}
viewChart = {'min': np.min(viewScore), 'max': np.max(viewScore), 'median': np.median(viewScore), 'hist': viewHist}
favChart = {'min': np.min(favorerScore), 'max': np.max(favorerScore), 'median': np.median(favorerScore), 'hist': favHist}
results = {'priceChart': priceChart, 'viewChart': viewChart, 'favChart': favChart, 'tags': tags}
print(json.dumps(results))
