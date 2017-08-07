$(function(){

// $( ".addresspicker" ).autocomplete( "option", "appendTo", ".eventInsForm" );

$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "/inventory/getproduct/", 
        minLength: 3,
        timeout: 300,
        // appendTo: ".name"
        select: function( event, ui ) {
            $('.nameid').val(ui['item']['id']);
        }
    });
});

load_warehouse()

function load_warehouse(){
    $.ajax({
        url : "/master/warehouse/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#warehouse').append($('<option>',{
                    'data-id': this.id,
                    'text': this.address_1 + " "+ this.address_2
                }));
            });
            $('#warehouse').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
        }
    });
}

load_units()

function load_units(){
    $.ajax({
        url : "/master/dimensionunit/unitdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            unit_data=jsondata
            $.each(jsondata, function(){
                $('#unit').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name,
                }));
            });
            $('#unit').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No unit is registered.", "error");
        }
    });
}

load_inventory()

function load_inventory(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#opening_inventory').append("<tr class='data text-center'>"+
                    "<td>"+this.product+"</td>"+
                    "<td>"+this.warehouse+"</td>"+
                    "<td>"+this.quantity+"</td>"+
                    "<td>"+this.purchase_price+"</td>"+
                    "<td>"+this.tentative_sales_price+"</td>"+
                    "<td>"+this.mrp+"</td>"+
                    "</tr>");
            });            
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No opening inventory registered.", "error");
        }
    });
}


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to update your joining invoice?<p>Note that you cannot reduce this inventory value</p>",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update joining inventory!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data()},600)            
        }
    })
});
    
function new_data(){
    var proceed=true;
    productid=$('.nameid').val();
    if (productid == '' || productid =='undefined' ){
        proceed = false;
        swal("Oops...", "Please enter a product", "error");
    }
    warehouseid=$('.warehouse').find(':selected').data('id');
    if (warehouseid == '' || warehouseid =='undefined' ){
        proceed = false;
        swal("Oops...", "Please select a warehouse", "error");
    }
    unitid=$('.unit').find(':selected').data('id');
    if (unitid == '' || unitid =='undefined' ){
        proceed = false;
        swal("Oops...", "Please select an unit", "error");
    }
    date=$('.date').val();
    quantity=parseInt($('.qty').val())
    if (isNaN(quantity) ){
        proceed = false;
        swal("Oops...", "Please enter a quantity", "error");
    }
    // manu_date=$('.manu').val()
    // expiry_date=$('.expiry').val()
    // serial=$('.serial').val()
    purchase=parseFloat($('.purchase').val())
    if (isNaN(purchase)){
        proceed = false;
        swal("Oops...", "Please enter a purchase price", "error");
    }
    tsp=$('.tsp').val()
    mrp=$('.mrp').val()

    // console.log(date);
    // console.log(date.split("/").reverse().join("-"));
    
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{productid: productid,
                    warehouse:warehouseid,
                    unit:unitid,
                    quantity:quantity,
                    date:date.split("/").reverse().join("-"),
                    purchase: purchase,
                    tsp: tsp,
                    mrp: mrp,
                    calltype: "newinventory",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Inventory updated", "success");
                        // $('.new_val').val(''); -->Try this
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
        swal("Oops...", "Please enter warehouse data and product details.", "error");
    }
}


});