$(function(){


// function apply_navbutton(jsondata, page_no){
//     $('.navbtn').remove()
//     for (i =jsondata['start']+1; i<=jsondata['end']; i++){
//         if (i==page_no){
//                     // $('.add_nav').append("<a href='#' class='btn nav_btn btn-sm btn-default' data=1 style='margin-right:0.2%'>"+i+"</a>")
//             $('.add_nav').append("<button title='Your Current Page' class='btn btn-sm navbtn btn-info' "+
//                 "value="+i+" style='margin-right:0.2%'>"+i+"</button>")
//         }
//         else{
//             $('.add_nav').append("<button title='Go to page no: "+i+"' class='btn btn-sm navbtn btn-default'"+
//                 " value="+i+" style='margin-right:0.2%'>"+i+"</button>")
//         }
//     }
// }


var end = moment();
var start = moment(end).subtract(60, 'days');
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
        "days": 90
    },
    'autoApply':true,
    'startDate' : start,
    'endDate' : end,
    },
    function(start, end, label) {
        dateChanged=true;
        startdate=start.format('YYYY-MM-DD');
        enddate=end.format('YYYY-MM-DD');
        // $('.details').attr('disabled', false);
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
            });
            $('#customer').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
        }
    });
}

$('.get_data').click(function(e){
    get_data(1);
});


function get_data(page_no) {
    customerid=$('.customer').find(':selected').data('id');
    
    // console.log(dateChanged)
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    } 
    // console.log(enddate);

    $.ajax({
        url : "data/", 
        type: "GET",
        data:{ start: startdate,
            end: enddate,
            customerid: customerid,
            page_no: page_no,
            // calltype:"apply_filter",
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#report_table .data").remove();
            var total_qty=0;
            var total_taxable=0;
            var total_amt=0;
            $.each(jsondata['object'], function(){
                total_qty+=parseFloat(this.quantities);
                total_taxable+=parseFloat(this.taxable_value);
                total_amt=parseFloat(this.total_amount);
                $('#report_table').append("<tr class='data' align='center'>"+
                "<td>"+this.product_name+"</td>"+
                "<td>"+parseFloat(this.quantities)+"</td>"+
                "<td>"+this.taxable_value+"</td>"+
                // "<td></td>"+
                "<td>"+this.total_amount+"</td>"+
                "</tr>");                
            })

            $('#report_table').append("<tr class='data' align='center'>"+
                "<td><b>Total</b></td>"+
                "<td><b>"+parseFloat(total_qty)+"</b></td>"+
                "<td><b>"+total_taxable.toFixed(2)+"</b></td>"+
                // "<td></td>"+
                "<td><b>"+total_amt.toFixed(2)+"</b></td>"+
                "</tr>");
            // apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales invoice exist.", "error");
        }
    });

}


});

