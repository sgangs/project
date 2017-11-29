$(function(){


load_users()

function load_users(){
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{calltype: "get_users",
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#customer').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+this.first_name+" "+this.last_name+"</td>"+
                "<td>"+this.username+"</td>"+
                "<td>"+this.email+"</td>"+
                "<td>"+$.trim(this.aadhar_no)+"</td>"+
                "<td>"+$.trim(this.user_type)+"</td>"+
                "</tr>");                
            })
            // console.log(jsondata);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some errors.", "error");
        }
    });
}



var username_valid =false, email_valid=false, phone='', password_valid=false, repeat_valid=false, repeat_change=0, password_strength = 0,
    lastname_valid = false, firstname_valid = false, permission_valid = false, number_valid=true, phone_data='';

var telInput = $('.phone'), errorMsg = $("#error-msg"), validMsg = $("#valid-msg");

var reset = function() {
  telInput.removeClass("error");
  errorMsg.addClass("hide");
  validMsg.addClass("hide");
}

telInput.blur(function() {
  reset();
  if ($.trim(telInput.val())) {
    if (telInput.intlTelInput("isValidNumber")) {
      validMsg.removeClass("hide");
      number_valid=true;
      phone=telInput.intlTelInput("getNumber");
    } else {
      telInput.addClass("error");
      errorMsg.removeClass("hide");
      number_valid=false
    }
  }
});


