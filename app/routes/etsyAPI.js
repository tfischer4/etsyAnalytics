var config 	= require('config');
var apiKey 	= config.get('etsy.key');
var baseURI	= config.get('etsy.baseURI');
var axpURI 	= config.get('axpProxy.uri');
var axpFlg 	= config.get('axpProxy.flg');

var request = require("request");


module.exports = {
  getListing : function( listingID, _callBack){
	var request = require("request");

  	request({
		url: baseURI + '/listings/' + listingID,
		// proxy: axpURI,
  		qs: { api_key: apiKey, includes: 'MainImage' },
  		method: "GET",
		}, 
		function(err, response, body) {
  		if(err) { console.log(err); return; }
		// console.log(body);

		_callBack(null, JSON.parse(body).results[0]);
		}
	);
  }
};

