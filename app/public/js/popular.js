var pageNbr = 1;

function writeListings(listings){
	html = '';
	for (i in listings) {
		html += '<div class="pop-row">';
		html += '<div class="pop-cell"><a href= "' + listings[i].url + '"><img src= "' + listings[i].image + '"align="left"></a></div>';
		html += '<div class="pop-cell"><h4 style="margin: 0;">' + listings[i].title + '\n</h4>';
    html += '<pre>Category: ' + listings[i].taxonomy_path + '\n';
    html += 'Favorers: ' + listings[i].num_favorers + '\n';
    html += 'Views: ' + listings[i].views + '</pre>';
		html += '</div></div>';
	}
  console.log(html);
	return html;
}


$("#popularMore").submit(function(e)
{
  $("#moreButton").attr("disabled", true);  
  var formURL = $(this).attr("action");
  pageNbr += 1;

  // Prep DOM
  // $("#results").empty();

  $.ajax(
  {
    url : formURL,
    type: "POST",
    data : {page: pageNbr},
    success:function(data, textStatus, jqXHR) 
    {
    	$("#resultsDiv").append(writeListings(data));
    	$("#moreButton").attr("disabled", false);
    },
    error: function(jqXHR, textStatus, errorThrown) 
    {
        //if fails      
    }
  });
  e.preventDefault(); //STOP default action
});
