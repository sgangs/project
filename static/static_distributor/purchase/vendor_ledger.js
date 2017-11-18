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
        "years": 1
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
            });
            $('#vendor').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No vendor data exist.", "error");
        }
    });
}

$('.get_data').click(function(e){
    get_data(1);
});


function get_data(page_no) {
    vendorid=$('.vendor').find(':selected').data('id');
    
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
            vendorid: vendorid,
            page_no: page_no,
            // calltype:"apply_filter",
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#report_table .data").remove();
            $.each(jsondata['object'], function(){
                date = this.journal__date.split("-").reverse().join("-")
                if (this.transaction_type == 1){
                    $('#report_table').append("<tr class='data' align='center'>"+
                    "<td class='text-center date'>"+date+"</td>"+
                    "<td class='text-center journal_trn' hidden>"+this.journal__trn_type+"</td>"+
                    "<td class='text-center remark'>"+this.journal__remarks+"</td>"+
                    "<td class='trn_type' align='left'>Debit</td>"+
                    "<td class='text-center debit'>"+this.value+"</td>"+
                    "<td class='text-center credit'></td>"+
                    "</tr>");
                }
                else{
                    $('#report_table').append("<tr class='data' align='center'>"+
                    "<td class='text-center date'>"+date+"</td>"+
                    "<td class='text-center journal_trn' hidden>"+this.journal__trn_type+"</td>"+
                    "<td class='text-center remark'>"+this.journal__remarks+"</td>"+
                    "<td class='trn_type' align='right'>Credit</td>"+
                    "<td class='text-center debit'></td>"+
                    "<td class='text-center credit'>"+this.value+"</td>"+
                    "</tr>");

                }
            })

            // $('#report_table').append("<tr class='data' align='center'>"+
            //     "<td><b>Total</b></td>"+
            //     "<td><b>"+parseFloat(total_qty)+"</b></td>"+
            //     "<td><b>"+total_taxable.toFixed(2)+"</b></td>"+
            //     // "<td></td>"+
            //     "<td><b>"+total_amt.toFixed(2)+"</b></td>"+
            //     "</tr>");
            // apply_navbutton(jsondata, page_no);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No purchase receipt exist.", "error");
        }
    });

}


});


