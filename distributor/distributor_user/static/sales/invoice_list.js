$(function(){

var total_payment=0, page_no=0, all_invoices = true,
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
    $('.invoice_summary').hide();
    $('.product_name').val('');
    $('.product_id').val('');
    $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_invoices(1);
});

// function speak_text(meassage){
//     const artyom = new Artyom();
//     function startOneCommandArtyom(){
//         artyom.fatality();// use this to stop any of

//         setTimeout(function(){// if you use artyom.fatality , wait 250 ms to initialize again.
//             artyom.initialize({
//                 lang:"en-GB",// A lot of languages are supported. Read the docs !
//                 continuous:false,// recognize 1 command and stop listening !
//                 listen:false, // Start recognizing
//                 debug:false, // Show everything in the console
//                 speed:1 // talk normally
//             }).then(function(){
//                 console.log("Ready to work !");
//             });
//         },250);
//     }
    
//     artyom.say(meassage,{
//         onStart:function(){
//             // console.log("The text is being readed");
//         },
//         onEnd:function(){
//             // console.log("Well, that was all. Try with a longer text !");
//         }
//     });
// }

// function create_speech_msg(meassage){
//     var msg = new SpeechSynthesisUtterance(message);
//     var voices = window.speechSynthesis.getVoices();
//     msg.voice = voices[7];
//     msg.rate = 0.8;
//     return msg;
// }


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
                // "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td><a href="+url+" class='new_link'>"+this.invoice_id+"</a></td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.payable_by)+"</td>"+
                "<td>"+this.customer_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
                "<td>"+this.return_value+"</td>"+
                "<td><a href='"+download_url+"'><button class='btn btn-primary btn-xs new'><i class='fa fa-download'>"+
                        "</i> Download Excel Format</button></a></td>"+
                "</tr>");

                // $('.receipt_table').find('tr:eq('+count+')').find('.new_link').href = url;
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
                // "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td><a href="+url+" class='new_link'>"+this.invoice_id+"</a></td>"+
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


/*$("#receipt_table").on("click", ".link", function(){
    // console.log('here');
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    console.log(get_url)
    location.href = get_url;
});*/

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
            "days": 366
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
                $('#customerfinalize').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#customer').selectpicker('refresh');
            $('#customer_filter').selectpicker('refresh');
            $('#customerfinalize').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
        }
    });
}

load_group()

function load_group(){
    $.ajax({
        url : "/master/productgroup/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#group_filter').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            $('#group_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product group exist.", "error");
        }
    });
}

load_manufacturer()

