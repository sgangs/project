
$(function(){

var pk;

discount_types=['No Discount','Percent(%)','Value(V)' ]


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
            calltype: "Sales Return"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // load_data(jsondata)
            maintain_inventory = jsondata['maintain_inventory']
            $('.invoice_meta').attr('hidden', false);
            $('.details .data').remove()
            igst_total=0;
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            $('.invoiceid').html("<strong >Invoice No.: </strong>"+jsondata['invoice_id']);
            $('.sales_inv_pk').val(jsondata['id'])
            
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.original_date').html("<strong>Date: </strong>"+date);
            $('.customer').html("<strong>Customer: </strong>"+jsondata['customer_name']);

            $('.editCustomerAddress').val(jsondata['customer_address']);
            $('.editCustomerGST').val(jsondata['customer_gst']);

            $('.warehouse').html("<strong>Delivery From: </strong>"+jsondata['warehouse_address']+',<br>'
                                    +jsondata['warehouse_city']);
            $('.subtotal_receipt').html(jsondata['subtotal']);
            $('.taxtotal_receipt').html(taxtotal.toFixed(2));
            $('.total_receipt').html(jsondata['total']);
            $('.round').html(jsondata['roundoff']);
            
            $.each(jsondata['line_items'], function(){
                igst_total+=this.igst_value;
                sales_rate=parseFloat(this.sales_price)
                qty=parseFloat(this.quantity)
                
                $('.details').append("<tr class='data ongoing text-center'>"+
                    '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
                    "<td hidden>"+this.id+"</td>"+
                    "<td hidden>"+this.product_id+"</td>"+
                    "<td>"+this.product_name+"</td>"+
                    "<td hidden><input class='form-control qty_avl' value="+(this.qty_avl)+" disabled></td>"+
                    "<td><input class='form-control qty' value="+(this.quantity - this.quantity_returned)+"></td>"+
                    "<td id='not_pos_print'>"+this.unit+"</td>"+
                    "<td hidden>"+this.unit_multi+"</td>"+
                    "<td id='not_pos_print' hidden>"+sales_rate.toFixed(2)+"</td>"+
                    "<td id='not_pos_print'><input class='form-control sr' value="+sales_rate+"></td>"+
                    // '<th class="text-center">'+this.discount_type+'</th>'+ //Disc. Type-1
                    '<td colspan="1"><select class="form-control selectpicker dt">'+
                        '<option data-id=0 title="-">No Discount</option>'+
                        '<option data-id=1 title=%>Percent(%)</option>'+
                        '<option data-id=2 title="V">Value(V)</option>'+
                        '</select></td>'+
                    "<td class='text-center'><input class='form-control dv' value="+(this.discount_value)+"></td>"+ //Disc. Value-1
                    // '<th class="text-center">'+this.discount2_type+'</th>'+ //Disc. Type-2
                    '<td colspan="1"><select class="form-control selectpicker dt2">'+
                        '<option data-id=0 title="-">No Discount</option>'+
                        '<option data-id=1 title=%>Percent(%)</option>'+
                        '<option data-id=2 title="V">Value(V)</option>'+
                        '</select></td>'+
                    "<td class='text-center'><input class='form-control dv2' value="+(this.discount2_value)+"></td>"+ //Disc. Value-2
                    "<td hidden>"+this.tentative_sales_price+"</td>"+
                    "<td hidden>"+this.mrp+"</td>"+
                    "<td id='not_pos_print'>"+this.line_tax+"</td>"+                    
                    "<td><input class='form-control cgstp' value="+this.cgst_percent+"></td>"+
                    "<td>"+this.cgst_value+"</td>"+
                    "<td><input class='form-control sgstp' value="+this.sgst_percent+"></td>"+
                    "<td>"+this.sgst_value+"</td>"+
                    "<td class='is_igst'><input class='form-control igstp' value="+this.igst_percent+"></td>"+
                    "<td class='is_igst'>"+this.igst_value+"</td>"+
                    "<td>"+this.line_total+"</td>"+
                    "</tr>");
                $('.dt').selectpicker('refresh');
                $('.dt2').selectpicker('refresh');

                updating_row=$('.details').find('.ongoing');
                $(updating_row).find('td:nth-child(11) .dt').val(discount_types[this.discount_type]);
                $(updating_row).find('td:nth-child(13) .dt2').val(discount_types[this.discount2_type]);
                $(updating_row).removeClass('ongoing');
                $('.dt').selectpicker('refresh')
                $('.dt2').selectpicker('refresh')
            });

        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No open/editable sales invoice exist.", "error");
        }
    });
})


