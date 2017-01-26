$(function(){



//This is used to remove the alert modal
// function clearmodal(){
//     window.setTimeout(function(){
//         bootbox.hideAll();
//     }, 2500);
// }


//get address of customer from database
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
        text: "You cannot undo profile crreation!",
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
            save_student()
        }
    })
});

function save_student(){
    if (profileid != "" && user!="" && email != "" && pass != "" && repeat != ""){
    //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ profileid: profileid,
                        user: user,
                        email:email,
                        pass: pass,
                        repeat: repeat,
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                    success : function(jsondata) {
                        if (jsondata['error'] == undefined){
                            swal("Hooray", "Profile login created successfully!", "success");
                            setTimeout(function(){
                                location.href = redirect_url;
                            },3000);
                            
                        }
                        else{
                            swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                        }
                    },
                    // handle a non-successful response
                    error : function() {
                        console.log("Some error");
                        // swal("Oops...", "There was some error in form creation!", "error");
                    }
                });
            }());
    }
    else if (profileid == ""){
        swal("Oops...", "Please select profile!", "error");
    }
    else if (user == ""){
        swal("Oops...", "Please fill username!", "error");
    }
    else if (email == ""){
        swal("Oops...", "Please fill email!", "error");
    }
    else{
        swal("Oops...", "Please check your password field!", "error");
    }
        
};

});