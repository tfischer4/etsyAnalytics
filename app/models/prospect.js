var mongoose = require( 'mongoose' );

var schema = new mongoose.Schema(
	{
        name: String,
        email: String,
        createDate: { type: Date, default: Date.now },
        modifyDate: { type: Date, default: Date.now }
	},
	{
		collection: 'prospects'
	}
);

var Prospect = module.exports = mongoose.model('Prospect', schema);