var mongoose = require('mongoose');
var AccountDetail = mongoose.model('AccountDetail');

module.exports = {
	getShopID : function( username, _callBack) {
		var query = AccountDetail.where({username: username}).select({shopID: 1, _id: 0});
		query.findOne(function (err, results) {
			if (err) return handleError(err);
			if (results) {
				_callBack(null, results['shopID']);
			}
		});
	}
}