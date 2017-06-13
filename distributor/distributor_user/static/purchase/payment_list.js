$(function(){

var total_payment=0;

load_receipts()

function load_receipts(){
    $.ajax({
        url : "/purchase/paymentlist/", 
        type: "GET",
        // data:{ calltype:"all_receipt"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {

            $.each(jsondata, function(){
                // console.log(this.purchase_receipt.id);
                rec_date=this.purchase_receipt.date
                rec_date=rec_date.split("-").reverse().join("-")

                pay_date=this.paid_on
                pay_date=pay_date.split("-").reverse().join("-")
                
                $('#payment_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+this.purchase_receipt.receipt_id+"</td>"+
                "<td>"+this.purchase_receipt.supplier_invoice+"</td>"+
                "<td>"+rec_date+"</td>"+
                "<td>"+$.trim(this.purchase_receipt.payable_by)+"</td>"+
                "<td>"+this.purchase_receipt.vendor_name+"</td>"+
                "<td>"+this.purchase_receipt.total+"</td>"+
                "<td>"+this.purchase_receipt.amount_paid+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
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



});

