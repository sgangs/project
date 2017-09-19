$(function(){

var total_payment=0, page_no=0, incerease = true, decrease=false, all_invoices = true,
    unpaid_invoices = false, overdue_invoices=false, filter_applied=false;

$('.overdue').hide();
$('.invoice_summary').hide();

load_invoices(1)

$('.all').click(function(){
    filter_applied=false;
    $('select').val([]).selectpicker('refresh');
    $('.product_name').val('');
    $('.product_id').val('');
    $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_invoices(1);
});

$('.apply_reset').click(function(){
    filter_applied=false;
    $('select').val([]).selectpicker('refresh');
    $('.product_name').val('');
    $('.product_id').val('');
    $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_invoices(1);
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

function load_invoices(page_no){
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"all_invoices",
            page_no:page_no},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.invoice_summary').hide();
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            
            all_invoices = true; unpaid_invoices = false; overdue_invoices=false;
            
            $('.all').hide();
            $('.unpaid').show();
            // $('.overdue').show();
            $.each(jsondata['object'], function(){
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
            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });
}

$('.unpaid').click(function(){
    filter_applied=false;
    $('select').val([]).selectpicker('refresh');
    $('.product_name').val('');
    $('.product_id').val('');
    $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_unpaid_invoices(1);
});

function load_unpaid_invoices(page_no) {
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"unpaid_invoices",
            page_no: page_no},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.invoice_summary').hide();
            $("#receipt_table .data").remove();
            all_invoices = false; unpaid_invoices = true; overdue_invoices=false;
            $('.all').show();
            $('.unpaid').hide();
            // $('.overdue').show();
            $.each(jsondata['object'], function(){
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
            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });

};


$("#receipt_table").on("click", ".link", function(){
    // console.log('here');
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    console.log(get_url)
    location.href = get_url;
});

load_metadata()

function load_metadata(){
    $.ajax({
        url : "metadata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            if (jsondata['invoice_value']['total__sum']==null){
                jsondata['invoice_value']['total__sum']='0.00'
            }
            if (jsondata['invoice_paid']['amount_received__sum']==null){
                jsondata['invoice_paid']['amount_received__sum']='0.00'
            }
            if (jsondata['invoice_overdue']['total__sum']==null){
                jsondata['invoice_overdue']['total__sum']='0.00'
            }
            $('.value').append($.trim(jsondata['invoice_value']['total__sum']));
            $('.paid').append($.trim(jsondata['invoice_paid']['amount_received__sum']));
            $('.overdue_value').append($.trim(jsondata['invoice_overdue']['total__sum']));
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales data exist.", "error");
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
                $('#customer').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
                $('#customer_filter').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#customer').selectpicker('refresh');
            $('#customer_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
        }
    });
}

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
        customerid=$(this).data('id');
        // if (customerid == 'undefined' || typeof(customerid) == undefined){
        if ($.trim(customerid).length>0){
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
        url : "listall/", 
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

$(".add_nav").on("click", ".navbtn", function(){
    if (filter_applied){
        filter_data($(this).val())
    }
    else if (all_invoices){
        load_invoices($(this).val())
    }
    else if (unpaid_invoices){
        load_unpaid_invoices($(this).val())
    }
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


$('.customer').change(function() {
    customerid=parseInt($(".customer").find(':selected').data('id'));
    if (customerid != 'undefined'){
        (function() {
            $.ajax({
                url : "listall/", 
                type: "GET",
                data:{ customerid: customerid,
                    calltype:"customer_pending"},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                    $("#payment_table .payment_data").remove();
                    if (jsondata.object.length>0){
                    
                        $('.detaildiv').attr('hidden',false);
                        $('.register').attr('disabled',false);
                        $.each(jsondata.object, function(){
                            pending=parseFloat(this.total) - parseFloat(this.amount_paid)
                            $('#payment_table').append("<tr class='payment_data' align='center'>"+
                            "<td hidden='true'>"+this.id+"</td>"+
                            "<td>"+this.invoice_id+"</td>"+
                            "<td>"+this.total+"</td>"+
                            // "<td>"+this.amount_paid+"</td>"+
                            "<td>"+pending.toFixed(2)+"</td>"+
                            "<td><input type='checkbox'></td>"+
                            "<td><input type = 'number' class='form-control'></td>"+
                            "<td><input type = 'text' class='form-control cheque_rtgs'></td>"+
                            "</tr>");
                        });
                    }
                },
                        // handle a non-successful response
                error : function() {
                    swal("Oops..", "it seems no pending invoice exist.", "error");
                }
            });
        }());
    }
});



$('.register').click(function(e) {
    var total_payment_check=0
    var count = 0
    $("#payment_table tr.payment_data").each(function() {
        var is_paid = $(this).find('td:nth-child(5) input').is(":checked");
        if (is_paid){
            var amount = parseFloat($(this).find('td:nth-child(6) input').val());
            total_payment_check+=amount
            count++
        }
    });

    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to register payment details?</p><p>Total Payments to be recorded: <b>Rs."
                +total_payment_check+"</b></p><p> Total number of invoices against which payment is made: <b>"+count+"</b></p>",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, register payment details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data()},600)            
        }
    })
});

