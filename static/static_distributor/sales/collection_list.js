$(function(){

var total_payment=0, page_no=0;

load_receipts(1);

function load_receipts(page_no){
    $.ajax({
        url : "/sales/collectionlist/", 
        type: "GET",
        // data:{ calltype:"all_receipt"},
        data:{ page_no: page_no},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#payment_table .data").remove();
            $('.navbtn').remove();

            $.each(jsondata['object'], function(){
                console.log(this);
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
            for (i =jsondata['start']+1; i<=jsondata['end']; i++){
                if (i==page_no){
                    // $('.add_nav').append("<a href='#' class='btn nav_btn btn-sm btn-default' data=1 style='margin-right:0.2%'>"+i+"</a>")
                    $('.add_nav').append("<button title='Your Current Page' class='btn btn-sm navbtn btn-info' "+
                        "value="+i+" style='margin-right:0.2%'>"+i+"</button>")
                }
                else{
                    $('.add_nav').append("<button title='Go to page no: "+i+"' class='btn btn-sm navbtn btn-default'"+
                        " value="+i+" style='margin-right:0.2%'>"+i+"</button>")
                }
            }
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No payment data exist.", "error");
        }
    });
}

$(".add_nav").on("click", ".navbtn", function(){
    load_receipts($(this).val())
});

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

