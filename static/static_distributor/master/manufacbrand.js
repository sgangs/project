$(function(){

load_manufacturer()

load_brand()

function load_manufacturer(){
    $.ajax({
        url : "manufacdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata)
            $.each(jsondata, function(){
                    $('#manufacturer').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "</tr>");
                    $('.manufac').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.name
                        }));
                    $('.manufac').selectpicker('refresh')
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No manufacturer data exist.", "error");
        }
    });
}

function load_brand(){
    $.ajax({
        url : "branddata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#brand').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.manufacturer+"</td>"+
                    "</tr>");
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No brand data exist.", "error");
        }
    });
}


var manname ='';


$('.submitman').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new manufacturer?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new manufacturer!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_man()},600)            
        }
    })
});
    
function new_man(){
    var proceed=true;
    manname=$('.manname').val()
    
    if (manname == '' || manname =='undefined'){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: manname,
                    calltype: "newmanufacturer",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New manufacturer added", "success");
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
        swal("Oops...", "Please note that name must be filled.", "error");
    }
}


var name ='', symbol ='', multiplier=0, dimension=0;


$('.submitunit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new brand",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new brand!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_unit()},600)            
        }
    })
});
    
function new_unit(){
    var proceed=true;
    name=$('.brandname').val()
    manufacturer=$(".manufac").find(':selected').data('id');
    
    if (name == '' || name =='undefined' || isNaN(manufacturer) || manufacturer <=0){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: name,
                    manufacturer:manufacturer,
                    calltype: "newbrand",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New unit added", "success");
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
        swal("Oops...", "Please note that all the fields must be filled and multiplier must be greater than zero.", "error");
    }
}


});