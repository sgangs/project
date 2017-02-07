$(function(){

var repeat_change=0;
var profileid='';
var email='';
var user='';
var pass='';
var repeat='';
$( ".student" ).change(function() {
    profileid=$(".student").find(':selected').data('id');
    (function() {
    $.ajax({
        url : "", 
        type : "POST", 
        data : { profileid: profileid,
            calltype: 'mail',
            csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            if (jsondata['email'] == "" || jsondata['email'] == null){
                email=null;
                $('.email').val('');
            }
            else{
                email=jsondata['email']
                $('.email').val(email);
            }
            
            
            //console.log("success"); // another sanity check
        },
        //handle a non-successful response
        error : function() {
            classnameproceed = true;
        }
    });
    }());
});


$( ".repeat" ).change(function() {
    repeat_change+=1;
    repeat=$(".repeat").val();
    pass=$(".password").val();
    if (repeat != pass){
        $(".repeatdiv").addClass('has-error');
        $(".repeat-p").attr('hidden',false);
        $(".passworddiv").addClass('has-error');
    }
    if (repeat == pass){
        $(".repeatdiv").removeClass('has-error');
        $(".passworddiv").removeClass('has-error');
        $(".repeat-p").attr('hidden',true);
    }
});

$( ".email" ).change(function() {
    email=$(".email").val();
});

$( ".user" ).change(function() {
    user=$(".user").val();
    if (user != ""){
        (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { user: user,
                calltype: 'user',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                if (jsondata['error'] == "Username exist"){
                    $(".userdiv").addClass('has-error');
                    $(".user-p").attr('hidden',false);
                }
                else{
                    $(".userdiv").removeClass('has-error');
                    $(".userdiv").addClass('has-success');
                    $(".user-p").attr('hidden',true);
                }
                
                
                //console.log("success"); // another sanity check
            },
            //handle a non-successful response
            error : function() {
                $(".userdiv").removeClass('has-error');
                $(".userdiv").addClass('has-success');
                $(".user-p").attr('hidden',true);
            }
        });
        })();
    }
});

$( ".password" ).change(function() {
    repeat=$(".repeat").val();
    pass=$(".password").val();
    if (repeat_change>0){
        if (repeat != pass){
            $(".repeatdiv").addClass('has-error');
            $(".repeat-p").attr('hidden',false);
            $(".passworddiv").addClass('has-error');
        }
        if (repeat == pass){
            $(".repeatdiv").removeClass('has-error');
            $(".passworddiv").removeClass('has-error');
            $(".repeat-p").attr('hidden',true);
        }
    }
});

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo attendance recording!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, create profile!",
        closeOnConfirm: false,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            save_data()
        }
    })
});

function save_data(){
    var items = [];
    var proceed = true;
    var info=false;
    $("tr.data").each(function() {       
        var id = $(this).find('td:nth-child(1)').html();
        var ispresent = $(this).find('td:nth-child(5) input').is(":checked");
        var absenttype = $(this).find('td:nth-child(6)').find(':selected').data('id');
        var remarks = $(this).find('td:nth-child(7) input').val();
        if (ispresent == undefined || ispresent=='' || ispresent == false){
            if (absenttype == undefined || absenttype==''){
                proceed=false;
            }
        }
        else{
            if (absenttype != undefined && absenttype !=''){
                info=true;
            }   
        }

        var item = {
            teacherid : id,
            ispresent: ispresent,
            absenttype: absenttype,
            remarks : remarks,    
        };
        items.push(item);        
    });
    console.log(items)
    if (proceed){
        if (info){
            swal("Umm...", "In case teacher is present, reason for absent will be ignored", "info");
        }
        else{
            swal("Hooray..", "Teacher attendance recorded successfully", "success");
        }
    }
    else{
        swal("Oops...", "Select type of absence.", "error");
    }
        
};

});