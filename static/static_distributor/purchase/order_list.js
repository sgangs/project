$(function(){

var filter_applied=false;

load_receipts(1)

$('.all').click(function(){
    load_receipts(1);
});

$('.apply_reset').click(function(){
    filter_applied=false;
    load_receipts(1);
});

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

function load_receipts(page_no){
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"all_receipt",
                page_no: page_no,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // console.log(jsondata);
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            $.each(jsondata['object'], function(){
                var url='/purchase/order/detailview/'+this.id+'/'
                if (this.is_closed){
                    var is_closed = 'Yes'
                }
                else{
                    var is_closed = 'No'
                }
                // var download_url='/purchase/receipt/excel/'+this.id+'/'
                var this_id=this.id
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'></td>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.order_id+"</td>"+
                "<td>"+this.supplier_order+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.delivery_by)+"</td>"+
                "<td>"+this.vendor_name+"</td>"+
                "<td>"+this.total+"</td>"+
                // "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                //         "</i> Download Excel Format</button></a></td>"+
                // "<td class='delete' style='text-decoration: underline; cursor: pointer'>Delete Invoice</td>"+
                "<td>"+is_closed+"</td>"+
                "<td class='receipt' style='text-decoration: underline; cursor: pointer'>Generate purchase receipt</td>"+
                "<td class='delete' style='text-decoration: underline; cursor: pointer'>Delete order</td>"+
                "</tr>");
            })

            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase order exist.", "error");
        }
    });
}


var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
// console.log(start.format('DD-MM-YYYY'));

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


$('.apply_filter').click(function(e){
    filter_data(1);
});


function filter_data(page_no) {
    var vendors=[];
    $.each($(".vendor_filter option:selected"), function(){
        vendorid=$(this).data('id')
        var vendor={
            vendorid: vendorid
        };
        vendors.push(vendor);
    });

    var order_type = $('.order_type :selected').data('id');
    
    order_id=$('.order_no').val()
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true; 
    }
    
    // console.log(order_type);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            start: startdate,
            end: enddate,
            order_type: order_type,
            order_id: order_id,
            page_no: page_no,
            vendors: JSON.stringify(vendors),
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            filter_applied=true;
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            // $.each(jsondata['object'], function(){
            //     var url='/purchase/receipt/detailview/'+this.id+'/'
            //     var download_url='/purchase/receipt/excel/'+this.id+'/'
            //     var this_id=this.id
            //     date=this.date
            //     date=date.split("-").reverse().join("-")
            //     $('#receipt_table').append("<tr class='data' align='center'>"+
            //     "<td hidden='true'>"+url+"</td>"+
            //     "<td hidden='true'>"+this_id+"</td>"+
            //     "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.receipt_id+"</td>"+
            //     "<td>"+this.supplier_invoice+"</td>"+
            //     "<td>"+date+"</td>"+
            //     "<td>"+$.trim(this.payable_by)+"</td>"+
            //     "<td>"+this.vendor_name+"</td>"+
            //     "<td>"+this.total+"</td>"+
            //     "<td>"+this.amount_paid+"</td>"+
            //     "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
            //             "</i> Download Excel Format</button></a></td>"+
            //     "<td class='link' style='text-decoration: underline; cursor: pointer'>Delete Invoice</td>"+
            //     "</tr>");
            // })

            $.each(jsondata['object'], function(){
                var url='/purchase/order/detailview/'+this.id+'/'
                if (this.is_closed){
                    var is_closed = 'Yes'
                }
                else{
                    var is_closed = 'No'
                }
                // var download_url='/purchase/receipt/excel/'+this.id+'/'
                var this_id=this.id
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'></td>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.order_id+"</td>"+
                "<td>"+this.supplier_order+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.delivery_by)+"</td>"+
                "<td>"+this.vendor_name+"</td>"+
                "<td>"+this.total+"</td>"+
                // "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                //         "</i> Download Excel Format</button></a></td>"+
                // "<td class='delete' style='text-decoration: underline; cursor: pointer'>Delete Invoice</td>"+
                "<td>"+is_closed+"</td>"+
                "<td class='receipt' style='text-decoration: underline; cursor: pointer'>Generate purchase receipt</td>"+
                "<td class='delete' style='text-decoration: underline; cursor: pointer'>Delete order</td>"+
                "</tr>");
            })

            apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

};

$(".add_nav").on("click", ".navbtn", function(){
    // console.log(unpaid_invoices)
    // console.log(all_invoices)
    // console.log(filter_applied)
    if (filter_applied){
        filter_data($(this).val())
    }
    else{
        load_receipts($(this).val())
    }
});

$("#receipt_table").on("click", ".link", function(){
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    location.href = get_url;
});


$("#receipt_table").on("click", ".receipt", function(){
    get_id=$(this).closest('tr').find('td:nth-child(3)').html();
    is_closed = $(this).closest('tr').find('td:nth-child(10)').html();
    if(is_closed == 'Yes'){
        swal("Ehhh...", "This order is already closed", "info");
    }
    else{
        url='/purchase/receipt-order/'+get_id+'/'
        location.href = url;
    }
});

$("#receipt_table").on("click", ".delete", function(){
    get_id=$(this).closest('tr').find('td:nth-child(3)').html();
    is_closed = $(this).closest('tr').find('td:nth-child(10)').html();
    if(is_closed == 'Yes'){
        swal("Ehhh...", "This order is already closed. This cannot be deleted.", "info");
    }
    else{
        $.ajax({
            url : "/purchase/order/delete/", 
            type: "POST",
            data:{order_pk: get_id,
                calltype: 'delete',
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',
                // handle a successful response
            success : function(jsondata) {
                if (jsondata == 'Success'){
                    swal("Hooray", "Purchase order is deleted.", "success");
                    setTimeout(location.reload(true),1000);
                }
                else{
                    swal("Oops...", jsondata, "error");
                }
            },
                // handle a non-successful response
            error : function() {
                swal("Oops...", "There were some error. Please try again later.", "error");
            }
        });
    }
});


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
//     console.log(paid);
    
// });

function delete_invoice(get_id){
    console.log(get_id);
    $.ajax({
        url : "/purchase/receipt/delete/", 
        type: "POST",
        data:{calltype: "delete",
            receipt_pk: get_id,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            swal("Hooray", "Purchase order deleted.", "success");
            setTimeout(location.reload(true),1000);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some error. Please try again later.", "error");
        }
    });
}




load_vendor()

function load_vendor(){
    $.ajax({
        url : "/master/vendor/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#vendor').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
                $('#vendor_filter').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#vendor_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No vendor data exist.", "error");
        }
    });
}



});

