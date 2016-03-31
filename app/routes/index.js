var express = require('express');
var passport = require('passport');
var router = express.Router();
var mongoose = require('mongoose');
var Edge = mongoose.model('Edge');
var Account = mongoose.model('Account');
var AccountDetail = mongoose.model('AccountDetail');
var async = require('async');
var etsy = require('./etsyAPI');
var pyTags = require('./pyTags');
var queries = require('./queries');

function loggedIn(req, res, next) {
    if (req.user) {
        next();
    } else {
        res.redirect('/login');
    }
}

function loggedInBool(req) {
    if (req.user) {
        return true
    } else {
        return false
    }
}

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { auth: loggedInBool(req), title: 'Express' });
});

/* Authentication routes */
router.get('/register', function(req, res) {
    res.render('register', {auth: loggedInBool(req), info: "" });
});

router.post('/register', function(req, res) {
    Account.register(new Account({ username : req.body.username }), req.body.password, function(err, account) {
        if (err) {
            return res.render("register", {auth: loggedInBool(req), info: "Sorry. That username already exists. Try again."});
        }

        //create new model
        var accountDetail = new AccountDetail(
          {
            username: req.body.username, 
            email: req.body.email, 
            shopID: req.body.shopID
          });

        //save model to MongoDB
        accountDetail.save(function (err) {
          if (err) {
            // DELETE record from account collection
            return err;
          }
          else {
            console.log("Post saved");
          }
        });

        passport.authenticate('local')(req, res, function () {
          res.redirect('/');
        });
    });
});

router.get('/login', function(req, res) {
    res.render('login', { auth: loggedInBool(req), user : req.user });
});

router.post('/login', passport.authenticate('local'), function(req, res) {
    res.redirect('/');
});

router.get('/logout', loggedIn, function(req, res) {
    req.logout();
    res.redirect('/');
});

router.get('/ping', loggedIn, function(req, res){
    res.status(200).send("pong!");
});

/* Application routes */

// router.get('/tag', function(req, res, next) {
//   res.render('search', { title: 'Tag Search', action: '/tag' });
// });

// router.post('/tag', function (req, res) {
//   var tag = req.body.tag;
//   console.log('This is the data: ', req.body);
//   console.log('This is the tag: ', tag);

//   pyTags.getTags(tag, function(err, t) {
//     res.send(t);
//     console.log("DONE")
//   });
// });

router.get('/search', loggedIn, function(req, res, next) {
  res.render('search', { auth: loggedInBool(req), title: 'Keyword Search', action: '/search' });
});

router.post('/search', loggedIn, function (req, res) {
  var tag = req.body.tag;
  console.log('This is the data: ', req.body);
  console.log('This is the tag: ', tag);

  pyTags.getKeywords(tag, function(err, t) {
    res.send(t);
    console.log("DONE")
  });
});

router.get('/edge', loggedIn, function(req, res, next) {
	var listingArray = [];
  queries.getShopID(req.user.username, function(err, shopID) {
    if (err) return handleError(err);
    var query  = Edge.where({ relatedShops: shopID });
  // var query  = Edge.where({ relatedShops: req.params.shopid });
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
            auth: loggedInBool(req),
            pageTitle: "Trending",
            pageDescription: "Recent activity of customers that liked your listings...",
            listingArray: listingArray
    			});
        });
      }	
    }).limit(5).sort({create_date: -1});
  });
});

router.get('/popular', loggedIn, function(req, res, next) {
	var listingArray = [];
  queries.getShopID(req.user.username, function(err, shopID) {
    if (err) return handleError(err);

    Edge.aggregate()
    	.match({"relatedShops": shopID, "shopID": {$ne: shopID}})
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
                num_favorers: listings[i].num_favorers
              });
    			  }
    			  res.render('popular',{
              auth: loggedInBool(req),
              pageTitle: "Popular",
              pageDescription: "People who favor your products, also favor...",
              listingArray: listingArray
            });
          });
        }	
      });
  });
});

module.exports = router;