function reconfirm(){

}
    
function new_data(){
    var items=[];
    total_payment=0;
    var bill_count=0;
    var proceed=true;
    customerid=$('.customer').find(':selected').data('id');
    modeid=$('.mode').find(':selected').data('id');
    date=$('.date_payment').val();
    //we need to consider payment mode as well.
    
    if (customerid == '' || customerid =='undefined' || modeid == '' || modeid =='undefined'){
        proceed = false;
        swal({
            title: "Oops..",
            text: "Please select a customer and a payment mode.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });
    }

    if (date == '' || date =='undefined'){
        proceed = false;
        swal({
            title: "Oops..",
            text: "Please enter the payment collection date.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });   
    }

    if (modeid == '' || modeid =='undefined' || typeof(modeid) == 'undefined' ){
        proceed = false;
        swal({
            title: "Oops..",
            text: "Please select a payment mode.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });   
    }

    $("#payment_table tr.payment_data").each(function() {
        var invoice_pk = $(this).find('td:nth-child(1)').html();
        var amount_pending=$(this).find('td:nth-child(4)').html();
        var is_paid = $(this).find('td:nth-child(5) input').is(":checked");
        if (is_paid){
            bill_count+=1;
            var amount = parseFloat($(this).find('td:nth-child(6) input').val());
            var cheque_rtgs_number = $(this).find('td:nth-child(7) input').val()
            total_payment+=amount
            if (isNaN(amount) || amount<=0){
                proceed=false;
                swal({
                    title: "Oops..",
                    text: "Amount must be a positive number.",
                    type: "error",
                    allowOutsideClick: true,
                    timer:2500,
                });
                $(this).closest('tr').addClass("has-error");    
            }
            else if (amount>Math.ceil(amount_pending)){
                console.log("here");
                proceed=false;
                swal({
                    title: "Oops..",
                    text: "Amount must not be greater than amount pending.",
                    type: "error",
                    allowOutsideClick: true,
                    timer:2500,
                });
                $(this).closest('tr').addClass("has-error");    
            }
            else{
                $(this).closest('tr').removeClass("has-error");   
                var item = {
                    invoice_pk : invoice_pk,
                    amount: amount,
                    cheque_rtgs_number: cheque_rtgs_number,
                };
                items.push(item);
            }
        }
    });

    if (isNaN(total_payment)){
        proceed=false;
    }
    if (bill_count <1 || total_payment == 0){
        proceed=false;
        swal({
            title: "Oops..",
            text: "Select atleast one bill against which payment is made.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });
    }

    if (proceed){
        (function() {
            $.ajax({
                url : "/sales/invoice/paymentsave/" , 
                type: "POST",
                data:{customerid: customerid,
                    modeid:modeid,
                    date:date.split("/").reverse().join("-"),
                    total_payment: total_payment,
                    payment_details: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Payment details registered.", "success");
                        setTimeout(location.reload(true),1000);
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
}


});

