$(function(){

load_returns()

// $('.all').click(function(){
//     load_invoices();
//     page_no+=1;
// });

// $('.apply_reset').click(function(){
//     load_invoices();
// });

function load_returns(){
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"all_returns"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $.each(jsondata, function(){
                // var url='/sales/invoice/detailview/'+this.id+'/'
                // var download_url='/sales/invoice/excel/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                // "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'></td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.return_id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+this.invoice__invoice_id+"</td>"+
                "<td>"+this.invoice__date+"</td>"+
                "<td>"+this.customer_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });
}

// Taking care of navigation

function navigation(){
    if (all_invoices == true){
        load_invoices
    }
    else if (unpaid_invoices == true){
        
    }
}



// $('.apply_filter').click(function(e) {
//     var customers=[];
//     $.each($(".customer_filter option:selected"), function(){
//         vendorid=$(this).data('id')
//         var customer={
//             customerid: customerid
//         };
//         customers.push(customer);
//     });
//     if (unpaid_receipts){
//         sent_with='unpaid_receipts'
//     }
//     else if(all_receipts){
//         sent_with='all_receipts'
//     }
//     else if(overdue_receipts){
//         sent_with='overdue_receipts'
//     }
//     invoice_no=$('.invoice_no').val()

//     $.ajax({
//         url : "listall/", 
//         type: "GET",
//         data:{ calltype:"apply_filter",
//             sent_with: sent_with,
//             start: startdate,
//             end: enddate,
//             invoice_no: invoice_no,
//             customers: JSON.stringify(customers),
//             csrfmiddlewaretoken: csrf_token},
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             $("#receipt_table .data").remove();
//             $('#filter').modal('hide');
//             $.each(jsondata, function(){
//                 var url='/purchase/receipt/detailview/'+this.id+'/'
//                 date=this.date
//                 date=date.split("-").reverse().join("-")
//                 $('#receipt_table').append("<tr class='data' align='center'>"+
//                 "<td hidden='true'>"+url+"</td>"+
//                 "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.receipt_id+"</td>"+
//                 "<td>"+this.supplier_invoice+"</td>"+
//                 "<td>"+date+"</td>"+
//                 "<td>"+$.trim(this.payable_by)+"</td>"+
//                 "<td>"+this.vendor_name+"</td>"+
//                 "<td>"+this.total+"</td>"+
//                 "<td>"+this.amount_paid+"</td>"+
//                 "</tr>");
//             })
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No purchase receipt exist.", "error");
//         }
//     });

// });



});

