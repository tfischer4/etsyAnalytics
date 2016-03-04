var mongoose = require( 'mongoose' );

var userSchema = new mongoose.Schema({
        shopID: Number,
        userName: String,
        status: String
});

var User = module.exports = mongoose.model('User', userSchema);

