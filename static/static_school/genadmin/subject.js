$(function(){

var year ='', start='', end ='', current=''

$('.submit').click(function(e) {
    $('.error_box').attr('hidden', true);
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new subject?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new subject!",
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
    var name=$('.name').val();    
    
    if (name=='' || name=='undefined'){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ name: name,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                    console.log(jsondata);
                    var show_success=true
                    if (jsondata['name'] == "Name exists"){
                        $('.error_box').attr('hidden', false);                        
                        show_success=false;
                    }
                    if (show_success){
                        swal("Hooray", "New subject added", "success");
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
        swal("Oops...", "Please enter the subject name before clicking submit.", "error");
    }
}


    
});