$(function(){

// $('.all').click(function(){
//     filter_applied=false;
//     $('select').val([]).selectpicker('refresh');
//     $('.product_name').val('');
//     $('.product_id').val('');
//     $('.invoice_no').val('');
//     date_update();
//     dateChanged=false;
//     load_invoices(1);
// });

// $('.apply_reset').click(function(){
//     filter_applied=false;
//     $('select').val([]).selectpicker('refresh');
//     $('.invoice_summary').hide();
//     $('.product_name').val('');
//     $('.product_id').val('');
//     $('.invoice_no').val('');
//     date_update();
//     dateChanged=false;
//     load_invoices(1);
// });

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


$('.monthwise').click(function(e){
    // console.log('here');
    $('#filter').modal('show');
    $('.data_btn').hide();
    $('.month_data_btn').show();
    // monthwise_data(1);
});

$('.month_data_btn').click(function(e){
    monthwise_data(1);
    $('#filter').modal('hide');
});



$('.zonewise').click(function(e){
    $('#filter').modal('show');
    $('.data_btn').hide();
    $('.zone_data_btn').show();
    // zonewise_data(1);
});

$('.zone_data_btn').click(function(e){
    zonewise_data(1);
    $('#filter').modal('hide');
});

$('.datewise').click(function(e){
    $('#filter').modal('show');
    $('.data_btn').hide();
    $('.date_data_btn').show();
    // datewise_data(1);
});

$('.date_data_btn').click(function(e){
    datewise_data(1);
    $('#filter').modal('hide');
});

$('.customerwise').click(function(e){
    $('#filter').modal('show');
    $('.data_btn').hide();
    $('.customer_data_btn').show();
    // datewise_data(1);
});

$('.customer_data_btn').click(function(e){
    customerwise_data(1);
    $('#filter').modal('hide');
});

var end = moment();
var start = moment(end).subtract(30, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();

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
            "month": 4
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


function monthwise_data(page_no) {
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"monthwise",
            start: startdate,
            end: enddate,
            // page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('.data_type').attr('hidden', true);
            $('.month_data').attr('hidden', false);
            $.each(jsondata['object'], function(){
                // month[this_month.getMonth()]
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td>"+moment(this.month,"YYYY-MM-DD").format("MMM'YY")+"</td>"+
                "<td hidden></td>"+
                "<td hidden></td>"+
                "<td hidden></td>"+
                "<td>"+this.total_sales+"</td>"+
                "<td>"+this.total_paid+"</td>"+
                "</tr>");
            })
            $('.response_details').attr('hidden', false);
            // apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were errors in getting data. Try again later", "error");
        }
    });

}

function zonewise_data(page_no) {
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"zonewise",
            start: startdate,
            end: enddate,
            // page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('.data_type').attr('hidden', true);
            $('.zone_data').attr('hidden', false);
            $.each(jsondata['object'], function(){
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden></td>"+
                "<td>"+this.customer__zone__name+"</td>"+
                "<td hidden></td>"+
                "<td hidden></td>"+
                "<td>"+this.total_sales+"</td>"+
                "<td>"+this.total_paid+"</td>"+
                "</tr>");
            })
            $('.response_details').attr('hidden', false);
            // apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were errors in getting data. Try again later", "error");
        }
    });

}

function datewise_data(page_no) {
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"datewise",
            start: startdate,
            end: enddate,
            // page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('.data_type').attr('hidden', true);
            $('.date_data').attr('hidden', false);
            $.each(jsondata['object'], function(){
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden></td>"+
                "<td hidden></td>"+
                "<td>"+moment(this.date,"YYYY-MM-DD").format("DD-MM-YY")+"</td>"+
                "<td hidden></td>"+
                "<td>"+this.total_sales+"</td>"+
                "<td>"+this.total_paid+"</td>"+
                "</tr>");
            })
            $('.response_details').attr('hidden', false);
            // apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were errors in getting data. Try again later", "error");
        }
    });

}

function customerwise_data(page_no) {
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"customerwise",
            start: startdate,
            end: enddate,
            // page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('.data_type').attr('hidden', true);
            $('.customer_data').attr('hidden', false);
            $.each(jsondata['object'], function(){
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden></td>"+
                "<td hidden></td>"+
                "<td hidden></td>"+
                "<td>"+this.customer_name+"</td>"+
                "<td>"+this.total_sales+"</td>"+
                "<td>"+this.total_paid+"</td>"+
                "</tr>");
            })
            $('.response_details').attr('hidden', false);
            // apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were errors in getting data. Try again later", "error");
        }
    });

}


});

