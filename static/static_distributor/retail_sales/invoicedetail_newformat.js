
$(function(){

discount_types=['Nil','%','Val' ]

load_data()

function load_data(){
    $.ajax({
        url : "/retailsales/invoice/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // console.log()
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal'])
            $('.invoiceid').append(jsondata['invoice_id']);
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append(date);
            // $('.customer').append(jsondata['customer_name']+
            //         ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']);
            $('.customer').append(jsondata['customer_name']);
            $('.warehouse').append('<strong>'+jsondata['tenant_name']+'</strong> ,<br>'+jsondata['warehouse_address']+
                                ',<br>'+jsondata['warehouse_city']);
            $('.subtotal_receipt').append(jsondata['subtotal']);
            $('.cgsttotal_receipt').append(parseFloat(jsondata['cgsttotal']).toFixed(2));
            $('.sgsttotal_receipt').append(parseFloat(jsondata['sgsttotal']).toFixed(2));
            $('.total_receipt').append(jsondata['total']);

            $.each(jsondata['line_items'], function(){
                var total_gst=parseFloat(this.cgst_percent) + parseFloat(this.sgst_percent);
                $('.details').append("<tr class='data text-center'>"+
                    "<td id='not_pos_print'>"+this.product_name+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.product_hsn)+"</td>"+
                    "<td id='not_pos_print'>"+this.quantity+"</td>"+
                    "<td id='not_pos_print'>"+this.unit+"</td>"+
                    // "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td id='not_pos_print'>"+this.sales_price+"</td>"+
                    // "<td id='not_pos_print'>"+discount_types[this.discount_type]+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.discount_amount)+"</td>"+
                    // "<td id='not_pos_print'>"+this.line_tax+"</td>"+
                    // "<td id='not_pos_print'>"+this.tax_percent+"</td>"+
                    "<td id='not_pos_print'>"+this.cgst_percent+"</td>"+
                    "<td id='not_pos_print'>"+this.cgst_value+"</td>"+
                    "<td id='not_pos_print'>"+this.sgst_percent+"</td>"+
                    "<td id='not_pos_print'>"+this.sgst_value+"</td>"+
                    "<td id='not_pos_print'>"+this.line_total+"</td>"+
                    "</tr>");

                // $('.details_pos').append("<tr class='data text-center'>"+
                //     "<td>"+this.product_name+"<br>"+$.trim(this.discount_amount)+"</td>"+
                //     "<td>"+$.trim(this.product_hsn)+"<br>"+this.cgst_percent+"</td>"+
                //     "<td>"+this.quantity+"<br>"+this.cgst_value+"</td>"+
                //     "<td>"+this.unit+"<br>"+this.sgst_percent+"</td>"+
                //     "<td>"+this.sales_price+"<br>"+this.sgst_value+"</td>"+
                //     "<td>--<br>"+this.line_total+"</td>"+
                //     "<td></td></tr>"
                // );

                $('.details_pos').append("<tr class='data text-center prod_name_row'>"+
                    "<td colspan='8'><font size='1'>"+this.product_name+"</font></td>"+
                    // "<td></td></tr>"
                    "</tr>"
                );
                $('.details_pos').append("<tr class='data text-center prod_details_row'>"+
                    // "<td>"+this.product_name+"<br>"+$.trim(this.discount_amount)+"</td>"+
                    "<td class='first_col'><font size='1'>"+$.trim(this.product_hsn)+"</font></td>"+
                    "<td class='middle_col'><font size='1'>"+this.quantity+"</font></td>"+
                    "<td class='middle_col'><font size='1'>"+this.unit+"</font></td>"+
                    "<td class='middle_col'><font size='1'>"+this.sales_price+"</font></td>"+
                    "<td class='middle_col'><font size='1'>"+$.trim(this.discount_amount)+"</font></td>"+
                    "<td class='middle_col'><font size='1'>"+total_gst+"</font></td>"+
                    "<td class='middle_col'><font size='1'>"+this.line_total+"</font></td>"+
                    "<td class='last_col'></td></tr>"
                    // "</tr>"
                );

                // $('.details_pos').append("<tr class='data text-center'>"+
                //     "<td colspan='5'>"+this.product_name+"</td></tr>"+
                //     "<tr class='data text-center'>"+
                //     "<td>"+$.trim(this.product_hsn)+"<br>"+this.cgst_percent+"</td>"+
                //     "<td>"+this.quantity+"<br>"+this.cgst_value+"</td>"+
                //     "<td>"+this.unit+"<br>"+this.sgst_percent+"</td>"+
                //     "<td>"+this.sales_price+"<br>"+this.sgst_value+"</td>"+
                //     "<td>"+$.trim(this.discount_amount)+"<br>"+this.line_total+"</td></tr>"
                // );
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
     $('#not_pos_print').removeClass('hidden-print')
     $('.not_pos_print').removeClass('hidden-print')

     
  
  

     $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: A4; margin: 0mm;}");
        text("@media print {#print{display: block;}#not_print{display: none;}}");
    // $(".print_style").
    //     text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: 3in 10in; margin: 0mm;}");

    window.print();
});

$('.posprintout').click(function(){
     // window.print();
     $('#not_pos_print').addClass('hidden-print')
     $('.not_pos_print').addClass('hidden-print')
     $('.total_div').attr('hidden', true);
     $('.total_div_pos').attr('hidden', false);

     $('#a4_detail_div').attr('hidden', true);
     $('#pos_detail_div').attr('hidden', false);

     // console.log('here')


     // $('.total_receipt').removeClass('hidden-print')
     var y=$('.print').height();
     // console.log(y)
     // console.log(dpi_y)
     y_inch=y/dpi_y+1.5;
     if (y_inch>8.4){
        y_inch+=0.5;
     }
     $(".print_style").
        // text("@media print {.table.details tr td, table.details tr th { page-break-inside:avoid; page-break-after:auto;"+
        //     "position: relative; }"+
            text("@media print {.#print{display: block;}#not_print{display: none;}} @page{size: 3in "+y_inch+"in; margin: 0mm;}"+
                    // "@media print {"+
                    ".details_pos { border: solid #000000 !important; border-width: 0.2px 0 0 0.2px !important; }"+
                    ".details_pos th { border: solid #000000 !important; border-width: 0 0.2px 0.2px 0 !important; } "+
                    ".details_pos  td { border-bottom:0.2px solid black !important; } "+
                    ".details_pos .prod_details_row td { border-top:0  !important; } "+
                    ".details_pos .first_col { border-left:0.2px solid black !important; } "+
                    ".details_pos .first_col { border-right:0 !important; } "+
                    ".details_pos .last_col { border-right:0.2px solid black !important; } "+
                    ".details_pos .last_col { border-left:0 !important; } "+
                    ".details_pos .middle_col { border-right:0 !important; } "+
                    ".details_pos .middle_col { border-left:0 !important; } "+
                    ".details_pos .last_col { border-right:0.2px solid black !important; } "+
                    ".details_pos .prod_name_row td { border-top:0.2px solid black !important; } "+
                    ".details_pos .prod_name_row td { border-left:0.2px solid black !important; } "+
                    ".details_pos .prod_name_row td { border-right:0.2px solid black !important; } "+
                    ".details_pos .prod_name_row td { border-bottom:0  !important; }"+
                    ".boderless td { border:0  !important; } "+
                    ".boderless { border-collapse: collapse  !important; }} "
                );

    window.print();
    $('.total_div_pos').attr('hidden', true);
    $('.total_div').attr('hidden', false);

    $('#a4_detail_div').attr('hidden', false);
    $('#pos_detail_div').attr('hidden', true);
});

});