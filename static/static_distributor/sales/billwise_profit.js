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
    date_update();
    dateChanged=false;
    load_receipts(1);
});

var end = moment();
var start = moment(end).subtract(15, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
date_update();


function date_update(){
startdate=start.format('DD-MM-YYYY');
enddate=end.format('DD-MM-YYYY');

$('.date_range').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD-MM-YYYY',
    },
    "dateLimit": {
        "days": 15
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

function fill_profit_table(jsondata){

    $("#profit_table .data").remove();
    var total_sales = 0;
    var total_purchase = 0;
    var total_profit = 0;
    var total_sales_tax = 0;
            
    $.each(jsondata['object'], function(){
                
        invoice_date=this.date;
        invoice_date=invoice_date.split("-").reverse().join("-");

        profit = parseFloat(this.subtotal) - parseFloat(this.purchase);
        profit_percent = (profit/parseFloat(this.subtotal))*100
                
        total_sales+= parseFloat(this.subtotal);
        total_purchase+= parseFloat(this.purchase);
        total_profit+= profit;
        total_sales_tax+= parseFloat(this.total);
                
        $('#profit_table').append("<tr class='data' align='center'>"+
            "<td hidden='true'></td>"+
            "<td>"+this.invoice_id+"</td>"+
            "<td>"+invoice_date+"</td>"+
            "<td>"+this.customer_name+"</td>"+
            "<td>"+this.subtotal+"</td>"+
            "<td>"+parseFloat(this.purchase).toFixed(2)+"</td>"+
            "<td>"+profit.toFixed(2)+"</td>"+
            "<td>"+profit_percent.toFixed(2)+"%</td>"+
            "<td>"+this.total+"</td>"+
            "</tr>");
    })
    var total_profit_percent = total_profit/total_sales*100;
    $('#profit_table').append("<tr class='data' align='center'>"+
        "<td hidden='true'></td>"+
        "<td colspan='3'><b>TOTAL</b></td>"+
        "<td><b>"+total_sales.toFixed(2)+"</b></td>"+
        "<td><b>"+total_purchase.toFixed(2)+"</b></td>"+
        "<td><b>"+total_profit.toFixed(2)+"</b></td>"+
        "<td><b>"+total_profit_percent.toFixed(2)+"%</b></td>"+
        "<td><b>"+total_sales_tax.toFixed(2)+"</b></td>"+
        "</tr>");

}



load_receipts(1);

function load_receipts(page_no){
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }
    $.ajax({
        url : "data/", 
        type: "GET",
        // data:{ calltype:"all_receipt"},
        data:{ page_no: page_no,
            start: startdate,
            end: enddate,},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            fill_profit_table(jsondata)


            // apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No invoice exist. Please retry.", "error");
        }
    });
}

// load_customer()

// function load_customer(){
//     $.ajax({
//         url : "/master/customer/getdata/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             $.each(jsondata, function(){
//                 $('#customer').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//                 $('#customer_filter').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//             });
//             $('#customer_filter').selectpicker('refresh');
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No customer data exist.", "error");
//         }
//     });
// }


$('.apply_filter').click(function(e){
    filter_data(1);
});


function filter_data(page_no) {
    // var customers=[];
    // $.each($(".customer_filter option:selected"), function(){
    //     customerid=$(this).data('id');
    //     // if (customerid == 'undefined' || typeof(customerid) == undefined){
    //     if ($.trim(customerid).length>0){
    //         var customer={
    //             customerid: customerid
    //         };
    //         customers.push(customer);
    //     }        
    // });
    
    // invoice_no=$('.invoice_no').val();
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(invoice_no);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ calltype:"apply_filter",
            start: startdate,
            end: enddate,
            // productid: productid,
            // invoice_no: invoice_no,
            // customers: JSON.stringify(customers),
            // page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('#filter').modal('hide');
            filter_applied=true;
            
            fill_profit_table(jsondata)
            // apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No invoice exist. Please retry.", "error");
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



});

