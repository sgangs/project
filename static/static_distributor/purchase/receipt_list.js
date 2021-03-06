$(function(){

var total_payment=0, all_receipts = true, unpaid_receipts = false, overdue_receipts=false, filter_applied=false;

load_receipts(1)

$('.invoice_summary').hide();

$('.updateOpening').click(function(){
    $('#openBalanceOption').modal('hide');
    $('#openBalance').modal('show');
})

$('.paymentOpening').click(function(){
    $('#openBalanceOption').modal('hide');
    $('#openBalancePayment').modal('show');
})


$('.all').click(function(){
    filter_applied=false;
    date_update();
    dateChanged=false;
    load_receipts(1);
});

$('.apply_reset').click(function(){
    $('.invoice_summary').hide();
    filter_applied=false;
    date_update();
    dateChanged=false;
    load_receipts(1);
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

function load_receipts(page_no){
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"all_receipt",
                page_no: page_no,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            $('.all').hide();
            $('.unpaid').hide();
            $('.overdue').hide();
            $('#filter').modal('hide');
            all_receipts=true, unpaid_receipts = false; overdue_receipts = false;
            $.each(jsondata['object'], function(){
                var url='/purchase/receipt/detailview/'+this.id+'/'
                var download_url='/purchase/receipt/excel/'+this.id+'/'
                var this_id=this.id
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td hidden='true'>"+this_id+"</td>"+
                "<td><a href="+url+" class='new_link'>"+this.receipt_id+"</a></td>"+
                "<td>"+this.supplier_invoice+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.payable_by)+"</td>"+
                "<td>"+this.vendor_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
                "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                        "</i> Download Excel Format</button></a></td>"+
                "<td class='delete' style='text-decoration: underline; cursor: pointer'>Delete Invoice</td>"+
                "</tr>");
            })

            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });
}

$('.unpaid').click(function(){
    load_unpaid_receipts(1);
});


function load_unpaid_receipts(page_no) {
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"unpaid_receipt",
                page_no: page_no,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.all').show();
            $('.unpaid').hide();
            $('.overdue').show();
            $("#receipt_table .data").remove();
            all_receipts=false, unpaid_receipts = true; overdue_receipts = false;
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

            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

};

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
    if (unpaid_receipts){
        sent_with='unpaid_receipts'
    }
    else if(all_receipts){
        sent_with='all_receipts'
    }
    else if(overdue_receipts){
        sent_with='overdue_receipts'
    }
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
    else if (all_receipts){
        load_receipts($(this).val())
    }
    else if (unpaid_invoices){
        load_unpaid_invoices($(this).val())
    }
});

$("#receipt_table").on("click", ".link", function(){
    // console.log('here');
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    location.href = get_url;
});


$("#receipt_table").on("click", ".delete", function(){
    // console.log('here');
    get_id=$(this).closest('tr').find('td:nth-child(2)').html();
    paid=$(this).closest('tr').find('td:nth-child(9)').html();
    if (paid == 0.00){
        swal({
            title: "Are you sure?",
            text: "Are you sure you want to delete the invoice?",
            type: "warning",
            showCancelButton: true,
          // confirmButtonColor: "#DD6B55",
            confirmButtonText: "Yes, delete invoice!",
            closeOnConfirm: true,
            closeOnCancel: true,
            html: false
        }, function(isConfirm){
            if (isConfirm){
                setTimeout(function(){delete_invoice(get_id)},600)            
            }
        })
    }
    else{
        swal("Err...", "Purchase invoice against which payment has been made cannot be deleted", "warning");
    }
    // console.log(paid);
    
});

function delete_invoice(get_id){
    $.ajax({
        url : "/purchase/receipt/delete/", 
        type: "POST",
        data:{calltype: "delete",
            receipt_pk: get_id,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            if (jsondata.length > 0){
                swal("Err...", jsondata, "error");    
            }
            else{
                swal("Hooray", "Purchase invoice deleted.", "success");
            }
            // setTimeout(location.reload(true),1000);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some error. Please try again later.", "error");
        }
    });
}


