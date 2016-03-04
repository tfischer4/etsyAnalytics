var express = require('express');
var router = express.Router();
var mongoose = require('mongoose');
var User = mongoose.model('User'); 
var Edge = mongoose.model('Edge');
var async = require('async');
var etsy = require('./etsyAPI');
var pyTags = require('./pyTags');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});


router.get('/tag', function(req, res, next) {
  res.render('search', { title: 'Tag Search'});
});

router.post('/tag', function (req, res) {
  var tag = req.body.tag;
  console.log('This is the data: ', req.body);
  console.log('This is the tag: ', tag);

  pyTags.getTags(tag, function(err, t) {
    res.send(t);
    console.log("DONE")
  });
});

router.get('/user/:name', function(req, res, next) {
	var query  = User.where({ userName: req.params.name });
	query.findOne(function (err, user) {
	  if (err) return handleError(err);
	  if (user) {
    		// doc may be null if no document matched
		 res.render('index', { title: user.shopID });
  	  }
	});
});

router.get('/edge/:shopid', function(req, res, next) {
	console.log('call edge with shopid: ' + req.params.shopid);
	var listingArray = [];
        var query  = Edge.where({ relatedShops: req.params.shopid });
        query.find(function (err, edges) {
        	if (err) return handleError(err);
          	if (edges) {
                	// doc may be null if no document matched
			var listingIDs = [];
			var edgesLength = edges.length;
			for (var i = 0; i < edgesLength; i++) {
				listingIDs.push(edges[i].listing_id);
			}
			async.map(listingIDs, etsy.getListing, function (err, listings) {
				console.log("async complete: " + listings.toString());
				var listingsLength = listings.length;
				for (var i = 0; i < listingsLength; i++) {
					listingArray.push({title: listings[i].title,
							image: listings[i].MainImage.url_170x135,
							url: listings[i].url,
							views: listings[i].views,
							taxonomy_path: listings[i].taxonomy_path,
							num_favorers: listings[i].num_favorers});
				}
				res.render('popular',
        			{	
                			pageTitle: "Trending",
					pageDescription: "Recent activity of customers that liked your listings...",
					listingArray: listingArray
        			});
			});
          	}	
        }).limit(5).sort({create_date: -1});
});

router.get('/popular/:shopid', function(req, res, next) {
	console.log('call edge with shopid: ' + req.params.shopid);
	var listingArray = [];
        Edge.aggregate()
		.match({"relatedShops": 9816366, "shopID": {$ne: 9816366}})
		.group({_id: "$listing_id", count: { $sum: 1 }})
		.sort({count: -1})
		.limit(5)
		.exec(function (err, edges) {

        	if (err) return handleError(err);
          	if (edges) {
                	// doc may be null if no document matched
			var listingIDs = [];
			var edgesLength = edges.length;
			for (var i = 0; i < edgesLength; i++) {
				listingIDs.push(edges[i]._id);
			}
			async.map(listingIDs, etsy.getListing, function (err, listings) {
				console.log("async complete: " + listings.toString());
				var listingsLength = listings.length;
				for (var i = 0; i < listingsLength; i++) {
					listingArray.push({title: listings[i].title,
							image: listings[i].MainImage.url_170x135,
							url: listings[i].url,
							views: listings[i].views,
                                                        taxonomy_path: listings[i].taxonomy_path,
                                                        num_favorers: listings[i].num_favorers});
				}
				res.render('popular',
        			{	
                			pageTitle: "Popular",
                                        pageDescription: "People who favor your products, also favor...",
					listingArray: listingArray
        			});
			});
          	}	
        });
});

module.exports = router;
