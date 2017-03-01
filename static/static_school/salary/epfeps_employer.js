$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var structure_name="", epfaccount='', epsaccount='', rule=0, salary_ceiling=0, epf_predefined=0, epf_multiplier=0, eps_predefined=0,
    eps_multiplier=0, epfadminaccount="", admin_min=0, admin_predefined=0, admin_multiplier=0, epfadmin=false;

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

$( ".rule3" ).click(function() {
    swal({
        type: "warning",
        title: "Statutory Warning!",
        text: "Please check with your accountant before selecting this. This rule, i.e. <b>Option 3</b> might be debatable"+
        " as per Indian Law",
        html: true,
        timer: 12000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});

$( ".epfaccount" ).change(function() {
    epfaccount=parseInt($( ".epfaccount" ).find(':selected').data('id'));
});


$( ".epsaccount" ).change(function() {
    epsaccount=parseInt($( ".epsaccount" ).find(':selected').data('id'));
    // console.log(epfaccount);
});


$('.rule input').on('change', function() {
    rule = parseInt($('input[name=optionsRadios]:checked', '.rule').val()); 
    if (rule ==4){
        $('.predefined').attr('hidden', false);
        $('.other').attr('hidden', true);
    }
    else if(rule==3){
        $('.other').attr('hidden', false);
        $('.predefined').attr('hidden', true);
        $('.epsmultiplierdiv').attr('hidden', true);
    }
    else{
        $('.other').attr('hidden', false);
        $('.predefined').attr('hidden', true);
    }
});


$( ".salary_ceiling" ).change(function() {
    salary_ceiling=$( ".salary_ceiling" ).val();
});

$( ".epsmultiplier" ).change(function() {
    eps_multiplier=$( ".epsmultiplier" ).val();
});

$( ".epspredefined" ).change(function() {
    eps_predefined=$( ".epspredefined" ).val();
});

$( ".epfmultiplier" ).change(function() {
    epf_multiplier=$( ".epfmultiplier" ).val();
});

$( ".epfpredefined" ).change(function() {
    epf_predefined=$( ".epfpredefined" ).val();    
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$( ".epfadminselect" ).on("change", function() {
    epfadmin=$('.epfadminselect').is(":checked");
    if (epfadmin){
        swal("EPF Admin Charges", "If not applicable, deselect it (remove the tick). Otherwise, fill the details below", "info");
        $('.epfadmindiv').attr('hidden',false);
    }
    else{
        $('.epfadmindiv').attr('hidden',true);
    }
});

$( ".epfadminaccount" ).change(function() {
    epfadminaccount=parseInt($( ".epfadminaccount" ).find(':selected').data('id'));
});

$( ".admin_min" ).change(function() {
    admin_min=$( ".admin_min" ).val();
});

$( ".admin_multiplier" ).change(function() {
    admin_multiplier=$( ".admin_multiplier" ).val();    
});

$( ".admin_predefined" ).change(function() {
    admin_predefined=$( ".admin_predefined" ).val();    
});

// $('.accountname').change(function(){
//     swal({
//         type: "warning",
//         title: "Statutory Law Alert!",
//         text: "Basic Salary needs to have PF structure. Do select 'Use this for PF calculation' accordingly.",
//         timer: 15000,
//         allowOutsideClick: true,
//         showConfirmButton: true
//     });
// });


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo statuory structure creation!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, Statutory Fromat Creation Confirmed!",
        closeOnConfirm: true,
        closeOnCancel: true
    }, function(isConfirm){
        if (isConfirm){
            console.log(isConfirm);
            setTimeout(function(){reconfirm()},600)
            
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
            console.log(isConfirm);
            setTimeout(function(){save_data()},600)
            
        }
    })
};

function save_data(){
    var proceed_admin=true, proceed_positive=true, proceed_account=true, proceed=true ;
    if (rule<0 || salary_ceiling<0 || epf_predefined<0 || epf_multiplier<0 || eps_predefined<0 ||
        eps_multiplier<0 || admin_min<0 || admin_predefined<0 || admin_multiplier<0){
        proceed_positive=false;
        console.log(rule);
        console.log(salary_ceiling); console.log(epf_predefined); console.log(epf_multiplier);console.log(eps_predefined);
        console.log(eps_multiplier);console.log(admin_min);console.log(admin_predefined);console.log(admin_multiplier);
    }

    //Check if accounts are selected
    if (epfaccount == 0 || epfaccount == undefined || epfaccount == '' ||
        epsaccount == 0 || epsaccount == undefined || epsaccount == ''){
        proceed_account=false;
        console.log("Its here");
    }
    //First check according to rule 1 & 2 irrespectively
    if (salary_ceiling == 0 || salary_ceiling == undefined || salary_ceiling == '' || 
        eps_multiplier == 0 || eps_multiplier == undefined || eps_multiplier == '' ||
        epf_multiplier == 0 || epf_multiplier == undefined || epf_multiplier == ''){
        proceed=false;
        console.log("Its here");
    }

    //modify proceed accrodingly if rule selected is 3/4
    if (rule == 4){
        if (eps_predefined == 0 || eps_predefined == undefined || eps_predefined == '' || 
            epf_predefined == 0 || epf_predefined == undefined || epf_predefined == ''){
            proceed=false;
            console.log("Its here");
        }
        else{
            proceed=true;

        }
    }
    else if(rule == 3){
        if(epf_multiplier == 0 || epf_multiplier == undefined || epf_multiplier == '' ||
            epfaccount == 0 || epfaccount == undefined || epfaccount == ''){
            proceed=false;
            console.log("Its here");
        }
        else{
            proceed=true;
        }
    }
    else if (rule == 0 || rule == undefined || rule == ''){
        proceed=false;
        console.log("Its here");
    }

    //check for epfadmin
    if (epfadmin){
        if (epfadminaccount == 0 || epfadminaccount == undefined || epfadminaccount == ''){
            proceed_admin=false;
        }
        if (rule == 4){
            if (admin_predefined == 0 || admin_predefined == undefined || admin_predefined == ''){
                proceed_admin=false;
            }
        }
        else{
            if (admin_min == 0 || admin_min == undefined || admin_min == '' || 
                admin_multiplier == 0 || admin_multiplier == undefined || admin_multiplier == ''){
                proceed_admin=false;
            }
        }

    }
    console.log(proceed);
    console.log(proceed_admin);
    console.log(proceed_positive);
    if (proceed && proceed_admin && proceed_positive && proceed_account){
    //Send ajax function to back-end 
    (function(){
        $.ajax({
            url : "", 
            type: "POST",
            data:{ structure_name: structure_name,
                rule:rule,
                epfaccount:epfaccount,
                epsaccount:epsaccount,
                salary_ceiling:salary_ceiling,
                epf_predefined:epf_predefined,
                epf_multiplier:epf_multiplier,
                eps_predefined:eps_predefined,
                eps_multiplier:eps_multiplier,
                epfadmin:epfadmin,
                epfadminaccount:epfadminaccount,
                admin_min:admin_min,
                admin_predefined:admin_predefined,
                admin_multiplier:admin_multiplier,
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