function load_manufacturer(){
    $.ajax({
        url : "/master/manufacbrand/manufacdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#manufacturer_filter').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            $('#manufacturer_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product manufacturer exist.", "error");
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

function encodeQueryData(data) {
   let ret = [];
   for (let d in data)
     ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
   return ret.join('&');
}


$('.download').click(function(e){
    
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

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

    var groups=[];
    $.each($(".group_filter option:selected"), function(){
        groupid=$(this).data('id');
        // if (customerid == 'undefined' || typeof(customerid) == undefined){
        if ($.trim(groupid).length>0){
            var group={
                groupid: groupid
            };
            groups.push(group);
        }        
    });

    payment_status=$(".payment_status").find(':selected').data('id');

    var data = { 'customers': JSON.stringify(customers), 'start': startdate, 'end': enddate, 'payment_status': payment_status, 
            groups: JSON.stringify(groups), 'calltype': 'apply_filter', 'returntype':'download' };
    var querystring = encodeQueryData(data);
    var download_url='/sales/invoicelist/listall/?'+querystring
    location.href = download_url;
    $('#filter').modal('hide');
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

    var groups=[];
    $.each($(".group_filter option:selected"), function(){
        groupid=$(this).data('id');
        // if (customerid == 'undefined' || typeof(customerid) == undefined){
        if ($.trim(groupid).length>0){
            var group={
                groupid: groupid
            };
            groups.push(group);
        }        
    });

    // var manufacturers=[];
    // $.each($(".manufacturer_filter option:selected"), function(){
    //     manufacturerid=$(this).data('id');
    //     // if (customerid == 'undefined' || typeof(customerid) == undefined){
    //     if ($.trim(manufacturerid).length>0){
    //         var manufacturer={
    //             manufacturerid: manufacturerid
    //         };
    //         manufacturers.push(manufacturer);
    //     }        
    // });

    manufacturer =$(".manufacturer_filter").find(':selected').data('id');


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
    invoice_status=$(".invoice_status").find(':selected').data('id');
    payment_status=$(".payment_status").find(':selected').data('id');
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            sent_with: sent_with,
            start: startdate,
            end: enddate,
            productid: productid,
            invoice_no: invoice_no,
            invoice_status: invoice_status,
            payment_status: payment_status,
            groups: JSON.stringify(groups),
            customers: JSON.stringify(customers),
            manufacturer: manufacturer,
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
                // "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td><a href="+url+" class='new_link'>"+this.invoice_id+"</a></td>"+
                "<td>"+date+"</td>"+
                "<td>"+$.trim(this.payable_by)+"</td>"+
                "<td>"+this.customer_name+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
                "<td>"+this.return_value+"</td>"+
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
    // Hide fields related to finalization of previous pay and delete related items
    $('.payfinaldiv').attr('hidden',true);
    $("#payment_finalize_table .payment_data").remove();
    
    // Unhide first time paymernt fields and disable buttons
    $('.current_pay').attr('hidden',false);
    $('.register_enable').attr('disabled',true);
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
                        $('.register_enable').attr('disabled',false);
                        $('.payfinaldiv').attr('hidden',true);

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

$('.open_pay_list').click(function(e) {
    customerid=parseInt($(".customer").find(':selected').data('id'));
    $("#payment_table .payment_data").remove();
    if (customerid != 'undefined'){
        (function() {
            $.ajax({
                url : "/sales/collectionlist/", 
                type: "GET",
                data:{ customerid: customerid,
                    calltype:"customer_open"},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                    $("#payment_finalize_table .payment_data").remove();
                    // Hide fields related to first time payment
                    $('.detaildiv').attr('hidden',true);
                    $('.current_pay').attr('hidden',true);
                    
                    if (jsondata.object.length>0){                    
                        $('.payfinaldiv').attr('hidden',false);    
                        $.each(jsondata.object, function(){
                            count=$('#payment_finalize_table tr').length;
                            pending=parseFloat(this.sales_invoice.total) - parseFloat(this.sales_invoice.amount_paid)
                            $('#payment_finalize_table').append("<tr class='payment_data' align='center'>"+
                            "<td hidden='true'>"+this.id+"</td>"+
                            "<td hidden='true'>"+this.sales_invoice.id+"</td>"+
                            "<td>"+this.sales_invoice.invoice_id+"</td>"+
                            "<td>"+this.sales_invoice.total+"</td>"+
                            // "<td>"+this.amount_paid+"</td>"+
                            "<td>"+pending.toFixed(2)+"</td>"+
                            "<td>"+this.payment_mode_name+"</td>"+
                            "<td><input class='form-control this_payment_date'></td>"+
                            "<td><input type='checkbox'></td>"+
                            "<td><input type = 'number' class='form-control update_payment_value' value="+this.amount_received+"></td>"+
                            "<td><input type = 'text' class='form-control cheque_rtgs' value="+this.cheque_rtgs_number+"></td>"+
                            "<td hidden>"+this.amount_received+"</td>"+
                            "<td hidden>"+pending.toFixed(2)+"</td>"+
                            "</tr>");

                            $('.this_payment_date').datepicker({
                                autoclose: true,
                                // endDate: moment(),
                                // endDate: '0d',
                                todayHighlight: true,
                                format: 'dd/mm/yyyy',    
                            });
                            $(".this_payment_date").datepicker("setDate", new Date(this.paid_on));
                            $(this).find('td:nth-child(7) input').removeClass("this_payment_date")
                        });

                    }
                    else{
                        swal({
                          title: "Hmmm..",
                          text: "No open payment found against this customer.",
                          type: "info",
                          timer: 3000
                       });
                    }
                },
                        // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some error in getting payment data.", "error");
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
    // speak_text("Are you sure you want to finalize payment details? Total Payments to be recorded is Rupees"
    //             +total_payment_check+" and total number of invoices against which payment is made is "+count)
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to finalize payment details? Total Payments to be recorded is Rupees"
    //             +total_payment_check+" and total number of invoices against which payment is made is "+count);
    // var voices = window.speechSynthesis.getVoices();
    // // console.log(voices);
    // msg.voice = voices[52];
    // window.speechSynthesis.speak(msg);
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to finalize payment details?</p><p>Total Payments to be recorded: <b>Rs."
                +total_payment_check+"</b></p><p> Total number of invoices against which payment is made: <b>"+count+"</b></p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, finalize payment details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data('final')},600)            
        }
    })
});

$('.generate_payment').click(function(e) {
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
    // speak_text("Are you sure you want to generate payment for future clerance? Total Payments to be recorded is Rupees"
    //             +total_payment_check+" and total number of invoices against which payment is made is "+count)
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to generate payment for future clerance? Total Payments to be recorded is Rupees"
    //             +total_payment_check+" and total number of invoices against which payment is made is "+count);
    // window.speechSynthesis.speak(msg);
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to generate payment for future clerance?</p><p>Total Payments to be recorded: <b>Rs."
                +total_payment_check+"</b></p><p> Total number of invoices against which payment is made: <b>"+count+"</b></p>",
        type: "info",
        showCancelButton: true,
        confirmButtonColor: "#428bca",
        confirmButtonText: "Yes, generate payment for future clearance!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data('not_final')},600)            
        }
    })
});

// function reconfirm(){

// }
    
function new_data(payment_type){
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
                    payment_type: payment_type,
                    payment_details: JSON.stringify(items),
                    calltype: "first_time",
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

$("#payment_finalize_table").on("blur", ".update_payment_value", function(){
    update_pending()
});

function update_pending(){
    for (var a = document.querySelectorAll('table.payment_finalize_table tbody tr'), i = 0; a[i]; ++i) {
        var original_amount_pending = parseFloat($(a[i]).find('td:nth-child(12)').html());
        var original_amount = parseFloat($(a[i]).find('td:nth-child(11)').html());
        var amount_pending = original_amount_pending + original_amount
        var current_payment = parseFloat($(a[i]).find('td:nth-child(9) input').val());
        var revised_pending = amount_pending - current_payment; 
        $(a[i]).find('td:nth-child(5) ').html(revised_pending.toFixed(2))
        
    }
    
};

$('.finalize_pay').click(function(e) {
    var total_payment_check=0
    var count = 0
    $("#payment_finalize_table tr.payment_data").each(function() {
        var is_update = $(this).find('td:nth-child(8) input').is(":checked");
        if (is_update){
            var amount = parseFloat($(this).find('td:nth-child(9) input').val());
            total_payment_check+=amount
            count++
        }
    });
    // speak_text("Are you sure you want to finalize payment details? Total Payments to be recorded is Rupees"
    //             +total_payment_check+" and total number of payments being finalized is"+count)
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to finalize payment details? Total Payments to be recorded is Rupees"
    //             +total_payment_check+" and total number of payments being finalized is"+count);
    // window.speechSynthesis.speak(msg);
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to finalize payment details?</p><p>Total Payments to be recorded: <b>Rs."
                +total_payment_check+"</b></p><p> Total number of payments being finalized: <b>"+count+"</b></p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, finalize payment details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){update_payment('finalize')},600)            
        }
    })
});


