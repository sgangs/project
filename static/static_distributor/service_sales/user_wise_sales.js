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
        "days": 30
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


load_users()

function load_users(){
    $.ajax({
        url : "/user/userlist/data/", 
        type: "GET",
        data:{calltype: "get_users"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#user').append($('<option>',{
                    'data-id': this.id,
                    'text': this.first_name + " "+ this.last_name
                }));
            });
            $('#user').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some errors.", "error");
        }
    });
}

$('.get_data').click(function(e){
    get_data(1);
});


function get_data(page_no) {
    userid = $('.user').find(':selected').data('id');
    
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
            userid: userid,
            page_no: page_no,
            calltype:"all_invoices",
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#report_table .data").remove();
            var total_qty=0;
            var total_taxable=0;
            var total_amt=0;
            // console.log(jsondata);
            $.each(jsondata['object'], function(){
                console.log(this)
                // total_qty+=parseFloat(this.quantities);
                // total_taxable+=parseFloat(this.taxable_value);
                // total_amt+=parseFloat(this.total_amount);
                $('#report_table').append("<tr class='data' align='center'>"+
                "<td>"+this.service_invoice__invoice_id+"</td>"+
                "<td>"+this.service_name+"</td>"+
                "<td>"+parseFloat(this.quantity)+"</td>"+
                "<td>"+this.line_before_tax+"</td>"+
                // "<td></td>"+
                "<td>"+this["user_details"][userid]+"</td>"+
                "</tr>");                
            })

            // $('#report_table').append("<tr class='data' align='center'>"+
            //     "<td><b>Total</b></td>"+
            //     "<td><b>"+parseFloat(total_qty)+"</b></td>"+
            //     "<td><b>"+total_taxable.toFixed(2)+"</b></td>"+
            //     // "<td></td>"+
            //     "<td><b>"+total_amt.toFixed(2)+"</b></td>"+
            //     "</tr>");
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No sales detail exist.", "error");
        }
    });

}


});