$('.editMetaData').click(function(){
    $('#billMetaData').modal('show');
});



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
    if (maintain_inventory){
        get_qty_avl(el);
    }
});
$(".details").on("keydown", ".qty", function(){
    var el=this;
    get_total();
    if (maintain_inventory){
        get_qty_avl(el);
    }
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

$(".details").on("change", ".dt", function(){
    get_total();
});

$(".details").on("change", ".dt2", function(){
    get_total();
});

$(".details").on("keyup", ".dv", function(){
    get_total();
});
$(".details").on("keydown", ".dv", function(){
    get_total();
});

$(".details").on("keyup", ".dv2", function(){
    get_total();
});
$(".details").on("keydown", ".dv2", function(){
    get_total();
});

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
    total = round_off(subtotal + taxtotal + round_value);
    console.log(total);
    $('.total_receipt').html(total.toFixed(2));
}


function get_qty_avl(el){
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(6) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(5) input').val());
    var unit = $(el).closest('tr').find('td:nth-child(7)').html();
    var unit_multi = $(el).closest('tr').find('td:nth-child(8)').html();
    
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>(quantity_avl/unit_multi) ){
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than actual sales quantity. <br>"+
                        " Actual Sales quantity: "+(quantity_avl/unit_multi)+" "+unit+".",
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
        // console.log(cells)
        var quantity=parseFloat($(cells[1]).val());
        
        var free_tax_qty=0;
        var sales_rate=$(cells[2]).val()
        // var mrp=$(a[i]).find('td:nth-child(9)').html();
        // var vat_total=0
        
        discount_type=$(a[i]).find('td:nth-child(11) :selected').data('id');
        discount_val=$(cells[3]).val();
        discount_type_2=$(a[i]).find('td:nth-child(13) :selected').data('id');
        discount_val_2=$(cells[4]).val();

        cgst_percent=parseFloat($(cells[5]).val());
        sgst_percent=parseFloat($(cells[6]).val());
        igst_percent=parseFloat($(cells[7]).val());

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        if(isNaN(igst_percent)){
            igst_percent=0;
        }
        
        // vat_input=parseInt(vat_type_reverse[$(a[i]).find('td:nth-child(18)').html()]);
        // vat_percent=parseFloat($(a[i]).find('td:nth-child(19)').html());
        
        if(isNaN(sales_rate)){
            sales_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        // if(isNaN(mrp)){
        //     mrp=0;
        // }
        // if(isNaN(free_tax_qty)){
            // free_tax_qty=0;
        // }
        
        var this_total=round_off(quantity*sales_rate)
        
        sales_disc_rate=sales_rate
        if (discount_type == 1){
            sales_disc_rate=sales_disc_rate-(discount_val*this_total/100);
            this_total=(this_total)-(discount_val*this_total/100);
        }
        else if(discount_type == 2){
            sales_disc_rate=sales_disc_rate - discount_val/quantity;
            this_total=(this_total - discount_val);
        }
        if (discount_type_2 == 1){
            sales_disc_rate=sales_disc_rate-(discount_val_2*this_total/100);
            this_total=(this_total)-(discount_val_2*this_total/100);
        }
        else if(discount_type_2 == 2){
            sales_disc_rate=sales_disc_rate - discount_val_2/quantity;
            this_total=(this_total - discount_val_2);
        }
        
        cgst_total=round_off((this_total*cgst_percent)/100);
        sgst_total=round_off((this_total*sgst_percent)/100);
        igst_total=round_off((this_total*igst_percent)/100);
        $(a[i]).find('td:nth-child(19) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(21) ').html(sgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(23) ').html(igst_total.toFixed(2))

        $(a[i]).find('td:nth-child(17) ').html(this_total.toFixed(2))
        
        this_final_total=round_off(this_total+cgst_total+sgst_total+igst_total)
        $(a[i]).find('td:nth-child(24) ').html(this_final_total.toFixed(2))
        subtotal=round_off(subtotal+this_total)
        tax_total=round_off(tax_total+cgst_total+sgst_total+igst_total)
    }
    total=round_off(subtotal+tax_total);
    round_value=round_off((Math.round(total)-total));
    payable=round_off(total+round_value);
    // console.log(round_value)
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.round').val(round_value.toFixed(2))
    $('.total_receipt').html(payable.toFixed(2))
};



$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to edit the sales invoice?",
        type: "warning",
        showCancelButton: true,
        // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, edit sales invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){edit_data()},600)            
        }
    })
});
    
