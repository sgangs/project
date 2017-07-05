
$(function(){

var pk;

discount_types=['Nil','%','Val' ]


$('.get_invoice').click(function(){
    invoice_id=$('.sales_inv_no').val()
    console.log("here")
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{invoice_id: invoice_id,
            calltype: "Sales Return"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata)
            load_data(jsondata)
            // $(".prod_data .prod_indi_data").remove();
            // $.each(jsondata, function(){
            //     $('.prod_data').append("<tr class='prod_indi_data'>"+
            //     "<td class='prod_tsp'>"+this.tentative_sales_price +"</td>"+
            //     "<td class='prod_mrp'>"+this.mrp+"</td>"+
            //     "<td class='prod_qa'>"+this.available+"</td>"+
            //     "<td class='prod_qa'>"+default_unit+"</td>"+
            //     "</tr>");
            // })
            // $('#productdetails').modal('show');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product inventory exist.", "error");
        }
    });
})


function load_data(pk){
    $.ajax({
        url : "/sales/invoice/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.invoice_meta').attr('hidden', false);
            $('.details .data').remove()
            igst_total=0;
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            $('.invoiceid').html("<strong >Invoice No.: </strong>"+jsondata['invoice_id']);
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').html("<strong>Original Date: </strong>"+date);
            // $('.customer').append(jsondata['customer_name']+
            //         ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']);
            $('.customer').html("<strong>Customer: </strong>"+jsondata['customer_name']);
            $('.warehouse').html("<strong>Delivery From: </strong>"+jsondata['warehouse_address']+',<br>'
                                    +jsondata['warehouse_city']);
            $('.subtotal_receipt').html(jsondata['subtotal']);
            $('.taxtotal_receipt').html(taxtotal.toFixed(2));
            $('.total_receipt').html(jsondata['total']);
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
                    "<td>"+this.product_name+"</td>"+
                    "<td><input class='form-control qty_avl' value="+this.quantity+" disabled></td>"+
                    "<td><input class='form-control qty' value="+this.quantity+"></td>"+
                    // "<td id='not_print'>"+this.free_without_tax+"</td>"+
                    // "<td id='not_print'>"+this.free_with_tax+"</td>"+
                    "<td id='not_pos_print'>"+this.unit+"</td>"+
                    // "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td id='not_pos_print' hidden><input class='form-control sp' value="+sales_rate.toFixed(2)+" disabled></td>"+
                    "<td id='not_pos_print'><input class='form-control sr' value="+sales_rate+"></td>"+
                    // "<td id='not_pos_print'><input class='form-control dt1' value="+discount_types[this.discount_type]+"></td>"+
                    // '<td colspan="1"><select class="form-control select dt">'+
                    //     '<option data-id=0 title="-">No Discount</option>'+
                    //     '<option data-id=1 title=%>Percent(%)</option>'+
                    //     '<option data-id=2 title="V">Value(V)</option>'+
                    //     '</select></td>'+
                    // "<td id='not_pos_print'><input class='form-control dv' value="+this.discount_value+"></td>"+
                    // "<td id='not_pos_print'><input class='form-control dt2' value="+discount_types[this.discount2_type]+"></td>"+
                    // '<td colspan="1"><select class="form-control selectpicker dt2">'+
                    //     '<option data-id=0 title="-">No Discount</option>'+
                    //     '<option data-id=1 title=%>Percent(%)</option>'+
                    //     '<option data-id=2 title="V">Value(V)</option>'+
                    //     '</select></td>'+
                    // "<td id='not_pos_print'><input class='form-control dv2' value="+this.discount2_value+"></td>"+
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
                // $('dt').val(this.discount_type);
                // $('dt2').val(this.discount2_type);
                // $('.dt').selectpicker('refresh');
                // $('.dt2').selectpicker('refresh');
            });

        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some issues in fetching the data.", "error");
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


function get_qty_avl(el){
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(3) input').val());
    var unit = $(el).closest('tr').find('td:nth-child(5)').html();
    
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than actual sales quantity. <br>"+
                        " Actual Sales quantity: "+quantity_avl+" "+unit+".",
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
        console.log(cells)
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
        
        // vat_input=parseInt(vat_type_reverse[$(a[i]).find('td:nth-child(18)').html()]);
        // vat_percent=parseFloat($(a[i]).find('td:nth-child(19)').html());
        
        if(isNaN(sales_rate)){
            sales_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        
        var this_total=quantity*sales_rate
        
        
        cgst_total=(this_total*cgst_percent)/100;
        sgst_total=(this_total*sgst_percent)/100;
        igst_total=(this_total*igst_percent)/100;
        $(a[i]).find('td:nth-child(10) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(12) ').html(sgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(14) ').html(igst_total.toFixed(2))

        $(a[i]).find('td:nth-child(8) ').html(this_total.toFixed(2))
        vat_total=0;
        
        this_final_total=this_total+cgst_total+sgst_total+igst_total
        $(a[i]).find('td:nth-child(15) ').html(this_final_total.toFixed(2))
        subtotal=subtotal+this_total
        tax_total=tax_total+cgst_total+sgst_total+igst_total
    }
    total=subtotal+tax_total
    
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.total_receipt').html(total.toFixed(2))
};

});