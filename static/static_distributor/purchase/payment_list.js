$(function(){

var total_payment=0, page_no=0, filter_applied = false;

var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();


function apply_navbutton(jsondata, page_no){
    $('.navbtn').remove()
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
}

$('.apply_reset').click(function(){
    filter_applied=false;
    $('select').val([]).selectpicker('refresh');
    $('.vendor_filter').val('');
    $('.receipt_no').val('');
    $('.cheque_rtgs').val('');
    date_update();
    dateChanged=false;
    load_receipts(1);
    $('#filter').modal('hide');
});


load_receipts(1)

function load_receipts(page_no){
    
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

    $.ajax({
        url : "/purchase/paymentlist/", 
        type: "GET",
        data:{ calltype:"all_receipt",
            page_no: page_no,
            start: startdate,
            end: enddate},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#payment_table .data").remove();

            $.each(jsondata['object'], function(){
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
            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch payment data. Kindly rety after some time.", "error");
        }
    });
}


load_vendors()

function load_vendors(){
    $.ajax({
        url : "/master/vendor/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#vendor_filter').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#vendor_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not load vendor data. Kindly try aain later.", "error");
        }
    });
}


function date_update(){
startdate=start.format('DD-MM-YYYY');
enddate=end.format('DD-MM-YYYY');

$('.date_range').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD-MM-YYYY',
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
        dateChanged=true;
        startdate=start.format('YYYY-MM-DD');
        enddate=end.format('YYYY-MM-DD');
        $('.details').attr('disabled', false);
});
};


$('.apply_filter').click(function(e){
    filter_data(1);
});


function filter_data(page_no) {
    var vendors = [];
    $.each($(".vendor_filter option:selected"), function(){
        vendorid=$(this).data('id');
        // if (customerid == 'undefined' || typeof(customerid) == undefined){
        if ($.trim(vendorid).length>0){
            var vendor={
                vendorid: vendorid
            };
            vendors.push(vendor);
        }        
    });
    // else if(overdue_receipts){
    //     sent_with='overdue_receipts'
    // }
    receipt_no=$('.receipt_no').val();
    
    cheque_rtgs=$('.cheque_rtgs').val();
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    
    $.ajax({
        url : "/purchase/paymentlist/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            start: startdate,
            end: enddate,
            receipt_no: receipt_no,
            cheque_rtgs: cheque_rtgs,
            vendors: JSON.stringify(vendors),
            page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#payment_table .data").remove();
            $('#filter').modal('hide');

            filter_applied=true;

            console.log(jsondata);
            
            $.each(jsondata['object'], function(){
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
            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch collection data. Kindly try again later.", "error");
        }
    });

}

$(".add_nav").on("click", ".navbtn", function(){
    if (filter_applied){
        filter_data($(this).val())
    }
    else{
        load_receipts($(this).val())
    }
});



});

