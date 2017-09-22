$(function(){

var transactions=['Purchase','Sales', 'Purchase Debit','Sales Credit','Retail Sales'], dateChanged=false;


var end = moment();
var start = moment(end).subtract(30, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();

$('.apply_reset').click(function(){
    // filter_applied=false;
    // $('select').val([]).selectpicker('refresh');
    // $('.product_name').val('');
    // $('.product_id').val('');
    // $('.invoice_no').val('');
    $('.report_text').html('Current Report: General Report')
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
        "days": 31
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
                date=this.date.split("-").reverse().join("-")
                
                $('.tax_details').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+transactions[parseInt(this.transaction_type) - 1]+"</td>"+
                "<td>"+this.transaction_bill_no+"</td>"+
                "<td>"+date+"</td>"+
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

load_summary(report_type='general')

function load_summary(report_type){
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }
    $.ajax({
        url : "getdata/", 
        type: "GET",
        data:{ calltype:"short_summary",
            report_type: report_type,
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
    filter_data(report_type='general');
    load_summary(report_type='general');
    $('.report_text').html('Current Report: General Report')
})

$('.b2b_report').click(function(e) {
    filter_data(report_type='b2b');
    load_summary(report_type='b2b');
    $('.report_text').html('Current Report: B2B Report')
})

$('.b2b_download').click(function(e) {
    download_report(report_type='b2b');
})

$('.b2cl_report').click(function(e) {
    filter_data(report_type='b2cl');
    load_summary(report_type='b2cl');
    $('.report_text').html('Current Report: B2CL Report')
})

$('.b2cl_download').click(function(e) {
    download_report(report_type='b2cl');
})

$('.b2cs_report').click(function(e) {
    filter_data(report_type='b2cs');
    load_summary(report_type='b2cs');
    $('.report_text').html('Current Report: B2CS Report')
})

$('.b2cs_download').click(function(e) {
    download_report(report_type='b2cs');
})

function filter_data(report_type) {
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
            report_type: report_type,
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
                date=this.date.split("-").reverse().join("-")
                
                $('.tax_details').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td>"+transactions[parseInt(this.transaction_type) - 1]+"</td>"+
                "<td>"+this.transaction_bill_no+"</td>"+
                "<td>"+date+"</td>"+
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
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

};

function download_report(report_type) {
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

    var download_url='/account/tax-report/'+startdate+'/'+enddate+'/'+report_type+'/'
    location.href = download_url;
}


});

