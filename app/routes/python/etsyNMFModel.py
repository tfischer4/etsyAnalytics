#!/usr/bin/python

from __future__ import print_function
from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from random import shuffle
from nltk import PorterStemmer

import sys
import urllib, urllib2, json, getpass
from pprint import pprint
import numpy as np
from datetime import date, timedelta, datetime
from stop_words import get_stop_words
import re, string
import HTMLParser
html_parser = HTMLParser.HTMLParser()





query = sys.argv[1]
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



tag = urllib.quote_plus(query)
descriptions = []
listings = []

nbrListings = 300
j = 0

while (j < nbrListings):
    data = getListingsFromTag(baseURI, tag, apiKey, limit, offset, opener, proxyFlag)
    effective_limit = min(data["pagination"]["effective_limit"], len(data["results"]))
    for i in range(0, effective_limit):
        if ("title" in data["results"][i] and "description" in data["results"][i] and "price" in data["results"][i]):

            listings.append({
                'listingID': data["results"][i]["listing_id"],
                'price': (float(data["results"][i]["price"]) / float(data["results"][i]["quantity"])),
                'view': data["results"][i]["views"],
                'favorer': data["results"][i]["num_favorers"] })
            
            d = '\035'.join(data["results"][i]["tags"])
            # searchObj = re.findall( r'(?u)\w[^\035]+\035', d)
            # print(repr(d))
            # print(searchObj)
            # exit()

            # for l in data["results"][i]["tags"]:
            #     for w in l.split():
            #         stem = PorterStemmer().stem_word(w)
            #         d = d + stem + ' '

            descriptions.append(d)

            
    j = j + limit
    if data["count"] < j: break
    offset = offset + limit


n_samples = 2000
n_features = 1000
n_topics = 4
n_top_words = 15
minDF = 5
maxDF = 0.8

def print_top_words(model, feature_names, n_top_words, listings, X):
    topicNum = 1
    topics = []
    priceChart = []
    viewChart = []
    favorerChart = []
    listingIDs = []
    for topic_idx, topic in enumerate(model.components_):
        t = []
        p = []
        v = []
        f = []
        l = []
        for i in topic.argsort()[:-n_top_words - 1:-1]:
            t.append(feature_names[i])
            indices = X[:,i].nonzero()
            for y in indices[0]:
                if listings[y]['listingID'] not in l:
                    l.append(listings[y]['listingID'])
                    p.append(listings[y]['price'])
                    v.append(listings[y]['view'])
                    f.append(listings[y]['favorer'])  
     

        topics.append(t)
        if len(l) > 0:
            priceChart.append(['Topic-' + str(topicNum), np.mean(p), np.percentile(p, 25), np.percentile(p, 50), np.percentile(p, 75)])
            viewChart.append(['Topic-' + str(topicNum), np.mean(v), np.percentile(v, 25), np.percentile(v, 50), np.percentile(v, 75)])
            favorerChart.append(['Topic-' + str(topicNum), np.mean(f), np.percentile(f, 25), np.percentile(f, 50), np.percentile(f, 75)])
            listingIDs.append(l)
        topicNum += 1

    results = {
        'topics': topics, 
        'priceChart': priceChart,
        'viewChart': viewChart,
        'favorerChart': favorerChart
        #'listingIDs': listingIDs
        }
    print(json.dumps(results))


# Load the 20 newsgroups dataset and vectorize it. We use a few heuristics
# to filter out useless terms early on: the posts are stripped of headers,
# footers and quoted replies, and common English words, words occurring in
# only one document or in at least 95% of the documents are removed20

data_samples = descriptions

# Use tf-idf features for NMF.
tfidf_vectorizer = TfidfVectorizer(max_df=maxDF, min_df=minDF, #max_features=n_features,
                                   stop_words='english', analyzer='word', token_pattern=r'(?u)\w[^\035]+\035')
tfidf = tfidf_vectorizer.fit_transform(data_samples)

# Use tf (raw term count) features for LDA.
tf_vectorizer = CountVectorizer(max_df=maxDF, min_df=minDF, max_features=n_features,
                                stop_words='english')
tf = tf_vectorizer.fit_transform(data_samples)

# Fit the NMF model
nmf = NMF(n_components=n_topics, random_state=1, alpha=.2, l1_ratio=.5).fit(tfidf)

tfidf_feature_names = tfidf_vectorizer.get_feature_names()
print_top_words(nmf, tfidf_feature_names, n_top_words, listings, tfidf)

