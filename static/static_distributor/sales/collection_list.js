$(function(){

var total_payment=0;

load_receipts()

function load_receipts(){
    $.ajax({
        url : "/sales/collectionlist/", 
        type: "GET",
        // data:{ calltype:"all_receipt"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {

            $.each(jsondata, function(){
                // console.log(this.purchase_receipt.id);
                rec_date=this.sales_invoice.date
                rec_date=rec_date.split("-").reverse().join("-")

                pay_date=this.paid_on
                pay_date=pay_date.split("-").reverse().join("-")
                
                $('#payment_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+this.sales_invoice.invoice_id+"</td>"+
                // "<td>"+this.purchase_receipt.supplier_invoice+"</td>"+
                "<td>"+rec_date+"</td>"+
                "<td>"+$.trim(this.sales_invoice.payable_by)+"</td>"+
                "<td>"+this.sales_invoice.customer_name+"</td>"+
                "<td>"+this.sales_invoice.total+"</td>"+
                "<td>"+this.sales_invoice.amount_paid+"</td>"+
                "<td>"+this.amount_received+"</td>"+
                "<td>"+pay_date+"</td>"+
                "<td>"+this.payment_mode_name+"</td>"+
                "<td>"+$.trim(this.cheque_rtgs_number)+"</td>"+
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No payment data exist.", "error");
        }
    });
}


var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
// console.log(start.format('DD-MM-YYYY'));

$('.date_range').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD/MM/YYYY',
    },
    "dateLimit": {
        "days": 90
    },
    'autoApply':true,
    // 'minDate': moment(start),
    // 'maxDate': moment(end)  
    'startDate' : start,
    'endDate' : end,
    },
    function(start, end, label) {
        startdate=start.format('YYYY-MM-DD');
        enddate=end.format('YYYY-MM-DD');
        $('.details').attr('disabled', false);
});



});

