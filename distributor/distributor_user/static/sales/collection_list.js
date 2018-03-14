$(function(){

var total_payment=0, page_no=0, filter_applied = false;


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

$('.apply_reset').click(function(){
    filter_applied=false;
    $('select').val([]).selectpicker('refresh');
    $('.customer_filter').val('');
    $('.invoice_no').val('');
    $('.cheque_rtgs').val('');
    date_update();
    dateChanged=false;
    load_receipts(1);
});


load_receipts(1);

function load_receipts(page_no){
    $.ajax({
        url : "/sales/collectionlist/", 
        type: "GET",
        // data:{ calltype:"all_receipt"},
        data:{ page_no: page_no},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#payment_table .data").remove();
            
            $.each(jsondata['object'], function(){
                
                rec_date=this.sales_invoice.date
                rec_date=rec_date.split("-").reverse().join("-")

                pay_date=this.paid_on
                pay_date=pay_date.split("-").reverse().join("-")
                
                $('#payment_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+this.sales_invoice.invoice_id+"</td>"+
                // "<td>"+this.purchase_receipt.supplier_invoice+"</td>"+
                "<td>"+rec_date+"</td>"+
                "<td>"+$.trim(this.sales_invoice.payable_by)+"</td>"+
                "<td>"+this.sales_invoice.customer_name+"</td>"+
                "<td>"+this.sales_invoice.total+"</td>"+
                "<td>"+this.sales_invoice.amount_paid+"</td>"+
                "<td>"+this.amount_received+"</td>"+
                "<td>"+pay_date+"</td>"+
                "<td>"+this.payment_mode_name+"</td>"+
                "<td>"+$.trim(this.cheque_rtgs_number)+"</td>"+
                "<td><input type='checkbox'></td>"+
                "</tr>");
            })
            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No payment data exist.", "error");
        }
    });
}

// $(".add_nav").on("click", ".navbtn", function(){
//     load_receipts($(this).val())
// });

var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();


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
            $('#customer_filter').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
        }
    });
}


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
    // else if(overdue_receipts){
    //     sent_with='overdue_receipts'
    // }
    invoice_no=$('.invoice_no').val();
    productid=$('.product_id').val();

    cheque_rtgs=$('.cheque_rtgs').val();
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    
    $.ajax({
        url : "/sales/collectionlist/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            start: startdate,
            end: enddate,
            productid: productid,
            invoice_no: invoice_no,
            cheque_rtgs: cheque_rtgs,
            customers: JSON.stringify(customers),
            page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#payment_table .data").remove();
            $('#filter').modal('hide');

            filter_applied=true;
            
            $.each(jsondata['object'], function(){
                
                rec_date=this.sales_invoice.date
                rec_date=rec_date.split("-").reverse().join("-")

                pay_date=this.paid_on
                pay_date=pay_date.split("-").reverse().join("-")
                
                $('#payment_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+this.sales_invoice.invoice_id+"</td>"+
                // "<td>"+this.purchase_receipt.supplier_invoice+"</td>"+
                "<td>"+rec_date+"</td>"+
                "<td>"+$.trim(this.sales_invoice.payable_by)+"</td>"+
                "<td>"+this.sales_invoice.customer_name+"</td>"+
                "<td>"+this.sales_invoice.total+"</td>"+
                "<td>"+this.sales_invoice.amount_paid+"</td>"+
                "<td>"+this.amount_received+"</td>"+
                "<td>"+pay_date+"</td>"+
                "<td>"+this.payment_mode_name+"</td>"+
                "<td>"+$.trim(this.cheque_rtgs_number)+"</td>"+
                "<td><input type='checkbox'></td>"+
                "</tr>");
            })
            apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No collection data exist.", "error");
        }
    });

}


$(".add_nav").on("click", ".navbtn", function(){
    if (filter_applied){
        filter_data($(this).val())
    }
    else{
        load_receipts($(this).val())
    }
});

$('.deletebtn').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to delete the collection details?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete collection details!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true,
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){delete_data()},600)            
        }
    })
});
    
function delete_data(){
    var items=[]
    var count = 0;
    $("#payment_table tr.data").each(function() {
        var payment_id = $(this).find('td:nth-child(1)').html();
        var is_selected = $(this).find('td:nth-child(12) input').is(":checked");
        if (is_selected){
            count+=1;
            var item = {
                payment_id : payment_id,
                };
            items.push(item);
            
        }
    });

    if (count>0){
        (function() {
            $.ajax({
                url : "/sales/invoice/paymentsave/" , 
                type: "POST",
                data:{payment_id_list: JSON.stringify(items),
                    calltype: "delete_payment",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Collection details deleted.", "success");
                        // setTimeout(location.reload(true),2500);
                        if (filter_applied){
                            filter_data(1)
                        }
                        else{
                            load_receipts(1)
                        }
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
    else{
        swal("Hmm...", "Please select atleast one entry to delete.", "info");
    }
}



});

