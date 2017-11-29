$(function(){

var page_no=0, all_invoices = true, filter_applied=false;;

$('.apply_reset').click(function(){
    filter_applied=false;
    // $('select').val([]).selectpicker('refresh');
    $('.payment_summary').hide();
    $('.invoice_no').val('');
    date_update();
    dateChanged=false;
    load_invoices(1);
});


load_invoices()

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

// $('.all').click(function(){
//     load_invoices();
//     page_no+=1;
// });

function load_invoices(){
    $.ajax({
        url : "listall/", 
        type: "GET",
        data:{ calltype:"all_invoices"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.payment_summary').hide();
            $('#filter').modal('hide');
            all_invoices = true;
            $("#receipt_table .data").remove();
            
            $.each(jsondata['object'], function(){
                var url='/servicesales/invoice/productdetailview/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+this.cgsttotal+"</td>"+
                "<td>"+this.sgsttotal+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td class='salesperson'>View Salesperson Details</td>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td class='delete'>Click here to delete</td>"+
                "</tr>");
            })

            // apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });
}


load_payment()

function load_payment(){
    $.ajax({
        url : "/retailsales/paymentmode/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#payment_mode').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            $('#payment_mode').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in retriving payment mode data.", "error");
        }
    });
}

// Taking care of navigation

// function navigation(){
// }

$("#receipt_table").on("click", ".link", function(){
    // console.log('here');
    get_url=$(this).closest('tr').find('td:nth-child(1)').html();
    location.href = get_url;
});

$("#receipt_table").on("click", ".salesperson", function(){
    // console.log('here');
    get_id = $(this).closest('tr').find('td:nth-child(8)').html();
    var url = '/servicesales/invoice/servicedetailview/'+get_id+'/'
    location.href = url;
});

$("#receipt_table").on("click", ".delete", function(){
    get_id=$(this).closest('tr').find('td:nth-child(7)').html();
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to delete the invoice? Note that once deleted, it cannot be recovered",
        type: "warning",
        showCancelButton: true,
          // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
        }, function(isConfirm){
            if (isConfirm){
                setTimeout(function(){reconfirm(get_id)},600)            
            }
    })  
});

function reconfirm(invoice_pk){
    swal({
        title: "Please reconfirm?",
        text: "Are you sure you want to delete the invoice? Please reconfirm.",
        type: "warning",
        showCancelButton: true,
          confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
        }, function(isConfirm){
            if (isConfirm){
                setTimeout(function(){delete_invoice(invoice_pk)},600)            
            }
    })
}

function delete_invoice(invoice_pk){
    $.ajax({
        url : "/retailsales/invoice/delete/", 
        type: "GET",
        data: {invoice_id: invoice_pk,
            calltype: 'delete',
        },
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            swal("Hooray...", "Invoice is deleted.", "success");
            setTimeout(location.reload(true),1500);
            },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales data exist.", "error");
        }
    });
}


$(".add_nav").on("click", ".navbtn", function(){
    if (filter_applied){
        filter_data($(this).val())
    }
    else{
        load_invoices($(this).val())
    }
});


var end = moment();
var start = moment(end).subtract(15, 'days');
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
            "days": 31
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
    invoice_no=$('.invoice_no').val();
    payment_mode=$(".payment_mode").find(':selected').data('id');
    
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
            start: startdate,
            end: enddate,
            invoice_no: invoice_no,
            payment_mode: payment_mode,
            // page_no: page_no,
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.payment_summary').show();
            filter_applied=true;
            $("#receipt_table .data").remove();
            $('#filter').modal('hide');
            $.each(jsondata['object'], function(){
                var url='/retailsales/invoice/detailview/'+this.id+'/'
                date=this.date
                date=date.split("-").reverse().join("-")
                $('#receipt_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+url+"</td>"+
                "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.invoice_id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+this.cgsttotal+"</td>"+
                "<td>"+this.sgsttotal+"</td>"+
                "<td>"+this.total+"</td>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td class='delete'>Click here to delete</td>"+
                "</tr>");
            })
            $("#summary_table .data").remove();
            $.each(jsondata['payment details'], function(){
                $('#summary_table').append("<tr class='data' align='center'>"+
                "<td>"+this.payment_mode_name+"</td>"+
                "<td>"+this.value+"</td>"+
                "</tr>");
            })
            // apply_navbutton(jsondata, page_no);
            // $('.amount_invoiced').html('Rs.'+jsondata['total_value'])
            // $('.amount_pending').html('Rs.'+jsondata['total_pending'])
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });

}


function encodeQueryData(data) {
   let ret = [];
   for (let d in data)
     ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
   return ret.join('&');
}


$('.download').click(function(e){
    // filter_data(1, 'download');
    // url='/sales/invoicelist/listall/'+get_id+'/'
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

    var data = { 'start': startdate, 'end': enddate, 'calltype': 'apply_filter', 'returntype':'download' };
    var querystring = encodeQueryData(data);
    var download_url='/sales/invoicelist/listall/?'+querystring
    location.href = download_url;
    $('#filter').modal('hide');
});


});

