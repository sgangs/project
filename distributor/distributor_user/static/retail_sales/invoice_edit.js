$(function(){
vat_type=["No VAT", "On MRP", "On actual"];
vat_type_reverse={"No VAT":0, "On MRP":1, "On actual":2};
var vat_input, vat_percent, unit_data, unit_multi={}, maintain_inventory, unit_names={};

function round_off(value){
    value=parseInt(value*1000)/1000
    value=parseFloat(value.toFixed(2))
    return value
}


$('.get_invoice').click(function(){
    invoice_no=$('.invoice_no').val();
    
    $.ajax({
        url : "/retailsales/invoice/invoicenodetails/", 
        type: "GET",
        data:{invoice_no: invoice_no,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $(".details .data").remove();
            $('.invoice_pk').html(jsondata['id'])
            $.each(jsondata['line_items'], function(){
                $('.details').append("<tr class='data text-center'>"+
                    '<td hidden>'+this.product+'</td>'+
                    '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
                    '<td colspan="1"><input class="form-control" value="'+this.product_name+'" disabled></td>'+
                    '<td colspan="1"><input class="form-control qty" value="'+this.quantity+'" width="15%"></td>'+
                    '<td colspan="1" class="qty_avl" hidden>'+parseFloat(this.quantity)+'</td>'+
                    '<td colspan="1">'+this.unit+'</td>'+ //Change this to unit_id later on.
                    '<td colspan="1" class="unit_multiplier">'+this.unit_multi+'</td>'+
                    '<td colspan="1"><input class="form-control sr" value="'+this.sales_price+'" width="15%"></td>'+
                    '<td colspan="1" hidden><input class="form-control da"></td>'+
                    '<td colspan="1" class="total" hidden>0.00</td>'+
                    '<td colspan="1" width="10%"><input type="checkbox" class="is_tax"/></td>'+
                    '<td colspan="1" width="10%"><input class="form-control cgstp" value="'+this.cgst_percent+'"></td>'+
                    '<td colspan="1" class="cgstv">'+this.cgst_value+'</td>'+
                    '<td colspan="1" width="10%"><input class="form-control sgstp" value="'+this.sgst_percent+'"></td>'+
                    '<td colspan="1" class="sgstv">'+this.sgst_value+'</td>'+
                    '<td colspan="1" class="tv">'+this.line_total+'</td>'+
                    '</tr>'
                )
            });
            $('.total_receipt').html(jsondata['total']);        
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Please cehck the invoice no. No data exist.", "error");
        }
    });
})

// load_units()

// function load_units(){
//     $.ajax({
//         url : "/master/dimensionunit/unitdata/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             unit_data=jsondata
//             $.each(jsondata, function(){
//                 unit_multi[this.id]=parseFloat(this.multiplier);
//                 unit_names[this.id]=this.name;
//                 $('#unit').append($('<option>',{
//                     'data-id': this.id,
//                     'title':this.symbol,
//                     'text': this.name,
//                 }));
//             });
//             $('#unit').selectpicker('refresh');
//             // $('#unit').html('refresh',true);
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No unit is registered.", "error");
//         }
//     });
// }


$('.details').on("mouseenter", ".first", function() {
    $( this ).children( ".delete" ).show();
});

$('.details').on("mouseleave", ".first", function() {
    $( this ).children( ".delete" ).hide();
});

$('.details').on("click", ".delete", function() {
    $(this).parent().parent().remove();
    get_total();
});

$(".details").on("keyup", ".qty", function(){
    var el=this;
    get_total();
    get_qty_avl(el);
});
$(".details").on("keydown", ".qty", function(){
    var el=this;
    get_total();
    get_qty_avl(el);
});


$(".details").on("keyup", ".sr", function(){
    get_total();
});
$(".details").on("keydown", ".sr", function(){
    get_total();
});
$(".details").on("change", ".is_tax", function(){
    get_total();
});

// $(".details").on("keyup", ".dv", function(){
//     get_total();
// });

// $(".details").on("keydown", ".dv", function(){
//     get_total();
// });


// $(".details").on("change", ".unit", function(){
//     var unit_id = $(this).find(':selected').data('id');
//     unit_multi_selected=unit_multi[unit_id]
//     $(this).closest('tr').find('td:nth-child(7)').html(unit_multi_selected);
//     if (maintain_inventory){
//         var el=this;
//         get_qty_avl(el);
//     }
//     // get_total();
// });



function get_qty_avl(el){
    var unit_name = $(el).closest('tr').find('td:nth-child(6)').html();
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(5)').html());
    if (isNaN(quantity_avl)){
        quantity_avl=0;
    }
    // var free = parseInt($(el).closest('tr').find('td:nth-child(6) input').val());
    // if (isNaN(free)){
        // free=0;
    // }
    // var free_tax = parseInt($(el).closest('tr').find('td:nth-child(7) input').val());
    // if (isNaN(free_tax)){
        // free_tax=0;
    // }
    var unit_multi_selected = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());
    quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            // var unit_symbol=$(el).closest('tr').find('td:nth-child(6) input').val();
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than original invoice quantity. <br>"+
                        " Total original quantity: "+quantity_avl+" "+unit_name+".",
                        // " Total original quantity: "+quantity_avl+" "+unit_name[unit_id]+".",                        
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



function get_total(){
    var subtotal=0, total=0, tax_total=0;
    var i =0;
    for (var a = document.querySelectorAll('table.details tbody tr'), i = 0; a[i]; ++i) {
        // get all cells with input field
        cells = a[i].querySelectorAll('input:last-child');
        
        var quantity=parseFloat($(cells[1]).val());
        // console.log(quantity)
        var qty_avl=parseFloat($(a[i]).find('td:nth-child(5)').html());
        
        var sales_rate=$(cells[2]).val()
        // console.log(sales_rate)
        
        // discount_type=$(a[i]).find('td:nth-child(11) :selected').data('id');
        // discount_val=$(cells[4]).val();
        discount_amt=$(cells[3]).val();
        
        cgst_percent=parseFloat($(cells[5]).val());
        sgst_percent=parseFloat($(cells[6]).val());

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        
        if(isNaN(sales_rate)){
            sales_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        
        var this_total=quantity*sales_rate
        
        // sales_disc_rate=sales_rate
        
        // if(discount_type == 2){
        //     sales_disc_rate=sales_disc_rate - discount_val/quantity;
        //     this_total=(this_total - discount_val);
        // }
        // is_tax=$(a[i]).find('td:nth-child(11)').html()
        is_tax = $(a[i]).find('td:nth-child(11) input').is(":checked")

        // console.log(is_tax);

        discount_amt=$(a[i]).find('td:nth-child(9) input').val()
        
        // sales_disc_rate=sales_disc_rate - discount_val/quantity;
        this_total=(this_total - discount_amt);
        // console.log(this_total)

        // console.log(i+": "+is_tax)
        
        if (is_tax) {
            total_tax_per=cgst_percent+sgst_percent
            total_tax_divider=(100+total_tax_per)/100
            tax_total=round_off(this_total-this_total/total_tax_divider)
            cgst_total=round_off(tax_total/2);
            sgst_total=round_off(tax_total/2);
            this_final_total=round_off(this_total);
            total+=this_final_total
            subtotal+=this_final_total-(cgst_total+ sgst_total)
            this_total = this_total - (cgst_total+ sgst_total)
        }
        else{
            cgst_total=round_off((this_total*cgst_percent)/100);
            sgst_total=round_off((this_total*sgst_percent)/100);
            tax_total = cgst_total+sgst_total;
            this_final_total=this_total+cgst_total+sgst_total;
            total+=this_final_total
            subtotal+=this_final_total-tax_total
        }
        // console.log(i+": "+tax_total)
        // console.log(i+": "+total)
        
        $(a[i]).find('td:nth-child(13) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(15) ').html(sgst_total.toFixed(2))
        
        $(a[i]).find('td:nth-child(10) ').html(this_total.toFixed(2))
        
        $(a[i]).find('td:nth-child(16) ').html(this_final_total.toFixed(2))
        
    }
    // console.log(total)
    // console.log(subtotal)
    subtotal = round_off(subtotal)
    total = round_off(total)
    
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.total_receipt').html(total.toFixed(2))
};


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to update the sales invoice?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update sales invoice!",
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
    var cgst_total_sum=0
    var sgst_total_sum=0
    var items=[];
    var proceed=true;
    
    subtotal=parseFloat($('.subtotal_receipt').html());
    // taxtotal=parseFloat($('.taxtotal_receipt').html());
    total=parseFloat($('.total_receipt').html());

    invoice_pk=$('.invoice_pk').html();
    
    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(1)').html();
        console.log(product_id);
        if (product_id == '' || product_id =='undefined'){
            proceed=false;
            console.log(product_id);
            swal("Oops...", "There are some error. ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var quantity = parseFloat($(this).find('td:nth-child(4) input').val());
        var quantity_avl = parseFloat($(this).find('td:nth-child(5)').html());
        if (isNaN(quantity)){
            proceed=false;
            console.log('here');
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        
        var qty_proceed= get_qty_avl(this);
        if (!qty_proceed){
            swal("Oops...", "Revised quantity cannot be more than original invoice quantity. Please generate new invoice in that case. ", "error");
            proceed=false;
        }
        
        var sales = parseFloat($(this).find('td:nth-child(8) input').val());
        if (isNaN(sales)){
            proceed=false;
            console.log('here');
            swal("Oops...", "Please enter a sales rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        var unit_name = $(this).find('td:nth-child(6)').html();
        var unit_multi = $(this).find('td:nth-child(7)').html();

        // var disc_type = $(this).find('td:nth-child(11) :selected').data('id');
        // var disc = parseFloat($(this).find('td:nth-child(12) input').val());
        // if (isNaN(disc)){
        //     disc=0;
        // }

        // var disc_amt = parseFloat($(this).find('td:nth-child(9) input').val());

        // if (isNaN(disc_amt)){
        //     disc_amt=0
        // }
        var disc_amt=0

        var is_tax = $(this).find('td:nth-child(11) input').is(":checked");

        var cgst_p = parseFloat($(this).find('td:nth-child(12) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(13)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }
        cgst_total_sum+=cgst_v
        var sgst_p = parseFloat($(this).find('td:nth-child(14) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(15)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }
        sgst_total_sum+=sgst_v
        
        var line_total = $(this).find('td:nth-child(16)').html();

        var taxable_total = line_total - cgst_v - sgst_v;
        var sales_after_tax = round_off(taxable_total/quantity); 
        
        var item = {
            product_id : product_id,
            quantity: quantity,
            unit_name: unit_name,
            unit_multi: unit_multi,
            sales_after_tax: sales_after_tax,
            discount_amount: disc_amt,
            cgst_p: cgst_p,
            cgst_v:cgst_v,
            sgst_p: sgst_p,
            sgst_v: sgst_v,
            taxable_total: taxable_total,
            line_total: line_total,
            is_tax: is_tax
        };
        items.push(item);
    });

    cgst_total_sum = round_off(cgst_total_sum);
    sgst_total_sum = round_off(sgst_total_sum);
    console.log(items)
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{subtotal: subtotal,
                    cgsttotal: cgst_total_sum,
                    sgsttotal: sgst_total_sum,
                    total: total,
                    invoice_pk: invoice_pk,
                    bill_details: JSON.stringify(items),
                    calltype: "edit",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                
                success : function(jsondata) {
                    var show_success=true
                    if (jsondata['id']){
                        swal("Hooray", "Sales invoice updated", "success");
                        var url='/retailsales/invoice/detailview/'+jsondata['pk']+'/'
                        location.href = url;
                        // setTimeout(location.reload(true),1000);
                    }
                    else{
                        swal("Oops...", jsondata, "error");
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
        // swal("Oops...", "Please note that vendor and warehouse details must be filled."+
        //     "Also please check the highlightd rows", "error");
    }
}

});