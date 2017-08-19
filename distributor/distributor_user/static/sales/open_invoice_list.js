$(function(){

var total_payment=0, page_no=0, incerease = true, decrease=false, all_invoices = true,
    unpaid_invoices = false, overdue_invoices=false;

load_invoices(1)

$('.all').click(function(){
    load_invoices();
    page_no+=1;
});

$('.apply_reset').click(function(){
    load_invoices();
    $('select').val([]).selectpicker('refresh');
    date_update();
    dateChanged=false;
});

$('.hintbtn').click(function(){
    $('#hint').modal('show');
    // load_invoices();
    // page_no+=1;
});

function load_invoices(page_no){
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"all_invoices",
            page_no: page_no},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('.navbtn').remove()
            $('#filter').modal('hide');
            $.each(jsondata['object'], function(){
                var url='/sales/invoice/detailview/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.payable_by)+"</td>"+
                "<td>"+this.customer_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td><input type='checkbox'></td>"+
                "</tr>");
            })
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
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });
}

$(".add_nav").on("click", ".navbtn", function(){
    load_invoices($(this).val())
});

// Taking care of navigation


$("#receipt_table").on("click", ".link", function(){
    // console.log('here');
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    console.log(get_url)
    location.href = get_url;
});


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


load_customer()

function load_customer(){
    $.ajax({
        url : "/master/customer/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#customer_filter').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#customer_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
        }
    });
}


$('.apply_filter').click(function(e) {
    var customers=[];
    $.each($(".customer_filter option:selected"), function(){
        customerid=$(this).data('id');
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
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            sent_with: sent_with,
            start: startdate,
            end: enddate,
            invoice_no: invoice_no,
            customers: JSON.stringify(customers),
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            $.each(jsondata, function(){
                var url='/sales/invoice/detailview/'+this.id+'/'
                var download_url='/sales/invoice/excel/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
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
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });

});


load_payment()

function load_payment(){
    $.ajax({
        url : "/account/payment-mode/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#mode').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            $('#mode').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in retriving payment mode data.", "error");
        }
    });
}


$('.finalizebtn').click(function(){
    // post_data("Finalize");
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to finalize and save the invoice?</p><p>Note that you cannot edit this invoice once finalized.</p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, finalize invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm("Finalize")},600)            
        }
    })    
});

$('.deletebtn').click(function(){
    // post_data("Delete");
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to delete the invoice?</p><p>Note that you cannot edit or view this invoice once deleted. "+
                "No record of this invoice shall exist. </p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm("Delete")},600)            
        }
    })
});

$('.cancelbtn').click(function(){
    // post_data("Delete");
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to cancel the invoice?</p><p>Note that you cannot edit this invoice once deleted. "+
                "You can see the list of canceled invoices. </p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, cancel invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm("Cancel")},600)            
        }
    })
});

function reconfirm(calltype){
   swal({
        title: "Please Reconfirm",
        text: "This process cannot be undone. Please reconfirm.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){post_data(calltype)},600)            
        }
    }) 
}

function post_data(calltype){
    console.log(calltype);
    items=[];
    $("tr.data").each(function() {
        var invoice_id = $(this).find('td:nth-child(2)').html();
        var is_selected = $(this).find('td:nth-child(8) input').is(":checked");
        if (is_selected){
            var item = {
                invoice_id : invoice_id,
            };
            items.push(item);
        }
    });
    if (items.length > 0){
        $.ajax({
            url : "save/", 
            type: "POST",
            data: {invoices_list: JSON.stringify(items),
                // calltype: "Finalize",
                calltype: calltype,
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                swal("Hooray...", "Invoice status updated and saved.", "success");
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "There were errors in saving data.", "error");
            }
        });
    }
    else{
        swal("Oops...", "Please select atleast one invoice.", "info");
    }
};



});

