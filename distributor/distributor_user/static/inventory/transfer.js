$(function(){
vat_type=["No VAT", "On MRP", "On actual"]
var vat_input, vat_percent, unit_data, default_unit, unit_multi={}, unit_names={};

$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "/inventory/getproduct", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            console.log(ui)
            $(el).closest('tr').addClass("updating");
            $(el).closest('tr').find('td:nth-child(2) input').val(ui['item']['id']);
            var unit=$(el).closest('tr').find('td:nth-child(6) :selected').data('id');
            $(el).closest('tr').find('td:nth-child(7)').html(unit_multi[unit]);
            // $(el).closest('tr').find('td:nth-child(8) .unit').val(ui['item']['unit']);
            // vat_input=ui['item']['vat_type']
            // $(el).closest('tr').find('td:nth-child(15) ').html(vat_type[vat_input]);
            // vat_percent=ui['item']['tax']
            // $(el).closest('tr').find('td:nth-child(16) ').html(vat_percent);
            // $('.unit').selectpicker('refresh');
            get_product_warehouse(el, ui['item']['id'])
        }
    });
});


function get_product_warehouse(el, product_id){
    warehouse_id=$('.from').find(':selected').data('id');
    // console.log(warehouse_id)
    $.ajax({
        url : "/inventory/getproductinventory", 
        type: "GET",
        data:{product_id: product_id,
            warehouse_id: warehouse_id},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $(".prod_data .prod_indi_data").remove();
            console.log(jsondata);
            $.each(jsondata, function(){
                $('.prod_data').append("<tr class='prod_indi_data'>"+
                "<td class='prod_pur'>"+this.purchase_price +"</td>"+
                "<td class='prod_tsp'>"+this.tentative_sales_price +"</td>"+
                "<td class='prod_mrp'>"+this.mrp+"</td>"+
                "<td class='prod_qa'>"+this.quantity_available+"</td>"+
                "<td class='prod_pd'>"+this.purchase_date+"</td>"+
                "<td class='prod_id' hidden>"+this.id+"</td>"+
                "</tr>");
            })
            $('#productdetails').modal('show');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product inventory exist.", "error");
        }
    });
}

$('.prod_data').on('click','.prod_indi_data', function(){
    // console.log('clicked');
    updating_row=$('.details').find('.updating')
    pr=$(this).closest('tr').find('td:nth-child(1)').html()
    tsp=$(this).closest('tr').find('td:nth-child(2)').html()
    mrp=$(this).closest('tr').find('td:nth-child(3)').html()
    qty_avl=$(this).closest('tr').find('td:nth-child(4)').html()
    date=$(this).closest('tr').find('td:nth-child(5)').html()
    inv_id=$(this).closest('tr').find('td:nth-child(6)').html()
    $(updating_row).find('td:nth-child(5)').html(qty_avl);
    $(updating_row).find('td:nth-child(8)').html(pr);
    $(updating_row).find('td:nth-child(9)').html(tsp);
    $(updating_row).find('td:nth-child(10)').html(mrp);
    $(updating_row).find('td:nth-child(11)').html(date);
    $(updating_row).find('td:nth-child(12)').html(inv_id);
    $(updating_row).removeClass('updating');
    $('#productdetails').modal('hide');
    // console.log(mrp)
});

load_warehouse()

