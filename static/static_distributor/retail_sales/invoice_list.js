$(function(){

var total_payment=0, page_no=0, incerease = true, decrease=false, all_invoices = true,
    unpaid_invoices = false, overdue_invoices=false;

load_invoices()

$('.all').click(function(){
    load_invoices();
    page_no+=1;
});

function load_invoices(){
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"all_invoices"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            if (incerease == true){
                page_no+=1;
            }
            else{
                page_no-=1;
            }
            $('.all').hide();
            $('.unpaid').show();
            $('.overdue').show();
            $.each(jsondata, function(){
                var url='/retailsales/invoice/detailview/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+this.cgsttotal+"</td>"+
                "<td>"+this.sgsttotal+"</td>"+
                "<td>"+this.total+"</td>"+
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });
}

// Taking care of navigation

// function navigation(){
// }

$("#receipt_table").on("click", ".link", function(){
    // console.log('here');
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    console.log(get_url)
    location.href = get_url;
});

// load_metadata()

// function load_metadata(){
//     $.ajax({
//         url : "metadata/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             console.log(jsondata);
//             if (jsondata['invoice_value']['total__sum']==null){
//                 jsondata['invoice_value']['total__sum']='0.00'
//             }
//             if (jsondata['invoice_paid']['amount_received__sum']==null){
//                 jsondata['invoice_paid']['amount_received__sum']='0.00'
//             }
//             if (jsondata['invoice_overdue']['total__sum']==null){
//                 jsondata['invoice_overdue']['total__sum']='0.00'
//             }
//             $('.value').append($.trim(jsondata['invoice_value']['total__sum']));
//             $('.paid').append($.trim(jsondata['invoice_paid']['amount_received__sum']));
//             $('.overdue_value').append($.trim(jsondata['invoice_overdue']['total__sum']));
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No sales data exist.", "error");
//         }
//     });
// }

// var end = new Date();
var end = moment();
var start = moment(end).subtract(60, 'days');

// console.log(start.format('DD-MM-YYYY'));

$('.date_range').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD/MM/YYYY',
    },
    "dateLimit": {
        "days": 30
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

