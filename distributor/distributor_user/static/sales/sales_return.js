
$(function(){

var pk, adjustment_same_inv = true, customer_id, current_invoice_id, adjust_invoice_error =false, adjustment_inv_no;

discount_types=['Nil','%','Val' ]

function round_off(value){
    value=parseInt(value*1000)/1000
    value=parseFloat(value.toFixed(2))
    return value
}



$('.get_invoice').click(function(){
    invoice_id=$('.sales_inv_no').val()
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{invoice_id: invoice_id,
            calltype: "return"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            customer_id = jsondata['customer'];
            current_invoice_id = jsondata['invoice_id'];
            $('.adjustment_inv_no').attr('disabled', false);
            // load_data(jsondata)
            $('.invoice_meta').attr('hidden', false);
            $('.details .data').remove()
            igst_total=0;
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            $('.invoiceid').html("<strong >Invoice No.: </strong>"+jsondata['invoice_id']);
            $('.sales_inv_pk').val(jsondata['id'])
            
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.original_date').html("<strong>Original Date: </strong>"+date);
            $('.customer').html("<strong>Customer: </strong>"+jsondata['customer_name']);
            $('.warehouse').html("<strong>Delivery From: </strong>"+jsondata['warehouse_address']+',<br>'
                                    +jsondata['warehouse_city']);
            // $('.subtotal_receipt').html(jsondata['subtotal']);
            // $('.taxtotal_receipt').html(taxtotal.toFixed(2));
            // $('.total_receipt').html(jsondata['total']);
            billtotal = parseFloat(jsondata['total']);
            billpaid = parseFloat(jsondata['amount_paid']);
            due = billtotal - billpaid;
            $('.original_due').html(due);
            
            $.each(jsondata['line_items'], function(){
                igst_total+=this.igst_value;
                // free_total=parseFloat(this.free_with_tax)+parseFloat(this.free_without_tax)
                sales_rate=parseFloat(this.sales_price)
                qty=parseFloat(this.quantity)
                d1_type=this.discount_type
                d2_type=this.discount2_type
                if (d1_type == 1){
                    d1_val=(this.discount_value*sales_rate/100);
                    sales_rate-=d1_val
                }
                else if(d1_type == 2){
                    d1_val=this.discount_value;
                    sales_rate-=(d1_val/qty)
                }
                if (d2_type == 1){
                    d2_val=(this.discount2_value*sales_rate/100);
                }
                else if(d2_type == 2){
                    d2_val=this.discount2_value;
                    sales_rate-=(d2_val/qty)
                }
                
                $('.details').append("<tr class='data text-center'>"+
                    '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
                    "<td hidden>"+this.id+"</td>"+
                    "<td hidden>"+this.product_id+"</td>"+
                    "<td>"+this.product_name+"</td>"+
                    "<td><input class='form-control qty_avl' value="+(this.quantity - this.quantity_returned)+" disabled></td>"+
                    "<td><input class='form-control qty'></td>"+
                    "<td id='not_pos_print'>"+this.unit+"</td>"+
                    "<td id='not_pos_print' hidden><input class='form-control sp' value="+sales_rate.toFixed(2)+" disabled></td>"+
                    "<td id='not_pos_print'><input class='form-control sr' value="+sales_rate+"></td>"+
                    
                    "<td id='not_pos_print'></td>"+
                    "<td><input class='form-control cgstp' value="+this.cgst_percent+"></td>"+
                    "<td></td>"+
                    "<td><input class='form-control sgstp' value="+this.sgst_percent+"></td>"+
                    "<td></td>"+
                    "<td class='is_igst'><input class='form-control igstp' value="+this.igst_percent+"></td>"+
                    "<td class='is_igst'></td>"+
                    "<td></td>"+
                    "</tr>");
                $('.dt').selectpicker('refresh');
                $('.dt2').selectpicker('refresh');
            });
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No finalized sales invoice exist. Sales return can be generated only for finalized invoices.", "error");
        }
    });
})


