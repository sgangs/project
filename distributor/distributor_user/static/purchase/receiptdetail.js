$(function(){

discount_types=['Nil','%','Val' ]

load_data()

function load_data(){
    $.ajax({
        url : "/purchase/receipt/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            $('.receiptid').append(jsondata['receipt_id']);
            $('.invoiceid').append(jsondata['supplier_invoice']);
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append(date);
            $('.vendor').append(jsondata['vendor_address']);
            $('.warehouse').append(jsondata['warehouse_address']);
            $('.subtotal_receipt').append(jsondata['subtotal']);
            $('.taxtotal_receipt').append(jsondata['taxtotal']);
            $('.total_receipt').append(jsondata['total']);
            $.each(jsondata['line_items'], function(){
                var d1_val=0, d2_val=0;
                free_total=parseFloat(this.free_with_tax)+parseFloat(this.free_without_tax)
                pur_rate=parseFloat(this.quantity)*parseFloat(this.purchase_price)
                // console.log(pur_rate);
                d1_type=this.discount_type
                console.log(d1_type)
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
                console.log(d1_val);
                console.log(d2_val);
                $('.details').append("<tr class='data text-center'>"+
                    "<td span='4'>"+this.product_name+"</td>"+
                    "<td>"+this.quantity+"</td>"+
                    "<td class='hidden-print'>"+this.free_without_tax+"</td>"+
                    "<td class='hidden-print'>"+this.free_with_tax+"</td>"+
                    "<td>"+this.unit+"</td>"+
                    "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td>"+this.purchase_price+"</td>"+
                    "<td>"+this.tentative_sales_price+"</td>"+
                    "<td>"+this.mrp+"</td>"+
                    "<td class='hidden-print'>"+discount_types[this.discount_type]+"</td>"+
                    "<td>"+this.discount_value+"</td>"+
                    // "<td class='visible-print-block'>"+d1_val+"</td>"+
                    "<td class='hidden-print'>"+discount_types[this.discount2_type]+"</td>"+
                    "<td>"+this.discount2_value+"</td>"+
                    // "<td class='visible-print-block'>"+d2_val+"</td>"+
                    "<td>"+this.line_tax+"</td>"+
                    "<td>"+this.tax_percent+"</td>"+
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

// $( ".printout" ).click(function() {
//     demoFromHTML();
// });


// var doc = new jsPDF('landscape');

// var specialElementHandlers = {
//     '#editor': function (element, renderer) {
//         return true;
//     }
// };


// $('.printout').click(function () {
//     doc.fromHTML($('#print').html(), 15, 15, {
//         // 'width': 170,
//         'elementHandlers': specialElementHandlers
//     });
// doc.save('sample-content.pdf');
// });

// $('.printout').click(function () {
// html2canvas(document.getElementById("print"), {
//     onrendered: function(canvas) {

//     var imgData = canvas.toDataURL('image/png');
//     // console.log('Report Image URL: '+imgData);
//     // var doc = new jsPDF('p', 'mm', [297, 210]); //210mm wide and 297mm high
//     var doc = new jsPDF('landscape');
                
//     doc.addImage(imgData, 'PNG', 10, 10);
//     // doc.addImage(imgData, 'PNG');
//     doc.save('sample.pdf');
//     }
// });
// });

$('.printout').click(function(){
     window.print();
});

});