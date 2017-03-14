$(function(){

var days=0;
var start=0;
var end="";
var pay=0;
var account=0;
var outside_proceed=true;


$( ".days" ).change(function() {
    days=parseInt($(".days").val());
});

$( ".start" ).change(function() {
    start=parseInt($(".start").val());
    if (isNaN(start)){
        swal("Oops..", "Start must be a number.", "error");
        end="Start is not a number";
        outside_proceed=false;
    }
    else if (start==1){
        end="Last";
        outside_proceed=true;
    }
    else if (start>1 && start < 29){
        end=start-1;
        outside_proceed=true;
    }
    else{
        end="Please change start date";
        outside_proceed=false;
        swal("Ehhh..", "Salary structure must start on any day upto the 28th of a month.", "info");
    }

    $(".end").val(end);
});


$( ".pay" ).change(function() {
    pay=parseInt($(".pay").val());
});

$( ".account" ).change(function() {
    account=$('.account').find(':selected').data('id');
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Your complete salary and attendance will be based on these rules.",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, create salary rule!",
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
    var proceed=true;
    if (pay < 1 || pay>31 || start <1 || start >28 || account < 1 || days<1 || days>30){
        proceed=false;
    }
    console.log(proceed);
    if (proceed && outside_proceed){
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ pay: pay,
                    days: days,
                    start:start,
                    end:end,
                    account: account,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    location.href = redirect_url;
                    // console.log(jsondata);
                    swal("Hooray!!", "The salary rule was successfully registered!", "success");
                    setTimeout(function(){location.reload(true);},600)
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors!", "error");
                }
            });
        }());                
    }
    else{
        swal("Bluhh..", "Please recheck your entry. Salary cycle must start latest by 28. No. of working days in a month cannot be more than 30", "error");
    }    
}

});