load_metadata()

function load_metadata(){
    $.ajax({
        url : "metadata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            if (jsondata['receipts_value']['total__sum']==null){
                jsondata['receipts_value']['total__sum']='0.00'
            }
            if (jsondata['receipts_paid']['amount_paid__sum']==null){
                jsondata['receipts_paid']['amount_paid__sum']='0.00'
            }
            if (jsondata['receipts_overdue']['total__sum']==null){
                jsondata['receipts_overdue']['total__sum']='0.00'
            }
            $('.value').append($.trim(jsondata['receipts_value']['total__sum']));
            $('.paid').append($.trim(jsondata['receipts_paid']['amount_paid__sum']));
            $('.overdue_value').append($.trim(jsondata['receipts_overdue']['total__sum']));
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase data exist.", "error");
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
                $('#vendor_opening').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
                $('#vendor_opening_pay').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#vendor').selectpicker('refresh');
            $('#vendor_filter').selectpicker('refresh');
            $('#vendor_opening').selectpicker('refresh');
            $('#vendor_opening_pay').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
        }
    });
}


$('.vendor').change(function() {
    vendorid=parseInt($(".vendor").find(':selected').data('id'));
    if (vendorid != 'undefined'){
        (function() {
            $.ajax({
                url : "listall/", 
                type: "GET",
                data:{ vendorid: vendorid,
                    page_no: 1,
                    calltype:"vendor_pending"},
                dataType: 'json',               
                        // handle a successful response
                        // +'/purchase/receipt/detailview/'+this.id+
                success : function(jsondata) {
                    $("#payment_table .payment_data").remove();
                    $('.detaildiv').attr('hidden',false);
                    $('.register').attr('disabled',false);
                    $.each(jsondata['object'], function(){
                        date=this.date
                        date=date.split("-").reverse().join("-")
                        pending=parseFloat(this.total) - parseFloat(this.amount_paid)
                        $('#payment_table').append("<tr class='payment_data' align='center'>"+
                        "<td hidden='true'>"+this.id+"</td>"+
                        "<td>"+this.supplier_invoice+"</td>"+
                        "<td>"+date+"</td>"+
                        "<td>"+this.total+"</td>"+
                        "<td hidden='true'>"+this.amount_paid+"</td>"+
                        "<td>"+pending.toFixed(2)+"</td>"+
                        "<td><input type='checkbox'></td>"+
                        "<td><input type = 'number' class='form-control'></td>"+
                        "<td><input type = 'text' class='form-control'></td>"+
                        "</tr>");
                    });
                },
                        // handle a non-successful response
                error : function() {
                    swal("Oops..", "it seems no pending invoice exist.", "error");
                }
            });
        }());
    }
});


$('.vendor_opening_pay').change(function() {
    vendorid=parseInt($(".vendor_opening_pay").find(':selected').data('id'));
    if (vendorid != 'undefined'){
        (function() {
            $.ajax({
                url : "/purchase/vendor/opening-balance/",
                type: "GET",
                data:{ vendorid: vendorid,
                    page_no: 1, 
                    calltype:"vendor_opening_details"},
                dataType: 'json',               
                        // handle a successful response
                        // +'/purchase/receipt/detailview/'+this.id+
                success : function(jsondata) {
                    $('.opening_pay_register').attr('disabled',false);
                    $('.open_balance_pay').val(jsondata['opening_balance']);
                    $('.open_balance_paid_pay').val(jsondata['opening_balance_paid']);
                    $('.current_open_balance_pay').val('');
                    $('.current_open_balance_pay').val('');
                    $('.open_balance_pay_date').val('');
                    $('.open_balance_pay_chqeue').val('');
                },
                        // handle a non-successful response
                error : function() {
                    swal("Oops..", "Couldn't fetch data. Kindly try again later.", "error");
                }
            });
        }());
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

            $.each(jsondata, function(){
                $('#vendor_opening_pay_mode').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });


            $('#mode').selectpicker('refresh')
            $('#vendor_opening_pay_mode').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in retriving payment mode data.", "error");
        }
    });
}

