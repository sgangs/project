$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var structure_name="", account='', rule=0, salary_ceiling=0, predefined=0, multiplier=0;

$( ".structurename" ).change(function() {
    structure_name=$(".structurename").val();
    if (structure_name != ''){
        $( ".submit" ).prop('disabled',false); 
    }
    else{
        $( ".submit" ).prop('disabled',true);     
    }
});

$( ".accounthover" ).click(function() {
    swal({
        type: "info",
        title: "How To",
        text: "These accounts are those defined under <b> Ledger Group - Salary </b>. If registered account is not available," +
        "that means they were registered under different Leger Group. Register (delete old account, if already created) to continue",
        html: true,
        timer: 15000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});

$( ".account" ).change(function() {
    account=parseInt($( ".account" ).find(':selected').data('id'));
    // console.log(epfaccount);
});



$('.rule input').on('change', function() {
    rule = parseInt($('input[name=optionsRadios]:checked', '.rule').val()); 
    if (rule ==3){
        $('.predefined').attr('hidden', false);
        $('.other').attr('hidden', true);
    }
    else if(rule==2){
        $('.other').attr('hidden', false);
        $('.predefined').attr('hidden', true);        
    }
    else if (rule ==1) {
        $('.other').attr('hidden', false);
        $('.predefined').attr('hidden', true);
        $('.sal_cap').attr('hidden', true);
    }
});


$( ".salary_ceiling" ).change(function() {
    salary_ceiling=$( ".salary_ceiling" ).val();
});

$( ".multiplier" ).change(function() {
    multiplier=$( ".multiplier" ).val();
});

$( ".predefined" ).change(function() {
    predefined=$( ".predefined" ).val();    
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo statuory structure creation!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, Employee Statutory Structure Confirmed!",
        closeOnConfirm: true,
        closeOnCancel: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)            
        }
    })
});

function reconfirm() {
    swal({
        title: "Please reconfirm",
        text: "<b>You cannot undo statutory structure creation!</b>",
        html: true,
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, Employee Statutory Structure Reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true
    }, function(isConfirm){
        console.log(isConfirm);
        if (isConfirm){
            setTimeout(function(){save_data()},600);            
        }
    })
};

function save_data(){
    var proceed_positive=true, proceed_account=true, proceed=true;
    //Check if accounts are selected
    if (rule<1 || salary_ceiling<0 || predefined<0 || multiplier<0){
        proceed_positive=false;
    }
    if (account == undefined || account == ''){
        proceed_account=false;
    }
    //First check according to generic rule 
    if (salary_ceiling == 0 || salary_ceiling == undefined || salary_ceiling == ''){
        proceed=false;
    }

    //modify proceed accrodingly if rule selected is different
    if (rule == 3){
        if (predefined< 0 ){
            proceed=false;
        }
        else{
            proceed=true;
        }
    }
    else if(rule == 1){
        if(multiplier< 0){
            proceed=false;
        }
        else{
            proceed=true;
        }
    }
    else if (rule< 0){
        proceed=false;
    }
    
    if (proceed && proceed_account && proceed_positive){
    //Send ajax function to back-end 
    (function(){
        $.ajax({
            url : "", 
            type: "POST",
            data:{ structure_name: structure_name,
                rule:rule,
                account:account,
                salary_ceiling:salary_ceiling,
                predefined:predefined,
                multiplier:multiplier,
                csrfmiddlewaretoken: csrf_token },
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
                // location.href = redirect_url;
                // console.log("Its cool in here")
                // console.log(jsondata);
                swal("Hooray!!", "The salary structure was successfully registered!", "success");
                setTimeout(function(){location.reload(true);},600);
            },
            // handle a non-successful response
            error : function() {
                swal("Oops..", "There were some errors!", "error");
            }
        });
    }());                
    }
    else{
        swal("Bluhh..", "Please fill the form as per instruction. All visible fields (as per selection)"+
            "shall be filled. Number fields should not have non numbers or negative values", "error");
    }
}   



});