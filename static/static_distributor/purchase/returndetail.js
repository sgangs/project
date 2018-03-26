$(function(){

var igst_total=0;

load_data()

function load_data(){
    $.ajax({
        url : "/purchase/return/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // console.log(jsondata);
            // taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            
            $('.receiptid').append(jsondata['supplier_note_no']);
            $('.invoiceid').append(jsondata['adjustmnet_receipt_no']);
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append(date);
            
            $('.vendor').append('<p>Name: '+jsondata['vendor_name']+
                '<br>Address: '+jsondata['vendor_address']+'<br>GST: '+$.trim(jsondata['vendor_gst'])+'</p>');
            $('.user').append('<p>Name: '+jsondata['tenant_name']+
                '<br>Address: '+jsondata['tenant_address']+'<br>GST: '+$.trim(jsondata['tenant_gst'])+'</p>');
            // $('.warehouse').append(jsondata['warehouse_address']);
            $('.subtotal_receipt').append(jsondata['subtotal']);
            
            // $('.taxtotal_receipt').append(taxtotal.toFixed(2));
            
            $('.cgsttotal_receipt').append((parseFloat(jsondata['cgsttotal'])).toFixed(2));
            $('.sgsttotal_receipt').append((parseFloat(jsondata['sgsttotal'])).toFixed(2));
            $('.round').append(jsondata['roundoff']);
            $('.total_receipt').append(jsondata['total']);
            if (jsondata['note_type'] == "1" || jsondata['note_type'] == 1){
                $.each(jsondata['line_items'], function(){
                    
                    igst_total+=this.igst_value;
                    // total_pretax=this.line_total - this.cgst_value - this.sgst_value - this.igst_value;
                    $('.details').append("<tr class='data text-center'>"+
                        "<td span='4'>"+this.product_name+"</td>"+
                        "<td span='4'>"+$.trim(this.product_hsn)+"</td>"+
                        "<td>"+this.quantity+"</td>"+
                        "<td>"+this.unit_symbol+"</td>"+
                        "<td>"+this.return_purchase_price+"</td>"+
                        "<td>"+this.tentative_sales_price+"</td>"+
                        "<td>"+this.mrp+"</td>"+
                        "<td>"+this.line_taxable_value+"</td>"+
                        "<td class='is_not_igst'>"+this.cgst_percent+"</td>"+
                        "<td class='is_not_igst'>"+this.cgst_value+"</td>"+
                        "<td class='is_not_igst'>"+this.sgst_percent+"</td>"+
                        "<td class='is_not_igst'>"+this.sgst_value+"</td>"+
                        "<td class='is_igst'>"+this.igst_percent+"</td>"+
                        "<td class='is_igst'>"+this.igst_value+"</td>"+
                        // "<td>"+this.tax_percent+"</td>"+
                        "<td>"+this.line_total+"</td>"+
                        "</tr>");
                });
            }
            else{
            $('.noninventory').attr('hidden', true);
                $.each(jsondata['line_items'], function(){
                    $('.details').append("<tr class='data text-center'>"+
                        "<td span='4'>"+this.product_name+"</td>"+
                        "<td span='4' hidden>"+$.trim(this.product_hsn)+"</td>"+
                        "<td hidden>"+this.quantity+"</td>"+
                        "<td hidden>"+this.unit_symbol+"</td>"+
                        "<td>"+this.return_purchase_price+"</td>"+
                        "<td hidden></td>"+
                        "<td hidden></td>"+
                        "<td>"+this.line_taxable_value+"</td>"+
                        "<td class='is_not_igst'>"+this.cgst_percent+"</td>"+
                        "<td class='is_not_igst'>"+this.cgst_value+"</td>"+
                        "<td class='is_not_igst'>"+this.sgst_percent+"</td>"+
                        "<td class='is_not_igst'>"+this.sgst_value+"</td>"+
                        "<td class='is_igst'>"+this.igst_percent+"</td>"+
                        "<td class='is_igst'>"+this.igst_value+"</td>"+
                        // "<td>"+this.tax_percent+"</td>"+
                        "<td>"+this.line_total+"</td>"+
                        "</tr>");
                });
            }
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
    if (igst_total == 0 || isNaN(igst_total)){
        $('.is_igst').addClass('hidden-print');

    }
    else{
        $('.is_not_igst').addClass('hidden-print');

    }
     window.print();
});

});