$(function(){

function encodeQueryData(data) {
   let ret = [];
   for (let d in data)
     ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
   return ret.join('&');
}



// function apply_navbutton(jsondata, page_no){
//     $('.navbtn').remove()
//     for (i =jsondata['start']+1; i<=jsondata['end']; i++){
//         if (i==page_no){
//                     // $('.add_nav').append("<a href='#' class='btn nav_btn btn-sm btn-default' data=1 style='margin-right:0.2%'>"+i+"</a>")
//             $('.add_nav').append("<button title='Your Current Page' class='btn btn-sm navbtn btn-info' "+
//                 "value="+i+" style='margin-right:0.2%'>"+i+"</button>")
//         }
//         else{
//             $('.add_nav').append("<button title='Go to page no: "+i+"' class='btn btn-sm navbtn btn-default'"+
//                 " value="+i+" style='margin-right:0.2%'>"+i+"</button>")
//         }
//     }
// }


var end = moment();
var start = moment(end).subtract(15, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();

function date_update(){
startdate=start.format('DD-MM-YYYY');
enddate=end.format('DD-MM-YYYY');

$('.date_range').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD-MM-YYYY',
    },
    "dateLimit": {
        "days": 30
    },
    'autoApply':true,
    'startDate' : start,
    'endDate' : end,
    },
    function(start, end, label) {
        dateChanged=true;
        startdate=start.format('YYYY-MM-DD');
        enddate=end.format('YYYY-MM-DD');
        // $('.details').attr('disabled', false);
});
};


load_users()

function load_users(){
    $.ajax({
        url : "/user/userlist/data/", 
        type: "GET",
        data:{calltype: "get_users"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#user').append($('<option>',{
                    'data-id': this.id,
                    'text': this.first_name + " "+ this.last_name
                }));
            });
            $('#user').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some errors.", "error");
        }
    });
}

$('.get_data').click(function(e){
    $("#servicecount_table").attr("hidden", true);
    get_data(1);
});


function get_data(page_no) {
    var userid = $('.user').find(':selected').data('id');
    var user_name = $('.user').find(':selected').text();
    // console.log(user_name);
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    if (userid){
        $.ajax({
            url : "data/", 
            type: "GET",
            data:{ start: startdate,
                end: enddate,
                userid: userid,
                page_no: page_no,
                calltype:"all_invoices",
                user_name: user_name,
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                $("#report_table .data").remove();
                $("#report_table").attr("hidden", false);
                var total_qty=0;
                var total_taxable=0;
                var total_amt=0;
                // console.log(jsondata);
                $('.report_name').html("<b>Sales report for: "+user_name+"</b>")
                
                $.each(jsondata['object'], function(){
                    // total_qty+=parseFloat(this.quantities);
                    // total_taxable+=parseFloat(this.taxable_value);
                    // total_amt+=parseFloat(this.total_amount);
                    $('#report_table').append("<tr class='data' align='center'>"+
                    "<td>"+this.service_invoice__invoice_id+"</td>"+
                    "<td>"+this.service_name+"</td>"+
                    "<td>"+parseFloat(this.quantity_final)+"</td>"+
                    "<td>"+this.line_before_tax+"</td>"+
                    // "<td></td>"+
                    "<td>"+this["user_details"][userid]+"</td>"+
                    "</tr>");                
                })

                // $('#report_table').append("<tr class='data' align='center'>"+
                //     "<td><b>Total</b></td>"+
                //     "<td><b>"+parseFloat(total_qty)+"</b></td>"+
                //     "<td><b>"+total_taxable.toFixed(2)+"</b></td>"+
                //     // "<td></td>"+
                //     "<td><b>"+total_amt.toFixed(2)+"</b></td>"+
                //     "</tr>");
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "No sales detail exist.", "error");
            }
        });
    }
    else{
        swal("Ugghh...", "Select an user.", "warning");
    }

}

$('.get_data_servicewise').click(function(e){
    $("#report_table").attr("hidden", true);
    get_data_servicewise(1);
});


function get_data_servicewise(page_no) {
    var userid = $('.user').find(':selected').data('id');
    var user_name = $('.user').find(':selected').text();
    
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    
    // console.log(enddate);

    if (userid){
        $.ajax({
            url : "data/", 
            type: "GET",
            data:{ start: startdate,
                end: enddate,
                userid: userid,
                page_no: page_no,
                calltype:"service_count",
                user_name: user_name,
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                $("#servicecount_table .data").remove();
                $("#servicecount_table").attr("hidden", false);
                // console.log(jsondata);
                $('.report_name').html("<b>Sales report for: "+user_name+"</b>")
                
                $.each(jsondata['object'], function(){
                    // total_qty+=parseFloat(this.quantities);
                    // total_taxable+=parseFloat(this.taxable_value);
                    // total_amt+=parseFloat(this.total_amount);
                    
                    $('#servicecount_table').append("<tr class='data' align='center'>"+
                    "<td>"+this.service_name+"</td>"+
                    "<td>"+this.total+"</td>"+
                    "</tr>");                
                })

            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "No sales detail exist.", "error");
            }
        });
    }
    else{
        swal("Ugghh...", "Select an user.", "warning");
    }

}

$('.printout').click(function(){
    // window.print();
    $('#not_pos_print').removeClass('hidden-print')
    $('.not_pos_print').removeClass('hidden-print')

    $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: A4; margin: 0mm;}");
        text("@media print {#print{display: block;}#not_print{display: none;}}");
    
    $('.report_name').attr("hidden", false);
    
    window.print();

    $('.report_name').attr("hidden", true);
});

$('.download').click(function(e){
    // filter_data(1, 'download');
    // url='/sales/invoicelist/listall/'+get_id+'/'
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

    var userid = $('.user').find(':selected').data('id');
    var user_name = $('.user').find(':selected').text();
    if ($.trim(user_name).length == 0 || user_name == 'Select User'){
        swal("Hmm...", "Select an user.", "info");
    }
    else{
        var data = { 'userid': userid, 'start': startdate, 'end': enddate, 'user_name': user_name, 
                'calltype': 'all_invoices', 'returntype':'download' };
        var querystring = encodeQueryData(data);
        var download_url='/servicesales/user-wise-service/data/?'+querystring
        location.href = download_url;
        $('#filter').modal('hide');
    }
});


});

