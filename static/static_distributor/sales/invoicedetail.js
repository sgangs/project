
$(function(){

discount_types=['Nil','%','Val' ]

load_data()

function load_data(){
    $.ajax({
        url : "/sales/invoice/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            document.title = "Sales Invoice:"+jsondata['invoice_id'];
            igst_total=0;
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            $('.invoiceid').append('<font size="3">'+jsondata['invoice_id']+'</font>');
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append('<font size="3">'+date+'</font');
            if ((jsondata['dl_1']!=''&& jsondata['dl_1'] !=null) || (jsondata['dl_2']!=''&& jsondata['dl_2']!=null) ){
                $('.customer').append('<font size="2">'+jsondata['customer_name']+
                    ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']
                    +'<br>DL No:'+jsondata['dl_1']+'/'+jsondata['dl_2']+'<font size="2">');
            }
            else{
                $('.customer').append('<font size="2">'+jsondata['customer_name']+
                    ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']+'<font size="2">');
            }
            if ((jsondata['tenant_dl1']!=''&& jsondata['tenant_dl1'] !=null) || (jsondata['tenant_dl2']!=''&& jsondata['tenant_dl2']!=null) ){
                $('.warehouse').append('<font size="2">'+jsondata['tenant_name']+'<br>'+jsondata['warehouse_address']+
                    ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<br>DL No:'+jsondata['tenant_dl1']+'/'
                    +jsondata['tenant_dl2']+'<font size="2">');
            }
            else{
                $('.warehouse').append('<font size="2">'+jsondata['tenant_name']+'<br>'+jsondata['warehouse_address']+
                    ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<font size="2">');
            }
            $('.subtotal_receipt').append('<font size="2">'+jsondata['subtotal']+'<font size="2">');
            // $('.taxtotal_receipt').append(taxtotal.toFixed(2));
            cgst_fixed=parseFloat(jsondata['cgsttotal']).toFixed(2);
            sgst_fixed=parseFloat(jsondata['sgsttotal']).toFixed(2)
            $('.cgsttotal_receipt').append('<font size="2">'+cgst_fixed+'<font size="2">');
            $('.sgsttotal_receipt').append('<font size="2">'+sgst_fixed+'<font size="2">');
            $('.total_receipt').append('<font size="2">'+(parseFloat(jsondata['total'])-parseFloat(jsondata['roundoff'])).toFixed(2)+'<font size="2">');
            $('.roundoff_receipt').append('<font size="2">'+jsondata['roundoff']+'<font size="2">');
            $('.payable_receipt').append('<font size="2">'+jsondata['total']+'<font size="2">');
            $.each(jsondata['line_items'], function(){
                igst_total+=this.igst_value;
                var d1_val=0.00, d2_val=0.00;
                // free_total=parseFloat(this.free_with_tax)+parseFloat(this.free_without_tax)
                pur_rate=parseFloat(this.quantity)*parseFloat(this.purchase_price)
                d1_type=this.discount_type
                d2_type=this.discount2_type
                if (d1_type == 1){
                    d1_val=(this.discount_value*pur_rate/100);
                    pur_rate-=d1_val
                }
                else if(d1_type == 2){
                    d1_val=this.discount_value;
                    pur_rate-=d1_val
                }
                if (d2_type == 1){
                    d2_val=(this.discount2_value*pur_rate/100);
                }
                else if(d2_type == 2){
                    d2_val=this.discount2_value;
                }
                $('.details').append("<tr class='data text-center'>"+
                    "<td><font size='1'>"+this.product_name+"</font></td>"+
                    "<td><font size='1'>"+$.trim(this.product_hsn)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.quantity)+"</font></td>"+
                    // "<td id='not_print'>"+this.free_without_tax+"</td>"+
                    // "<td id='not_print'>"+this.free_with_tax+"</td>"+
                    "<td id='not_pos_print' class='hidden-print'><font size='1'>"+this.unit+"</font></td>"+
                    // "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.sales_price+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.mrp+"</font></td>"+
                    "<td id='not_pos_print' class='hidden-print'><font size='1'>"+discount_types[this.discount_type]+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.discount_value+"</font></td>"+
                    "<td id='not_pos_print' class='hidden-print'><font size='1'>"+discount_types[this.discount2_type]+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.discount2_value+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.line_tax+"</font></td>"+
                    // "<td id='not_pos_print'>"+this.tax_percent+"</td>"+
                    "<td><font size='1'>"+parseFloat(this.cgst_percent)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.cgst_value)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.sgst_percent)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.sgst_value)+"</font></td>"+
                    "<td class='is_igst'><font size='1'>"+parseFloat(this.igst_percent)+"</font></td>"+
                    "<td class='is_igst'><font size='1'>"+parseFloat(this.igst_value)+"</font></td>"+
                    "<td><font size='1'>"+this.line_total+"</font></td>"+
                    "</tr>");
            });

        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some issues in fetching the data.", "error");
        }
    });
}

$('.printout').click(function(){
     // window.print();
     if (igst_total == 0 || isNaN(igst_total)){
        $('.is_igst').addClass('hidden-print');

    }
     $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: landscape; margin: 0mm;}");
        text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: auto; margin: 0mm;}");

    window.print();
});

});