$('.register').click(function(e) {
    var total_payment_check=0
    var count = 0
    $("#payment_table tr.payment_data").each(function() {
        var is_paid = $(this).find('td:nth-child(7) input').is(":checked");
        if (is_paid){
            var amount = parseFloat($(this).find('td:nth-child(8) input').val());
            total_payment_check+=amount
            count++
        }
    });
    swal({
        title: "Are you sure?",
        // text: "Are you sure you want to register payment details?",
        text: "<p>Are you sure you want to register payment details?</p><p>Total Payments to be recorded: <b>Rs."
                +total_payment_check+"</b></p><p> Total number of invoices against which payment is made: <b>"+count+"</b></p>",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add register payment details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data()},600)            
        }
    })
});
    
function new_data(){
    var items=[], total_payment=0, proceed=true;
    var bill_count=0;
    vendorid=$('.vendor').find(':selected').data('id');
    modeid=$('.mode').find(':selected').data('id');
    date=$('.date_payment').val();

    //we need to consider payment mode as well.
    
    if (vendorid == '' || vendorid =='undefined' || modeid == '' || modeid =='undefined'){
        proceed = false;
        error_messages_display("Please select a payment mode.", 2500);
    }
    $("#payment_table tr.payment_data").each(function() {
        var receipt_pk = $(this).find('td:nth-child(1)').html();
        var amount_pending=$(this).find('td:nth-child(6)').html();
        var is_paid = $(this).find('td:nth-child(7) input').is(":checked");
        if (is_paid){
            bill_count+=1;
            var amount = parseFloat($(this).find('td:nth-child(8) input').val());
            var cheque_rtgs_number = parseFloat($(this).find('td:nth-child(9) input').val());
            total_payment+=amount
            if (isNaN(amount) || amount<=0){
                proceed=false;
                error_messages_display("Amount must be a positive number.", 2500);
                $(this).closest('tr').addClass("has-error");    
            }
            else if (amount>Math.ceil(amount_pending)){
                proceed=false;
                error_messages_display("Amount must not be greater than amount pending.", 2500);
                $(this).closest('tr').addClass("has-error");    
            }
            else{
                $(this).closest('tr').removeClass("has-error");   
                var item = {
                    receipt_pk : receipt_pk,
                    amount: amount,
                    cheque_rtgs_number: cheque_rtgs_number,
                };
                items.push(item);
            }
        }
    });
    // console.log(items);
    
    if (isNaN(total_payment)){
        proceed=false;
    }
    if (bill_count <1 || total_payment == 0){
        proceed=false;
        error_messages_display("Select atleast one bill against which payment is made.", 2500);
    }

    if (proceed){
        (function() {
            $.ajax({
                url : "/purchase/receipt/paymentsave/" , 
                type: "POST",
                data:{vendorid: vendorid,
                    modeid:modeid,
                    date:date.split("/").reverse().join("-"),
                    total_payment: total_payment,
                    payment_details: JSON.stringify(items),
                    calltype: "new_payment_multiple",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Payment details registered.", "success");
                        setTimeout(location.reload(true),2500);
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
    // else{
        // swal("Oops...", "Please recheck your entry. There were some errors", "error");
    // }
}

$('.vendor_opening').change(function() {
    $('.update_opening').attr('disabled',false);    
});

$('.update_opening').click(function(e) {
    swal({
        title: "Are you sure?",
        // text: "Are you sure you want to register payment details?",
        text: "Are you sure you want to add opening balance? Note this cannot be redone later.",
        type: "warning",
        showCancelButton: true,
        // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update opening balance!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfimr_opening()},600)            
        }
    })
});

function reconfimr_opening() {
    swal({
        title: "Please reconfirm!",
        text: "Kindly reconfirm if you want to update opening balance. This cannot be redone.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update opening balance!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){opening_save()},600)            
        }
    })
};

function opening_save(){
    var proceed = true;
    vendorid=$('.vendor_opening').find(':selected').data('id');
    opening_balance = parseFloat($('.open_balance').val());
    if (isNaN(opening_balance)){
        proceed = false;
        error_messages_display("Opening Balance must be a number.", 2500)
    }

    if (proceed){
        (function() {
            $.ajax({
                url : "/purchase/vendor/opening-balance/" , 
                type: "POST",
                data:{vendorid: vendorid,
                    opening_balance:opening_balance,
                    calltype: "update_opening_balance",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                success : function(jsondata) {
                    if (jsondata.length == 0){
                        swal("Hooray", "Opening details updated.", "success");
                        setTimeout(location.reload(true),2500);
                    }
                    else{
                        swal("Hmm...", jsondata, "warning");   
                    }
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
    // else{
    //     swal("Oops...", "Please recheck your entry. There were some errors", "error");
    // }
}

$('.opening_pay_register').click(function(e) {
    swal({
        title: "Are you sure?",
        // text: "Are you sure you want to register payment details?",
        text: "Are you sure you want to register payment against opening balance? Note this cannot be redone later.",
        type: "warning",
        showCancelButton: true,
        // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, register payment!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){opening_payment_register()},600)            
        }
    })
});

// function reconfimr_opening_payment() {
//     swal({
//         title: "Please reconfirm!",
//         text: "Kindly reconfirm if you want to register payment against opening balance. This cannot be redone.",
//         type: "warning",
//         showCancelButton: true,
//         confirmButtonColor: "#DD6B55",
//         confirmButtonText: "Yes, register payment!",
//         closeOnConfirm: true,
//         closeOnCancel: true,
//         html: true,
//     }, function(isConfirm){
//         if (isConfirm){
//             setTimeout(function(){opening_payment_register()},600)        
//         }
//     })
// };

function opening_payment_register(){
    var proceed = true;
    vendorid=$('.vendor_opening_pay').find(':selected').data('id');
    modeid = $('.vendor_opening_pay_mode').find(':selected').data('id');

    opening_balance = parseFloat($('.open_balance_pay').val());
    opening_balance_paid = parseFloat($('.open_balance_paid_pay').val());
    
    if (isNaN(opening_balance_paid)){
        opening_balance_paid = 0;
    }
    
    current_balance_paid = parseFloat($('.current_open_balance_pay').val());
    date=$('.open_balance_pay_date').val();
    cheque_rtgs_number = parseFloat($('.open_balance_pay_chqeue').val());
    amount_due = (opening_balance - opening_balance_paid);
    if (isNaN(amount_due)){
        proceed = false;
        error_messages_display("No balance is due currently.", 2500)
    }
    if (isNaN(current_balance_paid)){
        proceed = false;
        error_messages_display("Current balance paid must be a number.", 2500) 
    }
    if (current_balance_paid > amount_due){
        proceed = false;
        error_messages_display("Current balance paid must not be more than amount due.", 2500) 
    }
    if (modeid == '' || modeid =='undefined' || modeid == undefined){
        proceed = false;
        error_messages_display("Please select a payment mode.", 2500)
    }

    if (isNaN(cheque_rtgs_number)){
        cheque_rtgs_number = "";
    }
    

    if (proceed){
        (function() {
            $.ajax({
                url : "/purchase/vendor/opening-balance/" , 
                type: "POST",
                data:{vendorid: vendorid,
                    amount_paid: current_balance_paid,
                    modeid: modeid,
                    date: date.split("/").reverse().join("-"),
                    cheque_rtgs_number: cheque_rtgs_number,
                    calltype: "opening_balance_payment",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                success : function(jsondata) {
                    if (jsondata.length == 0 || jQuery.isEmptyObject(jsondata)){
                        swal("Hooray", "Opening payment registered.", "success");
                        setTimeout(location.reload(true),2500);
                    }
                    else{
                        swal("Hmm...", jsondata, "warning");   
                    }
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