$('.delete_pay').click(function(e) {
    var total_payment_check=0
    var count = 0
    $("#payment_finalize_table tr.payment_data").each(function() {
        var is_update = $(this).find('td:nth-child(8) input').is(":checked");
        if (is_update){
            var amount = parseFloat($(this).find('td:nth-child(9) input').val());
            total_payment_check+=amount
            count++
        }
    });
    // speak_text("Are you sure you want to delete payment details? Total Payments to be deleted is Rupees"
    //             +total_payment_check+" and total number of payments being deleted is"+count)
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to delete payment details? Total Payments to be deleted is Rupees"
    //             +total_payment_check+" and total number of payments being deleted is"+count);
    // window.speechSynthesis.speak(msg);
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to delete payment details?</p><p>Total Payments to be deleted: <b>Rs."
                +total_payment_check+"</b></p><p> Total number of payments being deleted: <b>"+count+"</b></p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#f0ad4e",
        confirmButtonText: "Yes, delete payment details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){update_payment('delete')},600)            
        }
    })
});


function update_payment(payment_type){
    var items=[];
    var total_payment=0;
    var bill_count=0;
    var proceed=true;
    customerid=$('.customer').find(':selected').data('id');
    //we need to consider payment mode as well.
    
    if (customerid == '' || customerid =='undefined'){
        proceed = false;
        swal({
            title: "Oops..",
            text: "Please select a customer.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });
    }

    $("#payment_finalize_table tr.payment_data").each(function() {
        var date;
        var this_proceed = true;
        var payment_pk = $(this).find('td:nth-child(1)').html();
        var invoice_pk = $(this).find('td:nth-child(2)').html();
        var original_amount_pending = parseFloat($(this).find('td:nth-child(12)').html());
        var original_amount = parseFloat($(this).find('td:nth-child(11)').html());
        var amount_pending = original_amount_pending + original_amount
        date = $(this).find('td:nth-child(7) input').val();
        var is_finalize = $(this).find('td:nth-child(8) input').is(":checked");
        if (is_finalize){
            bill_count+=1;
            var amount = parseFloat($(this).find('td:nth-child(9) input').val());
            var cheque_rtgs_number = $(this).find('td:nth-child(10) input').val()
            total_payment+=amount
            
            if (date == '' || date =='undefined'){
                this_proceed = false;
                proceed = false;
                $(this).closest('tr').addClass("has-error");
                swal({
                    title: "Oops..",
                    text: "Please enter the payment collection date.",
                    type: "error",
                    allowOutsideClick: true,
                    timer:2500,
                });   
            }

            if (isNaN(amount) || amount<=0){
                this_proceed = false;
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
                this_proceed = false;
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
            if (this_proceed){
                $(this).closest('tr').removeClass("has-error");   
                var item = {
                    payment_pk : payment_pk,
                    invoice_pk : invoice_pk,
                    payment_date : date.split("/").reverse().join("-"),
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
            text: "Select atleast one bill against which payment is made. Additionally total payment must not be zero.",
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
                    total_payment: total_payment,
                    payment_type: payment_type,
                    payment_details: JSON.stringify(items),
                    calltype: "update_payment",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Payment details updated.", "success");
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

$('.customerfinalize').change(function() {
    customerid=parseInt($(".customerfinalize").find(':selected').data('id'));
    if (customerid != 'undefined'){
        (function() {
            $.ajax({
                url : "/sales/invoice/openinvoice/listall/",
                type: "GET",
                data:{ customerid: customerid,
                    calltype:"customer_finalize"},
                dataType: 'json',               
                        // handle a successful response
                success : function(jsondata) {
                    $("#finalize_table .finalize_data").remove();
                    if (jsondata.object.length>0){
                    
                        $('.detaildiv').attr('hidden',false);
                        $('.register').attr('disabled',false);
                        $.each(jsondata.object, function(){
                            $('#finalize_table').append("<tr class='finalize_data' align='center'>"+
                            "<td hidden='true'>"+this.id+"</td>"+
                            "<td>"+this.invoice_id+"</td>"+
                            "<td>"+this.date+"</td>"+
                            "<td>"+this.total+"</td>"+
                            // "<td>"+this.amount_paid+"</td>"+
                            "<td><input type='checkbox'></td>"+
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

$('.finalizebtn').click(function(){
    // post_data("Finalize");
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to finalize and save the invoice?"+
    //     " Note that you cannot edit this invoice once finalized.");
    // window.speechSynthesis.speak(msg);
    // speak_text("Are you sure you want to finalize and save the invoice? Note that you cannot edit this invoice once finalized.");
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to finalize and save the invoice?</p><p>Note that you cannot edit this invoice once finalized.</p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#9933CC",
        confirmButtonText: "Yes, finalize invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm_status("Finalize")},600)     
            // setTimeout(function(){post_data("Finalize")},600)    
        }
    })    
});

$('.deletebtn').click(function(){
    // post_data("Delete");
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to delete the invoice? Note that you cannot edit or view this invoice once deleted. "+
    //     "No record of this invoice shall exist.");
    // window.speechSynthesis.speak(msg);
    // speak_text("Are you sure you want to delete the invoice? Note that you cannot edit or view this invoice once deleted. "+
    //     "No record of this invoice shall exist.");
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to delete the invoice?</p><p>Note that you cannot edit or view this invoice once deleted. "+
                "No record of this invoice shall exist. </p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#CC0000",
        confirmButtonText: "Yes, delete invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm_status("Delete")},600)
            // setTimeout(function(){post_data("Delete")},600)            
        }
    })
});

$('.cancelbtn').click(function(){
    // post_data("Delete");
    // speak_text("Are you sure you want to cancel the invoice? Note that you cannot edit this invoice once cancelled. "+
    //     "You can see the list of canceled invoices. ");
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to cancel the invoice? Note that you cannot edit this invoice once cancelled. "+
    //     "You can see the list of canceled invoices. ");
    // window.speechSynthesis.speak(msg);
    swal({
        title: "Are you sure?",
        text: "<p>Are you sure you want to cancel the invoice?</p><p>Note that you cannot edit this invoice once cancelled. "+
                "You can see the list of canceled invoices. </p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#FF8800",
        confirmButtonText: "Yes, cancel invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm_status("Cancel")},600)            
        }
    })
});

function reconfirm_status(calltype){
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
    items=[];
    $("tr.finalize_data").each(function() {
        var invoice_id = $(this).find('td:nth-child(1)').html();
        var is_selected = $(this).find('td:nth-child(5) input').is(":checked");
        if (is_selected){
            var item = {
                invoice_id : invoice_id,
            };
            items.push(item);
        }
    });
    if (items.length > 0){
        $.ajax({
            url : "/sales/invoice/openinvoice/save/", 
            type: "POST",
            data: {invoices_list: JSON.stringify(items),
                // calltype: "Finalize",
                calltype: calltype,
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                swal("Hooray...", "Invoice status updated and saved.", "success");
                setTimeout(location.reload(true),1000);
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "There were errors in saving data. Check if accounting period exist.", "error");
            }
        });
    }
    else{
        swal("Oops...", "Please select atleast one invoice.", "info");
    }
};


});

