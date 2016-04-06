function drawChart(d, div, title) {
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'x');
  data.addColumn('number', 'values');
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({id:'i0', type:'number', role:'interval'});
  data.addColumn({type: 'string', role: 'style'});
  data.addRows(d);


  var options = {
    title: title,
    curveType: 'function',
    series: [{'color': '#629DD1'}],
    intervals: { style: 'bars', color: 'black' },
    legend: 'none',
  };

  var chart = new google.visualization.BarChart(document.getElementById(div));
  chart.draw(data, options);
}



$("#tagSearch").submit(function(e)
{
  $("#searchButton").attr("disabled", true);  
  var postData = $("#tagInput").val();
  var formURL = $(this).attr("action");

  // Prep DOM
  $("#results").empty();

  $.ajax(
  {
    url : formURL,
    type: "POST",
    data : {tag: postData},
    success:function(data, textStatus, jqXHR) 
    {
        //data: return data from server
        // console.log(data);
        var opacityKey = "opacity: ";
        var maxOpacity = 1.0;
        var minOpacity = 0.1;

        // Draw Chart Section
        var code = '<section class="wrapperLight style1" id="chartResults" style="text-align: center"></section>';
        $("#results").append(code);

        // Draw Price Chart
        var nbrTopics = data.priceChart.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrElements = data.priceChart[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          data.priceChart[i][nbrElements+1] = opacityKey.concat(opacity.toString());
        }  
        
        var priceDiv = 'priceDiv';
        var priceTitle = 'Average Price by Topic';
        var code = '<div id="priceDiv" style="width: 400px; height: 250px; margin: 0 auto; display:inline-block;"></div>';
        $("#chartResults").append(code);
        drawChart(data.priceChart, priceDiv, priceTitle);

        // Draw View Chart
        var nbrTopics = data.viewChart.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrElements = data.viewChart[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          data.viewChart[i][nbrElements+1] = opacityKey.concat(opacity.toString());
        }  
        
        var viewDiv = 'viewDiv';
        var viewTitle = 'Average # of Views by Topic';
        var code = '<div id="viewDiv" style="width: 400px; height: 250px; margin: 0 auto; display:inline-block;"></div>';
        $("#chartResults").append(code);
        drawChart(data.viewChart, viewDiv, viewTitle);

        // Draw Favorites Chart
        var nbrTopics = data.favorerChart.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrElements = data.favorerChart[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          data.favorerChart[i][nbrElements+1] = opacityKey.concat(opacity.toString());
        }  
        
        var favorerDiv = 'favorerDiv';
        var viewTitle = 'Average # of Favorers by Topic';
        var code = '<div id="favorerDiv" style="width: 400px; height: 250px; margin: 0 auto; display:inline-block;"></div>';
        $("#chartResults").append(code);
        drawChart(data.favorerChart, favorerDiv, viewTitle);

        // Draw Topic Keywords
        var nbrTopics = data.topics.length - 1;
        for (var i = nbrTopics; i >= 0; i--) {
          var nbrWords = data.topics[i].length - 1;
          var opacity = ((i+1)/(nbrTopics+1) * (maxOpacity - minOpacity));
          var divID = 'topic' + i.toString();
          var code = '<section class="wrapperSearch" id="' + divID + '" style="text-align: center"></section>';
          $("#chartResults").after(code);
          for (var j = nbrWords; j >= 0; j--) {
            var code = '<div class="searchResults" style="background: rgba(68,138,200,'+opacity.toString()+');"><p>' + data.topics[i][j] + '</p></div>';
            $("#" + divID).prepend(code);
          }
          var code = '<hr style="margin: 0 0;">';
          $("#" + divID).prepend(code);
        }
        $("#searchButton").attr("disabled", false);       
    },
    error: function(jqXHR, textStatus, errorThrown) 
    {
        //if fails      
    }
  });
  e.preventDefault(); //STOP default action
});

