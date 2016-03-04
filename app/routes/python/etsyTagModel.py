#!/usr/bin/python

import sys
import urllib, urllib2, json, getpass, time
from pprint import pprint
import numpy as np
from datetime import date, timedelta, datetime

if len(sys.argv) < 2:
  print 'ERROR: Tag parameter not passed--', sys.argv
  sys.exit(2)

if len(sys.argv) > 2:
  print 'ERROR: Too many parameters passed--', sys.argv
  sys.exit(2)

pwdFile = '../../../.pwd'
with open(pwdFile) as f:
  credentials = [x.strip().split("\t") for x in f.readlines()]

for app,username,password in credentials:
  if app == 'axpProxy':
    userNm = username
    passWd = password
  if app == 'etsyAPIKey':
    apiKey = password


apiCnt = 0
baseURI = 'https://openapi.etsy.com/v2'
input = sys.argv[1]
limit = 100
offset = 0
sortOn = 'created'
sortOrder = 'up'

# AXP Proxy Details
# passWd = getpass.getpass()
opener = urllib2.build_opener(urllib2.ProxyHandler({'https': 'https://tfische:' + passWd + '@proxy-newyork.aexp.com:8080'}))
proxyFlag = 1;

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
    uri = baseURI + '/listings/active?api_key=' + apiKey + "&limit=" + str(limit) + "&offset=" + str(offset) + "&tags=" + tag + "&sort_on=" + sortOn + "&sort_order=" + sortOrder
    return getJson(uri, opener, proxyFlag)


tag = urllib.quote_plus(input)
tagsList = []
viewScore = []
rankScore = []
favorerScore = []

nbrListings = 300
j = 0
while (j < nbrListings):
    data = getListingsFromTag(baseURI, tag, apiKey, limit, offset, opener, proxyFlag)
    effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))
    for i in range(0, effective_limit):
        if "tags" in data["results"][i]:

            nbrOfTags = len(data["results"][i]["tags"])
            listOfOnes = [1] * nbrOfTags

            tagsList.append(dict(zip(map(lambda x:x.upper(),data["results"][i]["tags"]), listOfOnes)))
            rankScore.append(((data["pagination"]["effective_page"] - 1) * limit) + i + 1)
            viewScore.append(data["results"][i]["views"])
            favorerScore.append(data["results"][i]["num_favorers"])
            
    j = j + limit
    if data["count"] < j: break
    offset = offset + limit


# Convert list of dicts containing tags to a sparse matrix

from sklearn.feature_extraction import DictVectorizer
v = DictVectorizer()
X = v.fit_transform(tagsList)


# Fit a model for the rank which assumes sort_on=score is set on API request

from sklearn import linear_model
#clfRank = linear_model.Lasso(alpha = 0.1, max_iter=2000, tol=0.001)
#clfRank.fit(X, rankScore)
#sR = clfRank.coef_



# Fit a model for the number of views the listing received
# Removing for now due to convergence issues

#clfView = linear_model.Lasso(alpha = 0.1, max_iter=2000, tol=0.001)
#clfView.fit(X, viewScore)
#sV = clfView.coef_



# Fit a model for the number of Favorers the listing received

clfFavorer = linear_model.Lasso(alpha = 0.1)
clfFavorer.fit(X, favorerScore)
sF = clfFavorer.coef_


# Normalize model coefficients 0 to 1

#sRNorm = [(a - min(sR))/(max(sR)-min(sR)) for a in sR]
#sVNorm = [(a - min(sV))/(max(sV)-min(sV)) for a in sV]
sFNorm = [(a - min(sF))/(max(sF)-min(sF)) for a in sF]
#sRVF = [a*b*c for a,b,c in zip(sRNorm,sVNorm,sFNorm)]
#sRVF = [a*b for a,b in zip(sRNorm,sFNorm)]
sRVF = sFNorm

# In[60]:

A = np.squeeze(np.asarray(X.sum(axis=0)))
t = zip(v.get_feature_names(), sRVF, A) 
t = [ (a,b) for (a,b,c) in zip(v.get_feature_names(), sRVF, A) if c >= 6 ]
t.sort(key=lambda tup: tup[1],reverse=True) 

#results = {'tags': t[:min(50, len(t))]}

t = list(enumerate(t,1))

results = list(({'tag': y[0], 'score': y[1], 'rank': x}) for x, y in t[:min(50, len(t))])
print json.dumps(results)
