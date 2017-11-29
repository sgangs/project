
$(function(){

discount_types=['Nil','%','Val' ]

load_data()

function load_data(){
    $.ajax({
        url : "/servicesales/invoice/servicedetail/"+pk+"/", 
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
            
            // $('.customer').append(jsondata['customer_name']);
            
            $('.warehouse').append('<strong>'+jsondata['tenant_name']+'</strong> ,<br>'+jsondata['warehouse_address']+
                                ',<br>'+jsondata['warehouse_city']);
            $('.subtotal_receipt').append(jsondata['subtotal']);
            $('.cgsttotal_receipt').append(parseFloat(jsondata['cgsttotal']).toFixed(2));
            $('.sgsttotal_receipt').append(parseFloat(jsondata['sgsttotal']).toFixed(2));
            $('.total_receipt').append(jsondata['total']);
            
            $.each(jsondata['line_items'], function(){
                pur_rate=parseFloat(this.quantity)*parseFloat(this.purchase_price)
                $('.details').append("<tr class='data text-center'>"+
                    "<td id='not_pos_print'>"+this.service_name+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.service_hsn)+"</td>"+
                    "<td id='not_pos_print'>"+this.quantity+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.user_details[0]['name'])+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.user_details[0]['cont'])+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.user_details[1]['name'])+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.user_details[1]['cont'])+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.user_details[2]['name'])+"</td>"+
                    "<td id='not_pos_print'>"+$.trim(this.user_details[2]['cont'])+"</td>"+
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
            text("@media print {.#print{display: block;}#not_print{display: none;}} @page{size: 3in "+y_inch+"in; margin: 0mm;}");

    window.print();
    $('.total_div_pos').attr('hidden', true);
    $('.total_div').attr('hidden', false);

    $('#a4_detail_div').attr('hidden', false);
    $('#pos_detail_div').attr('hidden', true);
});

});