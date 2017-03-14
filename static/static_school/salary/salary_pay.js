$(function(){

var payment_mode=0;
var outside_proceed=true;

$('.mode').change(function() {
    payment_mode=parseInt($(".mode").find(':selected').data('id'));
    (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ payment_mode: payment_mode,
                    call_type:"Payment",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                available=parseFloat(jsondata)
                console.log(available);
                console.log(total_payable);
                if (available < total_payable){
                    outside_proceed = false; 
                    swal("Oops..", "Please note that you have insufficient balance. Proceeding further will result in negative cash/bank balance.", "error");
                }

                // swal("Hooray!!", "The salary payment was successfully done", "success");
                // setTimeout(function(){location.reload(true);},2500);
                
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors.", "error");
                }
            });
        }());
});

$('.submit').click(function(e) {
    swal({
        title: "Make payment entry?",
        text: "Once paid this cannot be undone!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, pay salary!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            // setTimeout(function(){reconfirm()},400)
            setTimeout(function(){save_data()},400)
            
        }
    })
});
function reconfirm () {
    swal({
        title: "Make payment entry? Please RECONFIRM",
        text: "Once generated this cannot be undone!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, pay salary!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},400)
            
        }
    })
};

function save_data(){
    var proceed = true;
    var payment_proceed=true;
    payment_mode=parseInt($(".mode").find(':selected').data('id'));
    console.log(payment_mode);
    if (isNaN(payment_mode) || payment_mode <1){
        payment_proceed=false;
    }

    var details=[];
    $("tr.data").each(function() {
        var id = $(this).find('td:nth-child(1)').html();
        var confirm = $(this).find('td:nth-child(10) input').is(":checked");
        var reject = $(this).find('td:nth-child(11) input').is(":checked");
        if (confirm){
            if (reject){
                proceed=false;
            }
        }
        if (reject){
            if (confirm){
                proceed=false;
            }
        }
        var item = {
            id : id,
            confirm: confirm,
            reject: reject,
        };
        details.push(item);
    });
    if (proceed && payment_proceed){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details:JSON.stringify(details),
                    payment_mode: payment_mode,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                // location.href = redirect_url;
                swal("Hooray!!", "The salary payment was successfully done", "success");
                setTimeout(function(){location.reload(true);},2500);
                
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors.", "error");
                }
            });
        }());
    }
    else if (payment_proceed){
        swal("Oops..", "One entry cannot have both confirm and reject. Select either confirm or reject.", "error");
    }
    else if (proceed){
        swal("Oops..", "Please select payment mode.", "error");
    }
    else{
        swal("Oops..", "One entry cannot have both confirm and reject. Select either confirm or reject. Also, please select paymeny mode.", "error");
    }
}


});
