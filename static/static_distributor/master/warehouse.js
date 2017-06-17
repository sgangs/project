$(function(){

load_warehouse()

function load_warehouse(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                if (this.address_2 == null){
                    $('#warehouse').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.address_1+", "+this.state+ ", "+this.city +": "+this.pin+"</td>"+
                    "<td>"+this.default+"</td>"+
                    "</tr>");
                }
                else{
                    $('#warehouse').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.address_1+", "+ this.address_2+", "+this.state+ ", "+this.city +": "+this.pin+"</td>"+
                    "<td>"+this.default+"</td>"+
                    "</tr>");
                }
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
        }
    });
}


var name ='', key='', address_1 ='', address_2='', state='', city='', phone='', cst='', tin='', gst='', details='', zone='', 
    number_valid=true;

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

$('.submit').click(function(e) {
    // $('.year_error').attr('hidden', true);
    // $('.start_error').attr('hidden', true);
    // $('.end_error').attr('hidden', true);
    // $('.start_end').attr('hidden', true);
    // $('.error_box').attr('hidden', true);
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new customer?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new customer!",
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
    name=$('.name').val()
    key=$('.key').val()
    address_1=$('.add1').val()
    address_2=$('.add2').val()
    state=$(".state").find(':selected').data('id');
    city=$('.city').val()
    pin=$('.pin').val()
    cst=$('.cst').val()
    tin=$('.tin').val()
    gst=$('.gst').val()
    details=$('.details').val()
    zone=$(".zone").find(':selected').data('id');
    // var year=parseInt($('.year').val());
    // var start=$('.start').val();
    // var end=$('.end').val();
    // var current = $('.current').is(":checked");
    
    if (name == '' || name =='undefined' || key == '' || key =='undefined' ){
        proceed = false;
    }
    if (proceed && number_valid){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: name,
                    key:key,
                    address_1:address_1,
                    address_2:address_2,
                    state:state,
                    city:city,
                    pin:pin,
                    phone:phone,
                    cst:cst,
                    tin:tin,
                    gst:gst,
                    details:details,
                    zone:zone,
                    calltype: "newcustomer",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New customer added", "success");
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
        swal("Oops...", "Please note that name & key must be filled and phone number must be valid", "error");
    }
}



    
});