var express = require('express');
var passport = require('passport');
var router = express.Router();
var mongoose = require('mongoose');
var Edge = mongoose.model('Edge');
var Account = mongoose.model('Account');
var AccountDetail = mongoose.model('AccountDetail');
var Prospect = mongoose.model('Prospect');
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

function getListings(err, edges, _callBack) {
  if (err) return handleError(err);
  if (edges) {
    // doc may be null if no document matched
    var listingArray = [];
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
          num_favorers: listings[i].num_favorers
        });
      }
      _callBack(null, listingArray);
    });
  } 
}

function renderPopular(req, res, page, _callBack){
  var offset = parseInt(page) * 5;
  queries.getShopID(req.user.username, function(err, shopID) {
    if (err) return handleError(err);

    Edge.aggregate()
      .match({"relatedShops": shopID, "shopID": {$ne: shopID}})
      .group({listing_id: "$listing_id", count: { $sum: 1 }})
      .sort({count: -1})
      .skip(offset)
      .limit(5)
      .exec(function (err, edges) {
        getListings(err, edges, function (err, listingArray) {
          if (err) return handleError(err);
          _callBack(null, listingArray);
        });
      });
  });
}

function renderTrending(req, res, page, _callBack){
  var offset = parseInt(page) * 5;
  queries.getShopID(req.user.username, function(err, shopID) {
    if (err) return handleError(err);
    var query  = Edge.where({ relatedShops: shopID });
    query.find(function (err, edges) {
      if (err) return handleError(err);
      if (edges) {
        getListings(err, edges, function (err, listingArray) {
          if (err) return handleError(err);
          _callBack(null, listingArray);
        });
      }
    }).limit(5).sort({create_date: -1}).skip(offset);
  });
}


/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { auth: loggedInBool(req), title: 'Express' });
});

/* Request access page */
router.get('/request', function(req, res, next) {
  res.render('request', { auth: loggedInBool(req) });
});

router.post('/request', function(req, res) {
  //create new model
  var prospect = new Prospect(
    {
      name: req.body.name, 
      email: req.body.email
    });

  //save model to MongoDB
  prospect.save(function (err) {
    if (err) {
      // DELETE record from account collection
      return err;
    }
    else {
      console.log("Post saved");
      res.redirect('/thanks');
    }
  });
});

router.get('/thanks', function(req, res) {
    res.render('thanks', {auth: loggedInBool(req) });
});

/* Authentication routes */
router.get('/register', loggedIn, function(req, res) {
    res.render('register', {auth: loggedInBool(req), info: "" });
});

router.post('/register', loggedIn, function(req, res) {
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
    res.redirect('/search');
});

router.get('/logout', loggedIn, function(req, res) {
    req.logout();
    res.redirect('/');
});

router.get('/search', loggedIn, function(req, res, next) {
  res.render('search', { auth: loggedInBool(req), title: 'Tag Optimization', action: '/search' });
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
  renderTrending(req, res, 0, function (err, listingArray) {
    res.render('popular',
		{
      auth: loggedInBool(req),
      pageTitle: "Trending",
      action: '/edge',
      pageDescription: "Recent activity of customers that liked your listings...",
      listingArray: listingArray
		});
  });
});	

router.post('/edge', loggedIn, function (req, res) {
  var page = req.body.page;
  renderTrending(req, res, page, function(err, listingArray) {
    res.send(listingArray);
  });
});

router.get('/popular', loggedIn, function(req, res, next) {
  renderPopular(req, res, 0, function(err, listingArray) {
    res.render('popular',{
              auth: loggedInBool(req),
              pageTitle: "Popular",
              action: '/popular',
              pageDescription: "People who favor your products, also favor...",
              listingArray: listingArray
            });
  });
});

router.post('/popular', loggedIn, function (req, res) {
  var page = req.body.page;
  renderPopular(req, res, page, function(err, listingArray) {
    res.send(listingArray);
  });
});

module.exports = router;
