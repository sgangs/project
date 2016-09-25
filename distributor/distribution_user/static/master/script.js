$( function(){

	if(listtype != 'Sales Invoice'){

		$( ".delete" ).on("click", function(){

			var item = $.trim($(this).prev().html());
			var choice = confirm(this.getAttribute('data-confirm'));
			if (choice){

				(function() {
					$.ajax({
        				url : url_list, 
        				type : "POST", 
        				data : { type: listtype,
        						 itemkey: item,
        						 'csrfmiddlewaretoken': csrf_token}, // data sent with the post request
        				dataType: 'json',

        					// handle a successful response
        				success : function(jsondata){ 
        					//alert(jsondata['name'])
        					location.reload(true);
        				},

        				});
				}());

			}
			
		});

	}

	
});