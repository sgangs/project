$(function(){

function swal_messages_display(msg, timer, title, message_type){
    swal({
        title: title,
        text: msg,
        type: message_type,
        allowOutsideClick: true,
        timer:timer,
    });
}



load_accounts()

function load_accounts(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#period .data").remove();
            $('#account_period_current').find('option').remove();
            $.each(jsondata, function(){
                start_date = this.start.split("-").reverse().join("-")
                end_date = this.end.split("-").reverse().join("-")
                $('#period').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+start_date+"</td>"+
                "<td>"+end_date+"</td>"+
                "<td class='capitalize'>"+this.finalized+"</td>"+
                "<td class='capitalize'>"+this.current_period+"</td>"+
                "</tr>");

                $('#account_period_current').append($('<option>',{
                    'data-id': this.id,
                    'text': start_date + " to "+ end_date
                }));
            })
            $('.capitalize').css('textTransform', 'capitalize');
            $('#account_period_current').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal_messages_display("There were erros in retriving data. Kindly try after sometimes or contact support. ", 2500, "Oops...", "error")
            // swal("Oops...", "There were erros in retriving data. Kindly try after sometimes or contact support. ", "error");
        }
    });
}


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new accounting period?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new accounting period!",
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
    var start=$('.start_new').val()
    if (start == '' || start =='undefined' || start == undefined){
        proceed = false;
        swal("Oops...", "Please enter a start date", "error");
    }
    var end = $('.end_new').val()
    if (end == '' || end =='undefined' || end == undefined){
        proceed = false;
        swal("Oops...", "Please enter a end date", "error");
    }
    
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{start: start.split("/").reverse().join("-"),
                    end: end.split("/").reverse().join("-"),
                    calltype: "new_period",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New accounting period added", "success");
                        setTimeout(location.reload(true),2500);
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
}


$('.submit_change').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to change current accounting perood?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, change current accounting period!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){change_year()},600)
        }
    })
});
    
function change_year(){
    var proceed=true;
    period_id=$('.account_period_current').find(':selected').data('id');
    if (period_id == '' || period_id =='undefined' || typeof(period_id) == undefined ){
        proceed = false;
        swal("Oops...", "Please select an accounting year", "error");
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{period_id: period_id,
                    calltype: "change_current_period",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        $('#changeMode').modal('hide');
                        swal_messages_display("Current period changed.", 2000, "Hooray", "success")
                        // swal("Hooray", "Current period changed.", "success");
                        // setTimeout(location.reload(true),2500);
                        load_accounts();
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal_messages_display("Recheck your inputs. There were some errors!", 2500, "Oops...", "error")
                    // swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
}


});