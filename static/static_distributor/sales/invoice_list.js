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
            all_invoices = true; unpaid_invoices = false; overdue_invoices=false;
            $('.all').hide();
            $('.unpaid').show();
            $('.overdue').show();
            $.each(jsondata, function(){
                var url='/sales/invoice/detailview/'+this.id+'/'
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

function navigation(){
    if (all_invoices == true){
        load_invoices
    }
    else if (unpaid_invoices == true){
        
    }
}

$('.unpaid').click(function(e) {
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"unpaid_invoices"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#receipt_table .data").remove();
            all_invoices = true; unpaid_invoices = false; overdue_invoices=false;
            $('.all').show();
            $('.unpaid').hide();
            $('.overdue').show();
            $.each(jsondata, function(){
                var url='/sales/invoice/detailview/'+this.id+'/'
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
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });

});


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
            console.log(jsondata);
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
        "days": 90
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
            });
            $('#customer').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
        }
    });
}

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
                    $('.detaildiv').attr('hidden',false);
                    $('.register').attr('disabled',false);
                    $.each(jsondata, function(){
                        pending=parseFloat(this.total) - parseFloat(this.amount_paid)
                        $('#payment_table').append("<tr class='payment_data' align='center'>"+
                        "<td hidden='true'>"+this.id+"</td>"+
                        "<td>"+this.invoice_id+"</td>"+
                        "<td>"+this.total+"</td>"+
                        "<td>"+this.amount_paid+"</td>"+
                        "<td>"+pending.toFixed(2)+"</td>"+
                        "<td><input type='checkbox'></td>"+
                        "<td><input type = 'number' class='form-control'></td>"+
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



$('.register').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to register payment details?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add register payment details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data()},600)            
        }
    })
});
    
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
            text: "Please tner the payment colletion date.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });   
    }
    $("#payment_table tr.payment_data").each(function() {
        var invoice_pk = $(this).find('td:nth-child(1)').html();
        var amount_pending=$(this).find('td:nth-child(5)').html();
        var is_paid = $(this).find('td:nth-child(6) input').is(":checked");
        console.log(is_paid);
        if (is_paid){
            bill_count+=1;
            var amount = parseFloat($(this).find('td:nth-child(7) input').val());
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
                };
                items.push(item);
            }
        }
    });
    // console.log(items);
    console.log(date);
    
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

