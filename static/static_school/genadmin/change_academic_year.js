$(function(){

//This variable will store the student list added via json

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "This will change current academic year for the whole solution!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, change current academic year!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)            
        }
    })
});
    
function save_data(){
    var new_acad_year=0;
    new_acad_year=parseInt($(".academic").find(':selected').data('id'));
    if (new_acad_year != 0 && !(isNaN(new_acad_year))){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ new_acad_year: new_acad_year,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                                // alert("Group Fee linked successfully");
                    swal("Hooray", "Academic year changed.", "success");
                    setTimeout(function(){location.href = redirect_url;},2000);
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
        swal("Oops...", "Select academic year.", "error");
    }
}    
    
});