$(".username").change(function(){
    username = $(".username").val();
    if ($.trim(username).length < 2){
        $(".namediv").addClass('has-warning');
        $(".namediv").removeClass('has-success');
        $(".namediv").removeClass('has-error');
        $(".namediverror").attr('hidden',true);
        username_valid = false;
    }
    else{
        (function() {
            $.ajax({
                url : "data/" , 
                type: "GET",
                data:{username: username,
                    calltype: "check_username",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                    // contentType: "application/json",
                            // handle a successful response
                success : function(jsondata) {
                    if (jsondata['error'] == "Username exist"){
                        $(".namediv").removeClass('has-warning');
                        $(".namediv").removeClass('has-success');
                        $(".namediv").addClass('has-error');
                        $(".namediverror").attr('hidden',false);
                        username_valid = false;
                    }
                    else{
                        $(".namediv").removeClass('has-error');
                        $(".namediv").removeClass('has-warning');
                        $(".namediv").addClass('has-success');
                        $(".namediverror").attr('hidden',true);
                        username_valid = true;
                    }
                },
                    // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
});

$(".firstname").change(function(){
    firstname = $(".firstname").val();
    if ($.trim(firstname).length < 2){
        // $(".namediv").addClass('has-warning');
        // $(".namediv").removeClass('has-success');
        // $(".namediv").removeClass('has-error');
        // $(".namediverror").attr('hidden',true);
        firstname_valid = false;
    }
    else{
        firstname_valid = true;
    }
});

$(".lastname").change(function(){
    lastname = $(".lastname").val();
    if ($.trim(lastname).length < 2){
        // $(".namediv").addClass('has-warning');
        // $(".namediv").removeClass('has-success');
        // $(".namediv").removeClass('has-error');
        // $(".namediverror").attr('hidden',true);
        lastname_valid = false;
    }
    else{
        lastname_valid = true;
    }
});

function validateEmail(email) {
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}


$(".email").change(function(){
    email = $(".email").val();
    if (validateEmail(email)) {
        (function() {
            $.ajax({
                url : "data/" , 
                type: "GET",
                data:{email: email,
                    calltype: "check_email",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                    // contentType: "application/json",
                            // handle a successful response
                success : function(jsondata) {
                    if (jsondata['error'] == "Email exist"){
                        $(".emaildiv").removeClass('has-warning');
                        $(".emaildiv").removeClass('has-success');
                        $(".emaildiv").addClass('has-error');
                        $(".emaildiverror").attr('hidden',false);
                        $(".emailformaterror").attr('hidden',true);
                        email_valid = false;
                    }
                    else if (jsondata['error'] == "Email address is not valid"){
                        $(".emaildiv").addClass('has-warning');
                        $(".emaildiv").removeClass('has-success');
                        $(".emaildiv").removeClass('has-error');
                        $(".emaildiverror").attr('hidden',true);
                        $(".emailformaterror").attr('hidden',false);
                        email_valid = false;
                    }
                    else{
                        $(".emaildiv").removeClass('has-error');
                        $(".emaildiv").removeClass('has-warning');
                        $(".emaildiv").addClass('has-success');
                        $(".emaildiverror").attr('hidden',true);
                        $(".emailformaterror").attr('hidden',true);
                        email_valid = true;
                    }
                },
                    // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
    else{
        $(".emaildiv").addClass('has-warning');
        $(".emaildiv").removeClass('has-success');
        $(".emaildiv").removeClass('has-error');
        $(".emaildiverror").attr('hidden',true);
        $(".emailformaterror").attr('hidden',false);
        email_valid = false;
    }
});

$( ".repeat" ).change(function() {
    repeat_change+=1;
    repeat=$(".repeat").val();
    pass=$(".password").val();
    if (repeat != pass){
        $(".repeatdiv").addClass('has-error');
        $(".repeat-p").attr('hidden',false);
        $(".passworddiv").addClass('has-error');
        repeat_valid = false;
    }
    if (repeat == pass){
        $(".repeatdiv").removeClass('has-error');
        $(".passworddiv").removeClass('has-error');
        $(".repeat-p").attr('hidden',true);
        repeat_valid = true;
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
            repeat_valid = false;
        }
        if (repeat == pass){
            $(".repeatdiv").removeClass('has-error');
            $(".passworddiv").removeClass('has-error');
            $(".repeat-p").attr('hidden',true);
            repeat_valid = true;
        }
    }
});

// $('.password').pwstrength({
    // ui: { showVerdictsInsideProgressBar: true,
    // showErrors: true },
//     minChar: 8
// });

var options = {};
options.common = {
    usernameField: ".username",
    minChar: 8,
    
    onScore: function (options, word, totalScoreCalculated) {
            // If my word meets a specific scenario, I want the min score to
            // be the level 1 score, for example.
        if (word.length === 14 && totalScoreCalculated < options.ui.scores[1] && totalScoreCalculated > -50) {
                // Score doesn't meet the score[1]. So we will return the min
                // numbers of points to get that score instead.
            return options.ui.score[1]
            password_valid = true;
            password_strength = 10;

        }
            // Fall back to the score that was calculated by the rules engine.
            // Must pass back the score to set the total score variable.
        else if (totalScoreCalculated > 4){
                password_valid = true;
                password_strength = 10;
        }
        else{
            password_valid = false;
        }

        return totalScoreCalculated;
    }
};
options.ui =  {
    showVerdictsInsideProgressBar: true,
    showErrors: true
},

$('.password').pwstrength(options);


// $(".password").change(function(){
//     password = $(".password").val();
//     (function() {
//             $.ajax({
//                 url : "data/" , 
//                 type: "GET",
//                 data:{password: password,
//                     calltype: "check_password",
//                     csrfmiddlewaretoken: csrf_token},
//                 dataType: 'json',               
//                     // contentType: "application/json",
//                             // handle a successful response
//                 success : function(jsondata) {
//                     console.log(jsondata)
//                 },
//                     // handle a non-successful response
//                 error : function() {
//                     console.log(jsondata)
//                 }
//             });
//         }());
        
// });

// $(".phone").change(function(){
//     phone_selected = $(".phone").intlTelInput("getNumber")
//     (function() {
//             $.ajax({
//                 url : "data/" , 
//                 type: "GET",
//                 data:{phone: phone_selected,
//                     calltype: "check_phone",
//                     csrfmiddlewaretoken: csrf_token},
//                 dataType: 'json',               
//                     // contentType: "application/json",
//                             // handle a successful response
//                 success : function(jsondata) {
//                     console.log(jsondata);
//                 },
//                     // handle a non-successful response
//                 error : function() {
//                     console.log(jsondata);
//                 }
//             });
//         }());
        
// });

$(".permission").change(function(){
    var count = $(".permission :selected").length;
    if (count < 1){
        permission_valid = false;
    }
    else{
        permission_valid = true;   
    }
        
});


$('.password').bind("cut copy paste",function(e) {
    e.preventDefault();
});

$('.repeat').bind("cut copy paste",function(e) {
    e.preventDefault();
});


$('.submit').click(function(e) {
    // $('.year_error').attr('hidden', true);
    // $('.start_error').attr('hidden', true);
    // $('.end_error').attr('hidden', true);
    // $('.start_end').attr('hidden', true);
    // $('.error_box').attr('hidden', true);
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new user?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new user!",
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
    if (email_valid && password_valid && repeat_valid && number_valid && username_valid && firstname_valid && lastname_valid && permission_valid){
        var proceed=true;
        var username = $('.username').val()
        var firstname = $('.firstname').val()
        var lastname = $('.lastname').val()
        var email = $('.email').val()
        var aadhar = $('.aadhar').val()
        var password = $('.password').val()
        var repeat = $('.repeat').val()
        phone = $(".phone").intlTelInput("getNumber")

        var user_permissions=[];
        $.each($(".permission option:selected"), function(){
            user_type=$(this).data('id');
            // if (customerid == 'undefined' || typeof(customerid) == undefined){
            if ($.trim(user_type).length>0){
                var user_types={
                    user_type: user_type
                };
                user_permissions.push(user_type);
            }        
        });
        // console.log(user_permissions);
        // if (name == '' || name =='undefined' || key == '' || key =='undefined' ){
        //     proceed = false;
        // }
        // if (proceed && number_valid){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{username: username,
                    firstname:firstname,
                    lastname:lastname,
                    email:email,
                    aadhar:aadhar,
                    phone:phone,
                    password:password,
                    repeat:repeat,
                    user_permissions: JSON.stringify(user_permissions),
                    calltype: "newuser",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New customer added", "success");
                        // setTimeout(location.reload(true),1000);
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
        swal("Oops...", "There were some errors. Kindly check the highlighted fields. Also note, fields marked with asterisks (*) must be filled", "error");
    }
}


// $("#customer").on("click", ".link", function(){
//     customerid=$(this).closest('tr').find('td:nth-child(1)').html();
//     $('.update').hide();
//     $('.edit').show();
//     $.ajax({
//         url : "getdata/", 
//         type: "GET",
//         data: { calltype:"one_customer",
//             customerid:customerid},
//         dataType: 'json',
//             // handle a successful response
//         success : function(jsondata) {
//             $('#modal_details').modal('show');
//             console.log(jsondata)
//             $('.id_data').val(jsondata['id'])
//             $('.name_data').val(jsondata['name'])
//             $('.key_data').val(jsondata['key'])
//             $('.add1_data').val(jsondata['address_1'])
//             $('.add2_data').val(jsondata['address_2'])
//             $('.city_data').val(jsondata['city'])
//             $('.pin_data').val(jsondata['pin'])
//             $('.phone_data').val(jsondata['phone_no'])
//             $('.cst_data').val(jsondata['cst'])
//             $('.tin_data').val(jsondata['tin'])
//             $('.gst_data').val(jsondata['gst'])
//             $('.dl1_data').val(jsondata['dl_1'])
//             $('.dl2_data').val(jsondata['dl_2'])
//             $('.remarks').val(jsondata['details'])
//             $('.editable').attr('disabled', true);
//         },
//             // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No customer data exist.", "error");
//         }
//     });
// });

// $('.edit').click(function(e) {
//     $('.editable').attr('disabled', false);
//     $('.edit').hide();
//     $('.update').show();
// });

// $('.edit').change(function(e){
//     change_count=1
// });

});