$(function(){

transaction_types = ['', 'Debit', 'Credit']

load_journals()

// $('.all').click(function(){
//     load_invoices();
//     page_no+=1;
// });

// $('.apply_reset').click(function(){
//     load_invoices();
// });

function load_journals(){
    account_pk = pk;
    $.ajax({
        url : "/account/journallist/account-list/", 
        type: "GET",
        data:{ calltype:"all_journal",
            account_pk: account_pk},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#journal_table .data").remove();
            $.each(jsondata['object'], function(){
                date=this.journal__date;
                date=date.split("-").reverse().join("-")
                if (this.transaction_type == 1){
                    $('#journal_table').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+date+"</td>"+
                    "<td align='left'>"+transaction_types[this.transaction_type]+"</td>"+
                    "<td>"+this.journal__remarks+"</td>"+
                    "<td>"+this.value+"</td>"+
                    "<td></td>"+
                    "</tr>");
                }
                else{
                    $('#journal_table').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+date+"</td>"+
                    "<td align='right'>"+transaction_types[this.transaction_type]+"</td>"+
                    "<td>"+this.journal__remarks+"</td>"+
                    "<td></td>"+
                    "<td>"+this.value+"</td>"+
                    "</tr>");
                }
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch journal data. Kindly try after some time.", "error");
        }
    });
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

