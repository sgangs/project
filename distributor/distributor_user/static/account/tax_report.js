$(function(){

var transactions=['Purchase','Sales', 'Purchase Debit','Sales Credit','Retail Sales'], dateChanged=false;


var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();

$('.apply_reset').click(function(){
    // filter_applied=false;
    // $('select').val([]).selectpicker('refresh');
    // $('.product_name').val('');
    // $('.product_id').val('');
    // $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_list();
    load_summary();
    $('#filter').modal('hide');
});


function date_update(){
// var end = new Date();
// console.log(start.format('DD-MM-YYYY'));
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


load_list()

function load_list(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"all_list",},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $(".tax_details .data").remove();
            $.each(jsondata, function(){
                $('.tax_details').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+transactions[parseInt(this.transaction_type) - 1]+"</td>"+
                "<td>"+this.transaction_bill_no+"</td>"+
                "<td>"+this.date+"</td>"+
                "<td>"+this.bill_value+"</td>"+
                "<td>"+this.customer_state+"</td>"+
                "<td>"+this.tax_type+"</td>"+
                "<td>"+this.tax_percent+ "%</td>"+
                "<td>"+this.line_wo_tax+"</td>"+
                "<td>"+this.tax_value+"</td>"+
                "<td>"+this.is_registered+"</td>"+
                "<td>"+$.trim(this.customer_gst)+"</td>"+
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
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"short_summary",
            start: startdate,
            end: enddate,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.cgstin').html($.trim(jsondata['cgst_input']));
            $('.sgstin').html($.trim(jsondata['sgst_input']));
            $('.igstin').html($.trim(jsondata['igst_input']));

            $('.cgstout').html($.trim(jsondata['cgst_output']));
            $('.sgstout').html($.trim(jsondata['sgst_output']));
            $('.igstout').html($.trim(jsondata['igst_output']));
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some errors. Please try again later.", "error");
        }
    });
}
$('.apply_filter').click(function(e) {
    filter_data();
    load_summary();
})


function filter_data() {
    tax_type=$('#type_filter').find(':selected').data('id');
    tax_percent=$('#percent_filter').find(':selected').data('id');    

    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            // tax_percent: tax_percent,
            // tax_type: tax_type,
            start: startdate,
            end: enddate,
            // vendors: JSON.stringify(vendors),
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $(".tax_details .data").remove();
            $('#filter').modal('hide');
            console.log(jsondata);

            $.each(jsondata, function(){
                $('.tax_details').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+this.transaction_bill_no+"</td>"+
                "<td>"+transactions[parseInt(this.transaction_type) - 1]+"</td>"+
                "<td>"+this.tax_type+"</td>"+
                "<td>"+this.tax_percent+ "%</td>"+
                "<td>"+this.tax_value+"</td>"+
                "<td>"+this.is_registered+"</td>"+
                
                // "<td>"+this.total+"</td>"+
                // "<td>"+this.amount_paid+"</td>"+
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

};


});

