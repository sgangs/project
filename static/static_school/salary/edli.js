$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var structure_name="", edli_account=0, edliac_account=0, rule=0, ceiling=0, edli_predefined=0, edli_multiplier=0, 
    edliac_min=0, edliac_multiplier=0, edliac_predefined=0;

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



$( ".edli_account" ).change(function() {
    edli_account=parseInt($( ".edli_account" ).find(':selected').data('id'));
});

$( ".edliac_account" ).change(function() {
    edliac_account=parseInt($( ".edliac_account" ).find(':selected').data('id'));
});


$('.rule input').on('change', function() {
    rule = parseInt($('input[name=optionsRadios]:checked', '.rule').val()); 
    if (rule ==3){
        $('.predefined').attr('hidden', false);
        $('.other').attr('hidden', true);
    }
    else if(rule==1){
        $('.other').attr('hidden', false);
        $('.predefined').attr('hidden', true);
        $('.ceiling').attr('hidden', true);
    }
    else{
        $('.other').attr('hidden', false);
        $('.predefined').attr('hidden', true);
    }
});


$( ".salary_ceiling" ).change(function() {
    ceiling=$( ".salary_ceiling" ).val();
});

$( ".edli_multiplier" ).change(function() {
    edli_multiplier=$( ".edli_multiplier" ).val();
});

$( ".edli_predefined" ).change(function() {
    edli_predefined=$( ".edli_predefined" ).val();
});

$( ".edliac_min" ).change(function() {
    edliac_min=$( ".edliac_min" ).val();
});

$( ".edliac_multiplier" ).change(function() {
    edliac_multiplier=$( ".edliac_multiplier" ).val();
});

$( ".edliac_predefined" ).change(function() {
    edliac_predefined=$( ".edliac_predefined" ).val();
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo statuory structure creation!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, Statutory Fromat Creation Confirmed!",
        closeOnConfirm: true,
        closeOnCancel: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},300)
            
        }
    })
});

function reconfirm() {
    swal({
        title: "Are you sure?",
        text: "You cannot undo statuory structure creation!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, Statutory Fromat Creation Re-confirmed!",
        closeOnConfirm: true,
        closeOnCancel: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},300)            
        }
    })
};

function save_data(){
    var proceed_positive=true, proceed_account=true, proceed=true;
    if (rule<0 || ceiling<0 || edli_multiplier<0 || edli_predefined<0  || edliac_min<0 || edliac_multiplier<0 || edliac_predefined<0 ){
        proceed_positive=false;
    }
    //Check if accounts are selected
    if (edli_account < 1 || edli_account == '' || edli_account == 'undefined' || 
        edliac_account < 1 || edliac_account == '' || edliac_account == 'undefined'){
        proceed_account=false;
    }
    
    if (rule==3){
        if (edli_predefined == 0 || edli_predefined == '' || edli_predefined == 'undefined' || 
            edliac_predefined == 0 || edliac_predefined == '' || edliac_predefined == 'undefined'){
            proceed=false;
        }
    }
    else if (rule==2){
        if (ceiling == 0 || ceiling == '' || ceiling == 'undefined' || 
            edli_multiplier == 0 || edli_multiplier == '' || edli_multiplier == 'undefined' || 
            edliac_multiplier == 0 || edliac_multiplier == '' || edliac_multiplier == 'undefined' || 
            edliac_min == 0 || edliac_min == '' || edliac_min == 'undefined'){
            proceed=false;
        }
    }
    else if (rule == 1){
        if (edli_multiplier == 0 || edli_multiplier == '' || edli_multiplier == 'undefined' || 
            edliac_multiplier == 0 || edliac_multiplier == '' || edliac_multiplier == 'undefined' || 
            edliac_min == 0 || edliac_min == '' || edliac_min == 'undefined'){
            proceed=false;
        }
    }
    if (proceed && proceed_account && proceed_positive){
    //Send ajax function to back-end 
    (function(){
        $.ajax({
            url : "", 
            type: "POST",
            data:{ structure_name: structure_name,
                rule:rule,
                edli_account:edli_account,
                edliac_account:edliac_account,
                ceiling:ceiling,
                edli_multiplier:edli_multiplier,
                edli_predefined:edli_predefined,                
                edliac_min:edliac_min,
                edliac_multiplier:edliac_multiplier,
                edliac_predefined:edliac_predefined,
                csrfmiddlewaretoken: csrf_token },
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
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