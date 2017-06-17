$(function(){

load_zone()

function load_zone(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#customer').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.key+"</td>"+
                    "<td>"+this.details+"</td>"+
                    "</tr>");
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No zone data exist.", "error");
        }
    });
}


var name ='', key='', details ='';


$('.submit').click(function(e) {
    // $('.year_error').attr('hidden', true);
    // $('.start_error').attr('hidden', true);
    // $('.end_error').attr('hidden', true);
    // $('.start_end').attr('hidden', true);
    // $('.error_box').attr('hidden', true);
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new zone?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new zone!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data()},600)            
        }
    })
});
    
function new_data(){
    var proceed=true;
    name=$('.name').val()
    key=$('.key').val()
    details=$('.details').val()
    
    if (name == '' || name =='undefined' || key == '' || key =='undefined' ){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "getdata/" , 
                type: "POST",
                data:{name: name,
                    key:key,
                    details:details,
                    calltype: "newzone",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New zone added", "success");
                        setTimeout(location.reload(true),1000);
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
    else{
        swal("Oops...", "Please note that name & key must be filled and phone number must be valid", "error");
    }
}

});