
$(function(){

discount_types=['Nil','%','Val' ]

load_data()

function load_data(){
    $.ajax({
        url : "/inventory/transfer/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            document.title = "Delivery Challan:"+jsondata['transfer_id'];
            igst_total=0;
            // taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            $('.invoiceid').append('<font size="3">'+jsondata['transfer_id']+'</font>');
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append('<font size="3">'+date+'</font');
            
            // $('.customer').append('<font size="2">'+jsondata['customer_name']+
            //     ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']
            //     +'<br>DL No:'+jsondata['dl_1']+'/'+jsondata['dl_2']+'<font size="2">');
            
            // $('.warehouse').append('<font size="2">'+jsondata['tenant_name']+'<br>'+jsondata['warehouse_address']+
            //     ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<br>DL No:'+jsondata['tenant_dl1']+'/'
            //     +jsondata['tenant_dl2']+'<font size="2">');
            
            $.each(jsondata['line_items'], function(){
                $('.details').append("<tr class='data text-center'>"+
                    "<td><font size='1'>"+this.product_name+"</font></td>"+
                    "<td><font size='1'>"+$.trim(this.product_hsn)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.quantity)+"</font></td>"+
                    // "<td><font size='1'>"+this.unit+"</font></td>"+
                    "<td></td>"+
                    // "<td class='visible-print-block'>"+free_total+"</td>"+
                    // "<td id='not_pos_print'><font size='1'>"+this.sales_price+"</font></td>"+
                    // "<td id='not_pos_print'><font size='1'>"+this.mrp+"</font></td>"+
                    // "<td id='not_pos_print' class='hidden-print'><font size='1'>"+discount_types[this.discount_type]+"</font></td>"+
                    // "<td id='not_pos_print'><font size='1'>"+this.discount_value+"</font></td>"+
                    // "<td id='not_pos_print' class='hidden-print'><font size='1'>"+discount_types[this.discount2_type]+"</font></td>"+
                    // "<td id='not_pos_print'><font size='1'>"+this.discount2_value+"</font></td>"+
                    // "<td id='not_pos_print'><font size='1'>"+this.line_tax+"</font></td>"+
                    // // "<td id='not_pos_print'>"+this.tax_percent+"</td>"+
                    // "<td><font size='1'>"+parseFloat(this.cgst_percent)+"</font></td>"+
                    // "<td><font size='1'>"+parseFloat(this.cgst_value)+"</font></td>"+
                    // "<td><font size='1'>"+parseFloat(this.sgst_percent)+"</font></td>"+
                    // "<td><font size='1'>"+parseFloat(this.sgst_value)+"</font></td>"+
                    // "<td class='is_igst'><font size='1'>"+parseFloat(this.igst_percent)+"</font></td>"+
                    // "<td class='is_igst'><font size='1'>"+parseFloat(this.igst_value)+"</font></td>"+
                    // "<td><font size='1'>"+this.line_total+"</font></td>"+
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
     
     $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: landscape; margin: 0mm;}");
        text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: auto; margin: 0mm;}");

    window.print();
});

});