$(function(){

var transactions=['Purchase','Sales']

load_receipts()

function load_receipts(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"all_receipt"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            $.each(jsondata, function(){
                $('.tax_details').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+this.transaction_bill_id+"</td>"+
                "<td>"+transactions[parseInt(this.transaction_type) - 1]+"</td>"+
                "<td>"+this.tax_type+"</td>"+
                "<td>"+this.tax_percent+ "%</td>"+
                "<td>"+this.tax_value+"</td>"+
                
                // "<td>"+this.total+"</td>"+
                // "<td>"+this.amount_paid+"</td>"+
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No tax report exist.", "error");
        }
    });
}



});

