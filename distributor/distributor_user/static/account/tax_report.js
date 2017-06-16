$(function(){

var transactions=['Purchase','Sales']

load_list()

function load_list(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"all_list",},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('.tax_details').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+this.transaction_bill_no+"</td>"+
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

load_summary()

function load_summary(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"short_summary",},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.cgstin').append($.trim(jsondata['cgst_input']));
            $('.sgstin').append($.trim(jsondata['sgst_input']));
            $('.igstin').append($.trim(jsondata['igst_input']));

            $('.cgstout').append($.trim(jsondata['cgst_output']));
            $('.sgstout').append($.trim(jsondata['sgst_output']));
            $('.igstout').append($.trim(jsondata['igst_output']));
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some errors. Please try again later.", "error");
        }
    });
}

$('.apply_filter').click(function(e) {
    tax_type=$('#type_filter').find(':selected').data('id');
    tax_percent=$('#percent_filter').find(':selected').data('id');    
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            tax_percent: tax_percent,
            tax_type: tax_type,
            // start: startdate,
            // end: enddate,
            // vendors: JSON.stringify(vendors),
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // $("#receipt_table .data").remove();
            // $('#filter').modal('hide');
            console.log(jsondata);
            // $.each(jsondata, function(){
            //     var url='/purchase/receipt/detailview/'+this.id+'/'
            //     date=this.date
            //     date=date.split("-").reverse().join("-")
            //     $('#receipt_table').append("<tr class='data' align='center'>"+
            //     "<td hidden='true'>"+url+"</td>"+
            //     "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.receipt_id+"</td>"+
            //     "<td>"+this.supplier_invoice+"</td>"+
            //     "<td>"+date+"</td>"+
            //     "<td>"+$.trim(this.payable_by)+"</td>"+
            //     "<td>"+this.vendor_name+"</td>"+
            //     "<td>"+this.total+"</td>"+
            //     "<td>"+this.amount_paid+"</td>"+
            //     "</tr>");
            // })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

});


});

