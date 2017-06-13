$(function(){

load_dimension()

load_unit()

function load_dimension(){
    $.ajax({
        url : "dimensiondata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#dimension').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.details+"</td>"+                    
                    "</tr>");
                    // $('.dim').append($('<option/>',{
                    //     'data-id': this.id,
                    //     'text': this.name
                    //     }));
                    // $('.dim').selectpicker('refresh')
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No dimension data exist.", "error");
        }
    });
}

function load_unit(){
    $.ajax({
        url : "unitdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#unit').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.symbol+"</td>"+
                    "<td>"+this.multiplier+"</td>"+
                    "<td>"+this.dimension+"</td>"+
                    "</tr>");
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No unit data exist.", "error");
        }
    });
}


var dimname ='', dimdetails ='';


$('.submitdim').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new dimension?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new dimension!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_dim()},600)            
        }
    })
});
    
function new_dim(){
    var proceed=true;
    dimname=$('.dimname').val()
    dimdetails=$('.details').val()
    
    if (name == '' || name =='undefined'){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: name,
                    details:details,
                    calltype: "newdimension",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New dimension added", "success");
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


var name ='', symbol ='', multiplier=0, dimension=0;


$('.submitunit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new unit",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new unit!",
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
    name=$('.unitname').val()
    symbol=$('.symbol').val()
    multiplier=$('.multi').val()
    dimension=$(".dim").find(':selected').data('id');
    console.log(name);
    console.log(symbol);
    console.log(multiplier);
    
    if (name == '' || name =='undefined' || symbol == '' || symbol =='undefined' || isNaN(multiplier) || multiplier <=0 ||
            isNaN(dimension) || dimension <=0){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: name,
                    symbol:symbol,
                    multiplier: multiplier,
                    dimension:dimension,
                    calltype: "newunit",
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