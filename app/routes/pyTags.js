var PythonShell = require('python-shell');


module.exports = {
  getTags : function( tag, _callBack) {
    var options = {
      mode: 'json',
      scriptPath: '/Users/tfische/Projects/Etsy/app/routes/python',
      args: [tag]
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


/*
    var shell = PythonShell.run('etsyTagModel.py', options, function (err, results) {
      if (err) throw err;
      // results is an array consisting of messages collected during execution 
      console.log('results: %j', results[0]);

      _callBack(null, JSON.parse(results[0]));
    });
*/
  }
};


