$(function(){

var total_payment=0, filter_applied=false;

load_returns(1)

$('.all').click(function(){
    filter_applied=false;
    date_update();
    dateChanged=false;
    load_returns(1);
});

$('.apply_reset').click(function(){
    $('.invoice_summary').hide();
    filter_applied=false;
    date_update();
    dateChanged=false;
    load_returns(1);
});

function error_messages_display(msg, timer){
    swal({
        title: "Oops..",
        text: msg,
        type: "error",
        allowOutsideClick: true,
        timer:timer,
    });
}



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

function load_returns(page_no){
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"all_return",
                page_no: page_no,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            $.each(jsondata['object'], function(){
                var url='/purchase/return/detailview/'+this.id+'/'
                // var this_id=this.id
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                // "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td><a href="+url+" class='new_link'>"+this.note_id+"</a></td>"+
                "<td>"+this.note_id+"</td>"+
                "<td>"+this.supplier_note_no+"</td>"+
                "<td>"+this.adjustmnet_receipt_no+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+this.vendor_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td class='delete' style='text-decoration: underline; cursor: pointer'>Delete Invoice</td>"+
                "</tr>");
            })

            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch data. Kindly retry later", "error");
        }
    });
}

var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();

function date_update(){
// var end = new Date();
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


// $('.apply_filter').click(function(e){
//     filter_data(1);
// });


function filter_data(page_no) {
    var vendors=[];
    $.each($(".vendor_filter option:selected"), function(){
        vendorid=$(this).data('id')
        var vendor={
            vendorid: vendorid
        };
        vendors.push(vendor);
    });
    
    invoice_no=$('.invoice_no').val()

    order_no=$('.order_no').val()

    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true; 
    }
    // console.log(startdate);

    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            sent_with: sent_with,
            start: startdate,
            end: enddate,
            invoice_no: invoice_no,
            order_no: order_no,
            page_no: page_no,
            vendors: JSON.stringify(vendors),
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            filter_applied=true;
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            $.each(jsondata['object'], function(){
                var url='/purchase/receipt/detailview/'+this.id+'/'
                var download_url='/purchase/receipt/excel/'+this.id+'/'
                var this_id=this.id
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'>"+this_id+"</td>"+
                // "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.receipt_id+"</td>"+
                "<td><a href="+url+" class='new_link'>"+this.receipt_id+"</a></td>"+
                "<td>"+this.supplier_invoice+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.payable_by)+"</td>"+
                "<td>"+this.vendor_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
                "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                        "</i> Download Excel Format</button></a></td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>Delete Invoice</td>"+
                "</tr>");
            })

            apply_navbutton(jsondata, page_no);
            if (page_no == 1){
                $('.invoice_summary').show();
                $('.amount_invoiced').html('Rs.'+jsondata['total_value'])
                $('.amount_pending').html('Rs.'+jsondata['total_pending'])
            }
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

};

$(".add_nav").on("click", ".navbtn", function(){
    if (filter_applied){
        filter_data($(this).val())
    }
    else {
        load_returns($(this).val())
    }
    
});

// $("#receipt_table").on("click", ".link", function(){
//     // console.log('here');
//     get_url=$(this).closest('tr').find('td:nth-child(1)').html();
//     location.href = get_url;
// });


// $("#receipt_table").on("click", ".delete", function(){
//     // console.log('here');
//     get_id=$(this).closest('tr').find('td:nth-child(2)').html();
//     paid=$(this).closest('tr').find('td:nth-child(9)').html();
//     if (paid == 0.00){
//         swal({
//             title: "Are you sure?",
//             text: "Are you sure you want to delete the invoice?",
//             type: "warning",
//             showCancelButton: true,
//           // confirmButtonColor: "#DD6B55",
//             confirmButtonText: "Yes, delete invoice!",
//             closeOnConfirm: true,
//             closeOnCancel: true,
//             html: false
//         }, function(isConfirm){
//             if (isConfirm){
//                 setTimeout(function(){delete_invoice(get_id)},600)            
//             }
//         })
//     }
//     else{
//         swal("Err...", "Purchase invoice against which payment has been made cannot be deleted", "warning");
//     }
//     // console.log(paid);
    
// });

// function delete_invoice(get_id){
//     $.ajax({
//         url : "/purchase/receipt/delete/", 
//         type: "POST",
//         data:{calltype: "delete",
//             receipt_pk: get_id,
//             csrfmiddlewaretoken: csrf_token},
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             if (jsondata.length > 0){
//                 swal("Err...", jsondata, "error");    
//             }
//             else{
//                 swal("Hooray", "Purchase invoice deleted.", "success");
//             }
//             // setTimeout(location.reload(true),1000);
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "There were some error. Please try again later.", "error");
//         }
//     });
// }


// load_vendor()

// function load_vendor(){
//     $.ajax({
//         url : "/master/vendor/getdata/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             $.each(jsondata, function(){
//                 $('#vendor').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//                 $('#vendor_filter').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//                 $('#vendor_opening').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//                 $('#vendor_opening_pay').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//             });
//             $('#vendor').selectpicker('refresh');
//             $('#vendor_filter').selectpicker('refresh');
//             $('#vendor_opening').selectpicker('refresh');
//             $('#vendor_opening_pay').selectpicker('refresh');
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No warehouse data exist.", "error");
//         }
//     });
// }


});

