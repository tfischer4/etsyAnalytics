var mongoose = require( 'mongoose' );

var schema = new mongoose.Schema(
	{
        username: String,
        email: String,
        shopID: Number,
        createDate: { type: Date, default: Date.now },
        modifyDate: { type: Date, default: Date.now }
	},
	{
		collection: 'accounts_detail'
	}
);

var AccountDetail = module.exports = mongoose.model('AccountDetail', schema);

