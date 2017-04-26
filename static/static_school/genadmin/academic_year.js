$(function(){

var year ='', start='', end ='', current=''

$('.submitnew').click(function(e) {
    $('.year_error').attr('hidden', true);
    $('.start_error').attr('hidden', true);
    $('.end_error').attr('hidden', true);
    $('.start_end').attr('hidden', true);
    $('.error_box').attr('hidden', true);
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new academic year?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new academic  year!",
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
    var year=parseInt($('.year').val());
    var start=$('.start').val();
    var end=$('.end').val();
    var current = $('.current').is(":checked");
    
    if (year == '' || isNaN(year) || start=='' || end=='' || start=='undefined'||end=='undefined' || current=='undefined'){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ year: year,
                    start: start.split("/").reverse().join("-"),
                    end: end.split("/").reverse().join("-"),
                    current:current,
                    calltype: "newacadyear",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                    console.log(jsondata);
                    var show_success=true
                    if (jsondata['year'] == "Year Exists"){
                        $('.error_box').attr('hidden', false);
                        $('.year_error').attr('hidden', false);
                        show_success=false;
                    }
                    if (jsondata['start'] == "Start Exists"){
                        $('.error_box').attr('hidden', false);
                        $('.start_error').attr('hidden', false);
                        show_success=false;
                    }
                    if (jsondata['end'] == "End Exists"){
                        $('.error_box').attr('hidden', false);
                        $('.end_error').attr('hidden', false);
                        show_success=false;
                    }
                    if (jsondata['start-end'] == "Start gt End"){
                        $('.error_box').attr('hidden', false);
                        $('.start_end').attr('hidden', false);
                        show_success=false;
                    }
                    if (show_success){
                        swal("Hooray", "New academic year added", "success");
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
        swal("Oops...", "Please enter all the data before clicking submit.", "error");
    }
}


$('.submitchange').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "This will change current academic year for the whole system!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, change current academic year!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){change_data()},600)            
        }
    })
});
    
function change_data(){
    var new_acad_year=0;
    new_acad_year=parseInt($(".academic").find(':selected').data('id'));
    if (new_acad_year != 0 && !(isNaN(new_acad_year))){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ new_acad_year: new_acad_year,
                    calltype: "changeacadyear",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                    var done=true;
                    swal("Hooray", "Academic year changed.", "success");
                    setTimeout(location.reload(true),1000);
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