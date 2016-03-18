var PythonShell = require('python-shell');

var config = require('config');
var apiKey = config.get('etsy.key');
var baseURI= config.get('etsy.baseURI');
var axpURI = config.get('axpProxy.uri');
var axpFlg = config.get('axpProxy.flg');


module.exports = {
  getTags : function( tag, _callBack) {
    var options = {
      mode: 'json',
      scriptPath: '/Users/tfische/Projects/Etsy/app/routes/python',
      args: [tag, baseURI, apiKey, axpURI, axpFlg]
    };

    var pyshell = new PythonShell('etsyTagModel.py', options);
 
    pyshell.on('message', function (message) {
      console.log(message);
      _callBack(null, message);
    });

    pyshell.end(function (err) {
      if (err) throw err;
      console.log('finished for tag: %j', tag);
    });

  }
};


module.exports = {
  getKeywords : function( tag, _callBack) {
    var options = {
      mode: 'json',
      scriptPath: '/Users/tfische/Projects/Etsy/app/routes/python',
      args: [tag, baseURI, apiKey, axpURI, axpFlg]
    };

    var pyshell = new PythonShell('etsyNMFModel.py', options);

    pyshell.on('message', function (message) {
      console.log(message);
      _callBack(null, message);
    });

    pyshell.end(function (err) {
      if (err) throw err;
      console.log('finished for tag: %j', tag);
    });

  }
};


