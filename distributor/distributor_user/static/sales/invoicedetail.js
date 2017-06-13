
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
            $('.invoiceid').append(jsondata['invoice_id']);
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append(date);
            $('.customer').append(jsondata['customer_name']+
                    ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']);
            $('.warehouse').append(jsondata['warehouse_address']+',<br>'+jsondata['warehouse_city']);
            $('.subtotal_receipt').append(jsondata['subtotal']);
            $('.taxtotal_receipt').append(jsondata['taxtotal']);
            $('.total_receipt').append(jsondata['total']);
            $.each(jsondata['line_items'], function(){
                free_total=parseFloat(this.free_with_tax)+parseFloat(this.free_without_tax)
                $('.details').append("<tr class='data text-center'>"+
                    "<td>"+this.product_name+"</td>"+
                    "<td>"+this.quantity+"</td>"+
                    "<td id='not_print'>"+this.free_without_tax+"</td>"+
                    "<td id='not_print'>"+this.free_with_tax+"</td>"+
                    "<td id='not_pos_print'>"+this.unit+"</td>"+
                    "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td id='not_pos_print'>"+this.sales_price+"</td>"+
                    "<td id='not_pos_print'>"+discount_types[this.discount_type]+"</td>"+
                    "<td id='not_pos_print'>"+this.discount_value+"</td>"+
                    "<td id='not_pos_print'>"+discount_types[this.discount2_type]+"</td>"+
                    "<td id='not_pos_print'>"+this.discount2_value+"</td>"+
                    "<td id='not_pos_print'>"+this.line_tax+"</td>"+
                    "<td id='not_pos_print'>"+this.tax_percent+"</td>"+
                    "<td>"+this.line_total+"</td>"+
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
     $(".print_style").
        text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: landscape; margin: 0mm;}");

    window.print();
});

$('.posprintout').click(function(){
     // window.print();
     $(".print_style").
        text("@media print {#pos_print{display: block;}#not_print{display: none;}#not_pos_print{display: none;}}"+
            " @page{size: 3in 10in; margin: 0mm;}");

    window.print();
});

});