function edit_data(){
    var items=[];
    var proceed=true;
    invoiceid=$('.sales_inv_pk').val()
    // grand_discount_type=$('.gdt').find(':selected').data('id');
    // grand_discount_value=$('.gd').val();
    subtotal=round_off(parseFloat($('.subtotal_receipt').html()));
    // taxtotal=parseFloat($('.taxtotal_receipt').html());
    var cgsttotal=0, sgsttotal=0, igsttotal=0;
    
    round_value=round_off(parseFloat($('.round').val()));

    total=round_off(parseFloat($('.total_receipt').html()));
    if (invoiceid == '' || typeof(invoiceid) =='undefined'){
        proceed = false;
        swal("Oops...", "Please select/enter original invoice. ", "error");
    }
    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(3)').html();
        // if (product_id == '' || product_id =='undefined'){
        //     proceed=false;
        //     swal("Oops...", "Please enter a product ", "error");
        //     $(this).closest('tr').addClass("has-error");
        // }

        var quantity = parseFloat($(this).find('td:nth-child(6) input').val());
        // var quantity_avl = parseFloat($(this).find('td:nth-child(5)').html());
        if (quantity == '' || quantity =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        // var free = parseInt($(this).find('td:nth-child(6) input').val());

        // if (isNaN(free)){
        //     free=0;
        // }
        
        // var free_tax = parseInt($(this).find('td:nth-child(7) input').val());
        // if (isNaN(free_tax)){
        //     free_tax=0;
        // }
        if (maintain_inventory){
            var qty_proceed= get_qty_avl(this);
        }
        else{
            qty_proceed = true;
        }
        
        if (!qty_proceed){
            swal("Oops...", "You don't have enough quantity available. ", "error");
            proceed=false;
        }

        var unit_symbol = $(this).find('td:nth-child(7)').html();
        var unit_multi = $(this).find('td:nth-child(8)').html();
        // if (unit_id == '' || unit_id =='undefined'){
            // proceed=false;
            // swal("Oops...", "Please enter the purchase unit ", "error");
            // $(this).closest('tr').addClass("has-error");
        // }

        var tsp = $(this).find('td:nth-child(15)').html();
        var mrp = $(this).find('td:nth-child(16)').html();
        
        var sales = $(this).find('td:nth-child(10) input').val();
        if (sales == '' || sales =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a sales rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        var disc_type = $(this).find('td:nth-child(11) :selected').data('id');
        var disc = round_off(parseFloat($(this).find('td:nth-child(12) input').val()));
        if (isNaN(disc)){
            disc=0;
        }

        var disc_type_2 = $(this).find('td:nth-child(13) :selected').data('id');
        var disc_2 = parseFloat($(this).find('td:nth-child(14) input').val());
        if (isNaN(disc_2)){
            disc_2=0;
        }

        var cgst_p = parseFloat($(this).find('td:nth-child(18) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(19)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }
        cgsttotal+=cgst_v
        
        var sgst_p = parseFloat($(this).find('td:nth-child(20) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(21)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }
        sgsttotal+=sgst_v

        var igst_p = parseFloat($(this).find('td:nth-child(22) input').val());
        var igst_v = parseFloat($(this).find('td:nth-child(23)').html());
        if (isNaN(igst_p)){
            igst_p=0;
            igst_v=0;
        }
        igsttotal+=igst_v
        
        var taxable_total = $(this).find('td:nth-child(17)').html();
        var line_total = $(this).find('td:nth-child(24)').html();
        
        var item = {
            product_id : product_id,
            quantity: quantity,
            // free: free,
            // free_tax:free_tax,
            unit_symbol: unit_symbol,
            unit_multi: unit_multi,
            sales: sales,
            tsp:tsp,
            mrp: mrp,
            disc_type: disc_type,
            disc: disc,
            disc_type_2: disc_type_2,
            disc_2: disc_2,
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
    cgsttotal = round_off(cgsttotal);
    sgsttotal = round_off(sgsttotal);
    igsttotal = round_off(igsttotal)
    
    console.log(subtotal);
    console.log(cgsttotal);
    console.log(sgsttotal);
    console.log(total);
    console.log(round_value);
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{invoiceid:invoiceid,
                    // warehouse:warehouseid,
                    // date:date.split("/").reverse().join("-"),
                    // grand_discount_type: grand_discount_type,
                    // grand_discount_value: grand_discount_value,
                    subtotal: subtotal,
                    // taxtotal: taxtotal,
                    cgsttotal: cgsttotal,
                    sgsttotal: sgsttotal,
                    igsttotal: igsttotal,
                    round_value: round_value,
                    total: total,
                    // duedate: duedate.split("/").reverse().join("-"),
                    bill_details: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Sales invoice updated", "success");
                        var url='/sales/invoice/detailview/'+jsondata+'/'
                        location.href = url;
                        // setTimeout(location.reload(true),1000);
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