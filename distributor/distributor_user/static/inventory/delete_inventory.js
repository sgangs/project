$(function(){

// load_current_inventory()


$(document).on('keydown.autocomplete', '.product_name', function() {
    var el=this;
    $(this).autocomplete({
        source : "/inventory/getproduct/", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            $('.product_id').val(ui['item']['id']);
        }
    });
});


$('.get_data').click(function load_movement(){
    product=$('.product_id').val()
    date=$('.date').val()
    var proceed = true;
    if ($.trim(product).length == 0 || typeof(product) == 'undefined'){
        proceed=false;
    }
    if (proceed){
        $.ajax({
            url : "/inventory/openinginventory/product/data/",
            type: "GET",
            data:{calltype: 'product',
                product_id: product,},
            dataType: 'json',
                // handle a successful response
            success : function(jsondata) {
                $('.inventory').attr('hidden',false);
                $(".opening_inventory .data").remove();
                $.each(jsondata, function(){
                    $('.opening_inventory').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.warehouse__address_1+", "+this.warehouse__address_2+"</td>"+
                    "<td>"+this.quantity+"</td>"+
                    "<td>Rs."+this.purchase_price+"</td>"+
                    "<td>Rs."+this.tentative_sales_price+"</td>"+
                    "<td>Rs."+this.mrp+"</td>"+
                    "<td><input class='form-control revised_qty' value="+this.quantity+"></td>"+
                    "<td class='qty_reduced'>0</td>"+
                    "</tr>");
                })
            },
                // handle a non-successful response
            error : function() {
                swal("Oops...", "There was an error.", "error");
            }
        });
    }
    else{
        swal("Oops...", "Select a product first", "error");
    }
});



$(".opening_inventory").on("keyup", ".revised_qty", function(){
    var el=this;
    get_quantity(el, 'update');    
});
$(".opening_inventory").on("keydown", ".revised_qty", function(){
    var el=this;
    get_quantity(el, 'update');
});

function get_quantity(el, called_for) {
    var original_quantity =  parseFloat($(el).closest('tr').find('td:nth-child(3)').html());
    var revised_quantity =  parseFloat($(el).closest('tr').find('td:nth-child(7) input').val());

    if (isNaN(revised_quantity)){
        if (called_for == 'final_check'){
            $(el).closest('tr').addClass("has-error");
            return false;
        }
        revised_quantity = original_quantity;
    }
    
    var quantity_reduced = original_quantity - revised_quantity
    if (revised_quantity < 0 || revised_quantity > original_quantity){
        if (!$(el).closest('tr').hasClass("has-error")){
            $(el).closest('tr').addClass("has-error");
            $(el).closest('tr').find('td:nth-child(8)').html(0);
            swal("Oops...", "Revised Quantity cannot be greater than original quantity or less than zero.", "error"); 
        }
        return false;
    }
    else{
        if (quantity_reduced <= original_quantity && quantity_reduced >= 0){
             
            $(el).closest('tr').find('td:nth-child(8)').html(quantity_reduced);
            $(el).closest('tr').removeClass("has-error");
            return true;
        }
    }
}

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to update opening inventory? This may result in negative stock between opening inventory and current date.</p>"+
                "<p>Please understand that this is not good practise.</p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update inventory!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)            
        }
    })
});

function reconfirm(e) {
    swal({
        title: "Please Reconmfim?",
        text: "Please reconfirm that you understand what you're doing.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update inventory!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){submit_data()},600)            
        }
    })
};


function submit_data(){
    var items=[];
    var proceed = true;
    
    $(".opening_inventory tr.data").each(function() {
        var check_line = true;
        var inventory_id = $(this).find('td:nth-child(1)').html();
        var original_quantity = parseFloat($(this).find('td:nth-child(3)').html());
        var revised_quantity = parseFloat($(this).find('td:nth-child(7) input').val());
        var quantity_reduced = parseFloat($(this).find('td:nth-child(8)').html());
        console.log(revised_quantity)
        if (isNaN(revised_quantity)){
            proceed = false;
            $(this).closest('tr').addClass("has-error");
        }
        // else if (quantity_reduced != 0 && !isNaN (quantity_reduced) && !isNaN(revised_quantity)){
        else{
            check_line = get_quantity(this, 'final_check');
            console.log(check_line)
            if (quantity_reduced>0){
                var item = {
                    inventory_id : inventory_id,
                    revised_qty: revised_quantity,
                };
                items.push(item);
            }
        }
        // else{
        //     proceed = false;
        // }
        if (!check_line){
            console.log('here')
            proceed = false;
        }
    });

    if (items.length == 0){
        swal("Oops...", "No data changed for updation.", "warning");
        proceed = false;
    }

    console.log(items);
    console.log(proceed);

    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{inventory_id_list: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                
                success : function(jsondata) {
                    var show_success=jsondata['result']
                    console.log(show_success)
                    if (show_success){
                        swal("Hooray", "Opening quantity updated.", "success");
                        setTimeout(location.reload(true),1500);
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
        swal("Oops...", "Either no data were changed for updation or there were some errors in the highlighted rows.", "error");
    }
}




});