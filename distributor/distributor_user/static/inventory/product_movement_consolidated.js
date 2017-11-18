$(function(){

load_warehouse()

function load_warehouse(){
    $.ajax({
        url : "/master/warehouse/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#warehouse').append($('<option>',{
                    'data-id': this.id,
                    'text': this.address_1 + " "+ this.address_2
                }));
            });
            $('#warehouse').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
        }
    });
}

var end = moment();
var start = moment(end).subtract(30, 'days');
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
            "months": 1
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

$('.get_data').click(function load_movement(){
    warehouse=$('.warehouse').find(':selected').data('id');
    console.log("I'm here");
    
    if (!dateChanged){
        startdate = startdate.split("-").reverse().join("-")
        enddate = enddate.split("-").reverse().join("-")
        dateChanged= true;
    }

    
    var proceed = true;
    if ($.trim(warehouse).length == 0 || typeof(warehouse) == 'undefined' ){
        proceed=false;
    }
    if (proceed){
        $.ajax({
            url : "data/",
            type: "GET",
            data:{calltype: 'consolidated',
                warehouse: warehouse,
                start: startdate,
                end: enddate,},
            dataType: 'json',
                // handle a successful response
            success : function(jsondata) {
                $("#product_movement .data").remove();
                console.log(jsondata);
                
                $.each(jsondata, function(){
                    if (this.purchase_total == null || this.purchase_total == "null"){
                        this.purchase_total = 0
                    }
                    if(this.sales_total == null || this.sales_total == "null"){
                        this.sales_total = 0;
                    }
                    $('#product_movement').append("<tr class='data' align='center'>"+
                    "<td>"+this.product__name+"</td>"+
                    "<td>"+this.purchase_total+"</td>"+
                    "<td>"+this.sales_total+"</td>"+
                    "</tr>");
                })
            },
                // handle a non-successful response
            error : function() {
                swal("Oops...", "There was an error.", "error");
            }
        });
    }
    else{
        swal("Ehh...", "Please select a warehouse.", "warning");
    }
});


});