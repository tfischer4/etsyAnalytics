var request = require("request");
var apiKey = 


module.exports = {
  getListing : function( listingID, _callBack){
	var request = require("request");

  	request({
		url: 'https://openapi.etsy.com/v2/listings/' + listingID,
		proxy: 'http://tfische:January16@proxy-newyork.aexp.com:8080',
  		qs: { api_key: apiKey, includes: 'MainImage' },
  		method: "GET",
		}, function(err, response, body) {
  		if(err) { console.log(err); return; }
		console.log(body);

		_callBack(null, JSON.parse(body).results[0]);
	});
  }
};

