$(function(){
var change=0;
var states=[];

load_states()

function load_states(){
    $.ajax({
        url : "/master/getstatelist/", 
        type: "GET",
        // data: { calltype:"all_vendor"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            states=jsondata;
            load_vendors();
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some issues.", "error");
        }
    });
}

// load_vendors()

function load_vendors(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data: { calltype:"all_vendor"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                if (typeof(states[this.state]) == 'undefined'){
                    $('#vendor').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.name+"</td>"+
                    "<td>"+this.key+"</td>"+
                    "<td>"+this.address_1+", "+$.trim(this.address_2)+ ", "+this.city +": "+this.pin+"</td>"+
                    "<td>"+this.phone_no+"</td>"+
                    "</tr>");
                }
                else{
                    $('#vendor').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.name+"</td>"+
                    "<td>"+this.key+"</td>"+
                    "<td>"+this.address_1+", "+ $.trim(this.address_2)+", "+states[this.state]+ ", "+this.city +": "+this.pin+"</td>"+
                    "<td>"+this.phone_no+"</td>"+
                    "</tr>");
                }
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No vendor data exist.", "error");
        }
    });
}

var name ='', key='', address_1 ='', address_2='', state='', city='', phone='', cst='', tin='', gst='', details='',
    number_valid=true, number_update_valid=true;

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
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new vendor?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new vendor!",
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
    name=$('.name').val();
    key=$('.key').val();
    ismanufac=$('.ismanufac').is(":checked");
    address_1=$('.add1').val();
    address_2=$('.add2').val();
    state=$(".state").find(':selected').data('id');
    city=$('.city').val();
    pin=$('.pin').val();
    cst=$('.cst').val();
    tin=$('.tin').val();
    gst=$('.gst').val();
    details=$('.details').val();
    if (name == '' || name =='undefined' || key == '' || key =='undefined' ){
        proceed = false;
    }
    if (proceed && number_valid){
        (function() {
            $.ajax({
                url : "getdata/" , 
                type: "POST",
                data:{name: name,
                    key:key,
                    ismanufac:ismanufac,
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
                    calltype: "newvendor",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New Vendor added", "success");
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

$("#vendor").on("click", ".link", function(){
    vendorid=$(this).closest('tr').find('td:nth-child(1)').html();
    $('.update').hide();
    $('.edit').show();
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data: { calltype:"one_vendor",
            vendorid:vendorid},
        dataType: 'json',
            // handle a successful response
        success : function(jsondata) {
            $('#modal_details').modal('show');
            console.log(jsondata)
            $('.id_data').val(jsondata['id'])
            $('.name_data').val(jsondata['name'])
            $('.key_data').val(jsondata['key'])
            $('.add1_data').val(jsondata['address_1'])
            $('.add2_data').val(jsondata['address_2'])
            $('.city_data').val(jsondata['city'])
            $('.pin_data').val(jsondata['pin'])
            $('.phone_data').val(jsondata['phone_no'])
            $('.cst_data').val(jsondata['cst'])
            $('.tin_data').val(jsondata['tin'])
            $('.gst_data').val(jsondata['gst'])
            $('.details_data').val(jsondata['details'])
        },
            // handle a non-successful response
        error : function() {
            swal("Oops...", "No vendor data exist.", "error");
        }
    });
});

$('.edit').click(function(e) {
    $('.editable').attr('disabled', false);
    $('.edit').hide();
    $('.update').show();
});

var telUpdateInput = $('.phone_data'), errorUpdateMsg = $("#error-data-msg"), validUpdateMsg = $("#valid-data-msg");

var reset = function() {
  telUpdateInput.removeClass("error");
  errorUpdateMsg.addClass("hide");
  validUpdateMsg.addClass("hide");
}

     
telUpdateInput.blur(function() {
    reset();
    phone_update_check  
});

function phone_update_check(){
    if ($.trim(telUpdateInput.val())) {
        if (telUpdateInput.intlTelInput("isValidNumber")) {
          validUpdateMsg.removeClass("hide");
          number_update_valid=true;
          phone_data=telUpdateInput.intlTelInput("getNumber");
        } else {
          telUpdateInput.addClass("error");
          errorUpdateMsg.removeClass("hide");
          number_update_valid=false;
        }
    }
}


$('.update').click(function(e) {
    
    swal({
        title: "Are you sure?",
        text: "Are you sure to u[date customer data?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update data!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){update_data()},600)            
        }
    })
});

function update_data(){
    var proceed_update=true;
    pk=$('.id_data').val()
    name_data=$('.name_data').val()
    key_data=$('.key_data').val()
    address_1_data=$('.add1_data').val()
    address_2_data=$('.add2_data').val()
    // state=$(".state").find(':selected').data('id');
    city_data=$('.city_data').val()
    pin_data=$('.pin_data').val()
    cst_data=$('.cst_data').val()
    tin_data=$('.tin_data').val()
    gst_data=$('.gst_data').val()
    details_data=$('.details_data').val()
    phone_update_check();

    if (name_data == '' || name_data =='undefined' || key_data == '' || key_data =='undefined' ){
        proceed_update = false;
        console.log('Here');
    }
    if (proceed_update && number_update_valid){
        (function() {
            $.ajax({
                url : "getdata/" , 
                type: "POST",
                data:{pk: pk,
                    name: name_data,
                    key:key_data,
                    address_1:address_1_data,
                    address_2:address_2_data,
                    // state:state,
                    city:city_data,
                    pin:pin_data,
                    phone:phone_data,
                    cst:cst_data,
                    tin:tin_data,
                    gst:gst_data,
                    details:details_data,
                    calltype: "updatevendor",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Vendor data updated.", "success");
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