// function load_data(pk){
//     $.ajax({
//         url : "/sales/invoice/detail/"+pk+"/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             $('.invoice_meta').attr('hidden', false);
//             $('.details .data').remove()
//             igst_total=0;
//             taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
//             $('.invoiceid').html("<strong >Invoice No.: </strong>"+jsondata['invoice_id']);
//             $('.sales_inv_pk').val(jsondata['id'])
            
//             date=jsondata['date']
//             date=date.split("-").reverse().join("-")
//             $('.original_date').html("<strong>Original Date: </strong>"+date);
//             $('.customer').html("<strong>Customer: </strong>"+jsondata['customer_name']);
//             $('.warehouse').html("<strong>Delivery From: </strong>"+jsondata['warehouse_address']+',<br>'
//                                     +jsondata['warehouse_city']);
//             $('.subtotal_receipt').html(jsondata['subtotal']);
//             $('.taxtotal_receipt').html(taxtotal.toFixed(2));
//             $('.total_receipt').html(jsondata['total']);
            
//             $.each(jsondata['line_items'], function(){
//                 igst_total+=this.igst_value;
//                 // free_total=parseFloat(this.free_with_tax)+parseFloat(this.free_without_tax)
//                 sales_rate=parseFloat(this.sales_price)
//                 qty=parseFloat(this.quantity)
//                 d1_type=this.discount_type
//                 d2_type=this.discount2_type
//                 if (d1_type == 1){
//                     d1_val=(this.discount_value*sales_rate/100);
//                     sales_rate-=d1_val
//                 }
//                 else if(d1_type == 2){
//                     d1_val=this.discount_value;
//                     sales_rate-=(d1_val/qty)
//                 }
//                 if (d2_type == 1){
//                     d2_val=(this.discount2_value*sales_rate/100);
//                 }
//                 else if(d2_type == 2){
//                     d2_val=this.discount2_value;
//                     sales_rate-=(d2_val/qty)
//                 }
                
//                 $('.details').append("<tr class='data text-center'>"+
//                     '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
//                     "<td hidden>"+this.id+"</td>"+
//                     "<td hidden>"+this.product_id+"</td>"+
//                     "<td>"+this.product_name+"</td>"+
//                     "<td><input class='form-control qty_avl' value="+(this.quantity - this.quantity_returned)+" disabled></td>"+
//                     "<td><input class='form-control qty' value="+(this.quantity - this.quantity_returned)+"></td>"+
//                     "<td id='not_pos_print'>"+this.unit+"</td>"+
//                     "<td id='not_pos_print' hidden><input class='form-control sp' value="+sales_rate.toFixed(2)+" disabled></td>"+
//                     "<td id='not_pos_print'><input class='form-control sr' value="+sales_rate+"></td>"+
                    
//                     "<td id='not_pos_print'>"+this.line_tax+"</td>"+
//                     "<td><input class='form-control cgstp' value="+this.cgst_percent+"></td>"+
//                     "<td>"+this.cgst_value+"</td>"+
//                     "<td><input class='form-control sgstp' value="+this.sgst_percent+"></td>"+
//                     "<td>"+this.sgst_value+"</td>"+
//                     "<td class='is_igst'><input class='form-control igstp' value="+this.igst_percent+"></td>"+
//                     "<td class='is_igst'>"+this.igst_value+"</td>"+
//                     "<td>"+this.line_total+"</td>"+
//                     "</tr>");
//                 $('.dt').selectpicker('refresh');
//                 $('.dt2').selectpicker('refresh');
//             });

//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "There were some issues in fetching the data.", "error");
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

$(".details").on("keyup", ".cgstp", function(){
    get_total();
});
$(".details").on("keydown", ".cgstp", function(){
    get_total();
});

$(".details").on("keyup", ".sgstp", function(){
    get_total();
});
$(".details").on("keydown", ".sgstp", function(){
    get_total();
});

$(".details").on("keyup", ".igstp", function(){
    get_total();
});
$(".details").on("keydown", ".igstp", function(){
    get_total();
});