function load_warehouse(){
    $.ajax({
        url : "/master/warehouse/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            $.each(jsondata, function(){
                $('#from_warehouse').append($('<option>',{
                    'data-id': this.id,
                    'text': this.address_1 + " "+ this.address_2
                }));
                $('#to_warehouse').append($('<option>',{
                    'data-id': this.id,
                    'text': this.address_1 + " "+ this.address_2
                }));
            });
            $('#from_warehouse').selectpicker('refresh')
            $('#to_warehouse').selectpicker('refresh')
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
                unit_multi[this.id]=parseFloat(this.multiplier);
                unit_names[this.id]=this.name;
                $('#unit').append($('<option>',{
                    'data-id': this.id,
                    'title':this.symbol,
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

$('.details').on("mouseenter", ".first", function() {
    $( this ).children( ".delete" ).show();
});

$('.details').on("mouseleave", ".first", function() {
    $( this ).children( ".delete" ).hide();
});

$('.details').on("click", ".delete", function() {
    $(this).parent().parent().remove();
});

$('.addmore').click(function(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<th colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></th>'+
    '<td hidden=""><input class="id"></td>'+
    '<td colspan="3"><input class="form-control name"></td>'+
    '<td colspan="1"><input class="form-control qty"></td>'+
    '<td colspan="1" hidden></td>'+
    '<td colspan="1"><select class="form-control selectpicker unit" id="unit"></select></td>'+
    '<td colspan="1" hidden></td>'+
    '<td colspan="1" class="pr"></td>'+
    '<td colspan="1" class="tsr"></td>'+
    '<td colspan="1" class="mrp"></td>'+
    '<td colspan="1" class="pur_date"></td>'+
    '<td colspan="1" hidden class="inv_id"></td>'+
    '</tr>';
    $('.details').append(data);

    // $('.dt').selectpicker('refresh');
    
    $.each(unit_data, function(){
        $('.details').find('tr:eq('+count+')').find('#unit').append($('<option>',{
            'data-id': this.id,
            'title':this.symbol,
            'text': this.name,
        }));
    });
    $('.unit').selectpicker('refresh');
})



$(".details").on("change", ".unit", function(){
    var unit_id = $(this).find(':selected').data('id');
    unit_multi_selected=unit_multi[unit_id]
    $(this).closest('tr').find('td:nth-child(7)').html(unit_multi_selected);
    get_qty_avl(this);
});

$(".details").on("keyup", ".qty", function(){
    var el=this;
    get_qty_avl(el);
});
$(".details").on("keydown", ".qty", function(){
    var el=this;
    get_qty_avl(el);
});


function get_qty_avl(el){
    var unit_id = $(el).closest('tr').find('td:nth-child(6) .unit :selected').data('id');
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(5)').html());
    if (isNaN(quantity_avl)){
        quantity_avl=0;
    }
    var unit_multi_selected = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());
    quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            console.log("here");
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than available quantity. <br>"+
                        " Total available quantity: "+quantity_avl.toFixed(2)+" "+unit_names[unit_id]+".",
                type: "warning",
                showCancelButton: false,
                closeOnConfirm: true,
                closeOnCancel: true,
                html: true,
            });
            $(el).closest('tr').addClass("has-error");
            return false;
        }
        else{
            $(el).closest('tr').removeClass("has-error");
            return true;
        }
    }
    if ((quantity)<=quantity_avl){
        $(el).closest('tr').removeClass("has-error");
        return true;
    }
}

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to create a new receipt?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add create new receipt!",
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
    var items=[];
    var proceed=true;
    var from_warehouseid=$('.from').find(':selected').data('id');
    var to_warehouseid=$('.to').find(':selected').data('id');
    var date=$('.date').val()
    var record_transit = $('.transit').is(":checked");
    
    if (from_warehouseid == '' || typeof(from_warehouseid) =='undefined' ||
        to_warehouseid == '' || typeof(to_warehouseid) =='undefined' || date == '' || typeof(date) =='undefined'){
        proceed = false;
        swal("Oops...", "Please select from & to warehouse and date of the challan.", "error");
    }
    if (from_warehouseid == to_warehouseid){
        proceed = false;
        swal("Oops...", "From and to warehouses cannot be same.", "error");
    }
    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(2) input').val();
        if (product_id == '' || typeof(product_id) =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a product ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var quantity = $(this).find('td:nth-child(4) input').val();
        if (quantity == '' || quantity =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var qty_proceed= get_qty_avl(this);
        
        if (!qty_proceed){
            swal("Oops...", "You don't have enough quantity available. ", "error");
            proceed=false;
        }

        var unit_id = $(this).find('td:nth-child(6) :selected').data('id');
        if (unit_id == '' || unit_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter the purchase unit ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var inventory_id = $(this).find('td:nth-child(12)').html();

        var item = {
            product_id : product_id,
            quantity: quantity,
            unit_id: unit_id,
            inventory_id: inventory_id,
        };
        items.push(item);
    });
    console.log(items)

    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{from_warehouseid:from_warehouseid,
                    to_warehouseid: to_warehouseid,
                    date:date.split("/").reverse().join("-"),
                    record_transit:record_transit,
                    all_details: JSON.stringify(items),
                    calltype: "newtransfer",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New purchase receipt added", "success");
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
    
}

});