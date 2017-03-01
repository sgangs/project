$(function(){


// //This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });

var start_date;
var end_date;
$('.date').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD/MM/YYYY',
    },
    'autoApply':true,
    'minDate': moment(min),
    'maxDate': moment(max)      
    },
    function(start, end, label) {
        startdate=start.format('YYYY-MM-DD');
        enddate=end.format('YYYY-MM-DD');
        $('.details').attr('disabled', false);
});
    
//This function gets called as year is entered.
$( ".details" ).click(function() {
    console.log(start_date);
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : {start: startdate,
                end: enddate,
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                $(".feeview .data").remove(); 
                $(".fee_heading").remove(); 
                $(".details").attr('hidden', false);
                $.each(jsondata, function(){
                    if (this.data=="Student"){
                        $('.feeview').append("<tr class='data'>"+
                        "<td>"+this.student_id+"</td>"+
                        "<td>"+this.student_local+"</td>"+
                        "<td>"+this.student_name+"</td>"+
                        "<td>"+this.date+"</td>"+
                        "<td>"+this.amount+"</td></tr>");
                    }
                    else if (this.data == 'Total'){
                        $('.feeview').append("<tr class='data'>"+
                        "<td colspan=4'><b>Total Amount Collected</b></td>"+
                        "<td><b>"+this.collected+"</b></td></tr>")
                        $('.fee_heading_outer').append("<label class='fee_heading'>Total Amount Collected in Date Range: " +
                            moment(startdate).format('DD-MM-YYYY')+" to "+moment(enddate).format('DD-MM-YYYY')+"</label>");
                    }
                })
            },
            // handle a non-successful response
            error : function() {
                $(".feeview .data").remove(); 
                $(".fee_heading").remove(); 
                $(".details").attr('hidden', false);
                swal("Oopss..","There were some errors!!","error");
            }
        });
    }());    
});

});