var mongoose = require( 'mongoose' );

var edgeSchema = new mongoose.Schema({
	_id: String,
	listing_id: Number,
	create_date: Number,
        shopID: Number,
	listing_state: String,
	relatedShops: [Number],
	user_id: Number
	},
	{collection: 'edges'}
);

var Edge = module.exports = mongoose.model('Edge', edgeSchema);

