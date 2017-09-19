$(function(){

var page_no=0, filter_applied=false;

load_transfers(1)

$('.all').click(function(){
    filter_applied=false;
    $('select').val([]).selectpicker('refresh');
    $('.product_name').val('');
    $('.product_id').val('');
    $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_transfers(1);
});

// $('.apply_reset').click(function(){
//     filter_applied=false;
//     $('select').val([]).selectpicker('refresh');
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

function load_transfers(page_no){
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"all_transfer",
            page_no:page_no},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            $("#detail_table .data").remove();
            $('#filter').modal('hide');
            
            $.each(jsondata['object'], function(){
                console.log(this);
                // var url='/sales/invoice/detailview/'+this.id+'/'
                // var download_url='/sales/invoice/excel/'+this.id+'/'
                date=this.initiated_on
                date=date.split("-").reverse().join("-")
                $('#detail_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                '<td class="text-center" hidden>'+this.id+'</td>'+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.transfer_id+"</td>"+
                '<td class="text-center">'+date+'</td>'+
                '<td class="text-center">'+this.from_warehouse_address+'</td>'+
                '<td class="text-center">'+this.to_warehouse_address+'</td>'+
                '<td class="text-center">'+this.total_value+'</td>'+
                // "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                //         "</i> Download Excel Format</button></a></td>"+
                "</tr>");
            })
            // apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No data exist.", "error");
        }
    });
}


// $("#receipt_table").on("click", ".link", function(){
//     // console.log('here');
//     get_url=$(this).closest('tr').find('td:nth-child(1)').html();
//     console.log(get_url)
//     location.href = get_url;
// });


var end = moment();
var start = moment(end).subtract(60, 'days');
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


// This is used to overlay autocomplete over the modal.
$( ".product_name" ).autocomplete({
  appendTo: "#filter"
});

$(document).on('keydown.autocomplete', '.product_name', function() {
    var el=this;
    $(this).autocomplete({
        source : "/inventory/getproduct/", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            $('.product_id').val(ui['item']['id']);
        }
    });
});

$('.apply_filter').click(function(e){
    filter_data(1);
});


function filter_data(page_no) {
    var customers=[];
    $.each($(".customer_filter option:selected"), function(){
        // if (customerid == 'undefined' || typeof(customerid) == undefined){
        if ($.trim(customerid).length>0){
            console.log("Here with id: "+customerid+" & type: "+typeof(customerid));
            var customer={
                customerid: customerid
            };
            customers.push(customer);
        }        
    });
    if (unpaid_invoices){
        sent_with='unpaid_invoices';
    }
    else if(all_invoices){
        sent_with='all_invoices';
    }
    // else if(overdue_receipts){
    //     sent_with='overdue_receipts'
    // }
    invoice_no=$('.invoice_no').val();
    productid=$('.product_id').val();
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            sent_with: sent_with,
            start: startdate,
            end: enddate,
            productid: productid,
            invoice_no: invoice_no,
            customers: JSON.stringify(customers),
            page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.invoice_summary').show();
            filter_applied=true;
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            $.each(jsondata['object'], function(){
                // var url='/sales/invoice/detailview/'+this.id+'/'
                // var download_url='/sales/invoice/excel/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'></td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.payable_by)+"</td>"+
                "<td>"+this.customer_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
                "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                        "</i> Download Excel Format</button></a></td>"+
                "</tr>");
            })
            apply_navbutton(jsondata, page_no);
            $('.amount_invoiced').html('Rs.'+jsondata['total_value'])
            $('.amount_pending').html('Rs.'+jsondata['total_pending'])
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });

}

// $(".add_nav").on("click", ".navbtn", function(){
//     if (filter_applied){
//         filter_data($(this).val())
//     }
//     else if (all_invoices){
//         load_invoices($(this).val())
//     }
//     else if (unpaid_invoices){
//         load_unpaid_invoices($(this).val())
//     }
// });

});