$(".adjustment_same_inv").change(function() {
    adjustment_same_inv = this.checked
    if(this.checked) {
        $('.adjustment_inv_div').removeClass("has-error");
        $('.adjustment_inv_no').val('');
        $('.adjustment_inv_div').attr('hidden', true);
    }
    else{
        $('.adjustment_inv_div').attr('hidden', false);
        adjust_invoice_error = false;
    }
})

$(".adjustment_inv_no").blur(function() {
    adjustment_inv_no = $(".adjustment_inv_no").val();
    if (current_invoice_id == adjustment_inv_no){
        swal("Ehh...", "Adjustment must not be against current invoice. If you want to adjust against current invoice, please select the same"
                +" under 'Adjustment Against' settings.", "info");
        adjust_invoice_error = true;
    }
    else{
        $.ajax({
            url : "due-amount/", 
            type: "GET",
            data:{adjustment_inv_no: adjustment_inv_no,
                customer_id: customer_id,
                calltype: "due_amount"},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                if (jsondata == "Invoice doesn't exist."){
                    $('.adjustment_inv_div').addClass("has-error");
                    adjust_invoice_error = true;
                    swal("Oops...", "No invoice with this invoice no for current customer found. Kindly retry.", "warning");
                }
                else{
                    adjust_invoice_error = false;
                    $('.adjustment_due').html(jsondata);
                    $('.adjustment_inv_div').removeClass("has-error");
                }
            },
            // handle a non-successful response
            error : function() {
                adjust_invoice_error = true;
                $('.adjustment_inv_div').addClass("has-error");
                swal("Oops...", "THere were some error. Please try again.", "error");
            }
        });
    }
})

$(".billdata").on("keyup", ".round", function(){
    round_manual();
});
$(".billdata").on("keydown", ".round", function(){
    round_manual();
});

function round_manual(argument) {
    subtotal = parseFloat($('.subtotal_receipt').html());
    console.log(subtotal);
    taxtotal = parseFloat($('.taxtotal_receipt').html());
    console.log(taxtotal);
    round_value = parseFloat($('.round').val());
    if (isNaN(round_value)){
        round_value = 0;
        // $('.round').val("0.00");
    }
    total = round_off(subtotal + taxtotal + round_value);
    console.log(total);
    $('.total_receipt').html(total.toFixed(2));
}

