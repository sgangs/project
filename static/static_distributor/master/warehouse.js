$(function(){


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
            load_warehouse();
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some issues.", "error");
        }
    });
}

// load_warehouse()

function load_warehouse(){
    console.log("here");
    $.ajax({
        url : "getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                console.log(jsondata);
                if (typeof(states[this.state]) == 'undefined'){
                    $('#warehouse').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.address_1+", "+$.trim(this.address_2)+ ", "+this.city +": "+this.pin+"</td>"+
                    "<td>"+this.default+"</td>"+
                    "</tr>");
                }
                else{
                    $('#warehouse').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.address_1+", "+ $.trim(this.address_2)+", "+states[this.state]+ ", "+this.city +": "
                        +this.pin+"</td>"+
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


$('.submit').click(function(e) {
    // $('.year_error').attr('hidden', true);
    // $('.start_error').attr('hidden', true);
    // $('.end_error').attr('hidden', true);
    // $('.start_end').attr('hidden', true);
    // $('.error_box').attr('hidden', true);
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new warehouse?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new warehouse!",
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
    var name=$('.name').val()
    var address_1=$('.add1').val()
    var address_2=$('.add2').val()
    var state=$(".state").find(':selected').data('id');
    var city=$('.city').val()
    var pin=$('.pin').val()
    var remarks=$('.remarks').val()
    var retail = $('.retail').is(":checked");
    
    if (name == '' || typeof(name) =='undefined' || address_1 == '' || typeof(address_1) =='undefined' ){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: name,
                    address_1:address_1,
                    address_2:address_2,
                    state:state,
                    city:city,
                    pin:pin,
                    remarks:remarks,
                    retail:retail,
                    calltype: "newwarehouse",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New warehouse added", "success");
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