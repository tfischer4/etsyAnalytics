function drawPriceChart(d) {
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'x');
  data.addColumn('number', 'values');
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({type: 'string', role: 'style'});
  data.addRows(d);


  var options = {
    title: 'Average Price by Topic',
    curveType: 'function',
    series: [{'color': '#629DD1'}],
    intervals: { style: 'bars', color: 'black' },
    legend: 'none',
  };

  var chart = new google.visualization.BarChart(document.getElementById('priceDiv'));
  chart.draw(data, options);
}

function drawViewChart(d) {
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'x');
  data.addColumn('number', 'values');
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({type: 'string', role: 'style'});
  data.addRows(d);


  var options = {
    title: 'Average # of Views by Topic',
    curveType: 'function',
    series: [{'color': '#629DD1'}],
    intervals: { style: 'bars', color: 'black' },
    legend: 'none',
  };

  var chart = new google.visualization.BarChart(document.getElementById('viewDiv'));
  chart.draw(data, options);
}


$("#tagSearch").submit(function(e)
{
  var postData = $("#tagInput").val();
  var formURL = $(this).attr("action");
  $.ajax(
  {
    url : formURL,
    type: "POST",
    data : {tag: postData},
    success:function(data, textStatus, jqXHR) 
    {
        //data: return data from server
        console.log(data);
        var opacityKey = "opacity: ";
        var maxOpacity = 1.0;
        var minOpacity = 0.1;

        // Draw Price Chart
        var nbrTopics = data.priceChart.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrElements = data.priceChart[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          data.priceChart[i][nbrElements+1] = opacityKey.concat(opacity.toString());
        }  
        
        var code = '<div id="priceDiv" style="width: 500px; height: 250px;"></div>';
        $("#searchResults").before(code);
        drawPriceChart(data.priceChart);

        // Draw View Chart
        var nbrTopics = data.viewChart.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrElements = data.viewChart[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          data.viewChart[i][nbrElements+1] = opacityKey.concat(opacity.toString());
        }  
        
        var code = '<div id="viewDiv" style="width: 500px; height: 250px;"></div>';
        $("#searchResults").before(code);
        drawViewChart(data.viewChart);

        // Draw Topic Keywords
        var nbrTopics = data.topics.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrWords = data.topics[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          for (var j = nbrWords; j >= 0; j--) {
            var code = '<div class="searchResults" style="background: rgba(68,138,200,'+opacity.toString()+')"><p>' + data.topics[i][j] + '</p></div>';
            $("#searchResults").after(code);
          }
        }     
    },
    error: function(jqXHR, textStatus, errorThrown) 
    {
        //if fails      
    }
  });
  e.preventDefault(); //STOP default action
  e.unbind(); //unbind. to stop multiple form submit.
});