function get_qty_avl(el){
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(6) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(5) input').val());
    var unit = $(el).closest('tr').find('td:nth-child(5)').html();
    
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            swal({
                title: "Oops",
                text: "Total  return quantity cannot be greater than available sales quantity. <br>"+
                        "Available sales quantity: "+quantity_avl+" "+unit+".",
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
    for (var a = document.querySelectorAll('table.details tbody tr'), i = 0; a[i]; ++i) {
        // get all cells with input field
        cells = a[i].querySelectorAll('input:last-child');
        var quantity=parseFloat($(cells[1]).val());
        var qty_avl=parseFloat($(a[i]).find('td:nth-child(5)').html());
        // var free_tax_qty=parseFloat($(cells[4]).val());
        var free_tax_qty=0;
        var sales_rate=$(cells[3]).val()
        // var vat_total=0
        
        cgst_percent=parseFloat($(cells[4]).val());
        sgst_percent=parseFloat($(cells[5]).val());
        igst_percent=parseFloat($(cells[6]).val());

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        if(isNaN(igst_percent)){
            igst_percent=0;
        }
        
        if(isNaN(sales_rate)){
            sales_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        
        var this_total=round_off(quantity*sales_rate)        
        
        cgst_total=round_off((this_total*cgst_percent)/100);
        sgst_total=round_off((this_total*sgst_percent)/100);
        igst_total=round_off((this_total*igst_percent)/100);
        // cgst_total=(this_total*cgst_percent)/100;
        // sgst_total=(this_total*sgst_percent)/100;
        // igst_total=(this_total*igst_percent)/100;
        $(a[i]).find('td:nth-child(12) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(14) ').html(sgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(16) ').html(igst_total.toFixed(2))

        $(a[i]).find('td:nth-child(10) ').html(this_total.toFixed(2))
        vat_total=0;
        
        this_final_total=this_total+cgst_total+sgst_total+igst_total
        $(a[i]).find('td:nth-child(17) ').html(this_final_total.toFixed(2))
        subtotal=subtotal+this_total
        tax_total=tax_total+cgst_total+sgst_total+igst_total
    }
    subtotal = round_off(subtotal)
    tax_total = round_off(tax_total)
    total=round_off(subtotal+tax_total);
    
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.total_receipt').html(total.toFixed(2))
};



$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to generate a new sales return?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, generate new sales return!",
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
    invoiceid=$('.sales_inv_pk').val()
    date=$('.date').val()
    
    subtotal=parseFloat($('.subtotal_receipt').html());
    var cgsttotal=0, sgsttotal=0, igsttotal=0;
    total = parseFloat($('.total_receipt').html());
    
    if (invoiceid == '' || typeof(invoiceid) =='undefined' || $.trim(date) == '' || typeof(date) =='undefined'){
        proceed = false;
        swal("Oops...", "Please select/enter original invoice and return invoice date. ", "error");
    }
    
    $(".details tr.data").each(function() {
        var line_item_id = $(this).find('td:nth-child(2)').html();
        var product_id = $(this).find('td:nth-child(3)').html();
        
        var quantity_avl = parseFloat($(this).find('td:nth-child(5) input').val());
        var quantity = parseFloat($(this).find('td:nth-child(6) input').val());
        
        if (quantity == '' || quantity =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        if (quantity > quantity_avl){
            swal("Oops...", "Sales return quantity is more than original quantity. ", "error");
            proceed=false;
        }

        
        var return_price = $(this).find('td:nth-child(9) input').val();
        
        if (return_price == '' || return_price =='undefined' || typeof(return_price) == 'undefined'){
            proceed=false;
            swal("Oops...", "Please enter a sales return rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        var cgst_p = parseFloat($(this).find('td:nth-child(11) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(12)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }
        cgsttotal+=cgst_v
        
        var sgst_p = parseFloat($(this).find('td:nth-child(13) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(14)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }
        sgsttotal+=sgst_v

        var igst_p = parseFloat($(this).find('td:nth-child(15) input').val());
        var igst_v = parseFloat($(this).find('td:nth-child(16)').html());
        if (isNaN(igst_p)){
            igst_p=0;
            igst_v=0;
        }
        igsttotal+=igst_v
        
        var taxable_total = $(this).find('td:nth-child(10)').html();
        var line_total = $(this).find('td:nth-child(17)').html();
        
        var item = {
            line_item_id: line_item_id,
            product_id : product_id,
            quantity: quantity,
            return_price: return_price,
            cgst_p: cgst_p,
            cgst_v:cgst_v,
            sgst_p: sgst_p,
            sgst_v: sgst_v,
            igst_p: igst_p,
            igst_v: igst_v,
            taxable_total: taxable_total,
            line_total: line_total,
        };
        items.push(item);
    });

    adjustment_same_inv;
    
    if (adjustment_same_inv){
        available_total = ($('.original_due').html());
        if (total>available_total){
            proceed = false;
            swal("Ehh...", "Sales Return amount exceeds receivable amount against current invoice.", "error");
        }
    }
    else{
        console.log('here');
        available_total =  $('.adjustment_due').html();
        if (total>available_total){
            proceed = false;
            swal("Ehh...", "Sales Return amount exceeds receivable amount against selected invoice.", "error");
        }
    }

    if (adjust_invoice_error){
        proceed = false;
    }
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{invoiceid:invoiceid,
                    date:date.split("/").reverse().join("-"),
                    subtotal: subtotal,
                    cgsttotal: cgsttotal,
                    sgsttotal: sgsttotal,
                    igsttotal: igsttotal,
                    total: total,
                    adjustment_same_inv: adjustment_same_inv,
                    adjustment_inv_no: adjustment_inv_no,
                    bill_details: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New sales return generated", "success");
                        var url='/sales/invoice/detailview/'+jsondata+'/'
                        location.href = url;
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
        // swal("Oops...", "Please note that vendor and warehouse details must be filled."+
        //     "Also please check the highlightd rows", "error");
    }
}



});