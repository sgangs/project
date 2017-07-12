$(function(){

trn_type=["Closing Balance", "Purchase", "Sales", "Sales Return", "Other Inward", "Purchase Return", "Other Outward", "Transfer Outward", 
        "Transfer Inward", "Retail Sales", "Retail Sales Return"];

// load_current_inventory()


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
// var start = moment(end).subtract(30, 'days');
// var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');

// $('.date_range').daterangepicker({
//     'showDropdowns': true,
//     'locale': {
//         format: 'DD/MM/YYYY',
//     },
//     "dateLimit": {
//         "days": 31
//     },
//     'autoApply':true,
//     // 'minDate': moment(start),
//     // 'maxDate': moment(end)  
//     'startDate' : start,
//     'endDate' : end,
//     },
//     function(start, end, label) {
//         startdate=start.format('YYYY-MM-DD');
//         enddate=end.format('YYYY-MM-DD');
// });


$('.get_data').click(function load_movement(){
    warehouse=$('.warehouse').find(':selected').data('id');
    product=$('.product_id').val()
    date=$('.date').val()
    // if(moment(startdate, 'DD-MM-YYYY',true).isValid()){
    //     startdate=startdate.split("-").reverse().join("-")
    //     console.log(startdate);
    // }
    // if(moment(enddate, 'DD-MM-YYYY',true).isValid()){
    //     enddate=enddate.split("-").reverse().join("-")
    // }
    var proceed = true;
    if ($.trim(warehouse).length == 0 || typeof(warehouse) == 'undefined' || $.trim(product).length == 0 || typeof(product) == 'undefined'){
        proceed=false;
    }
    if (proceed){
        $.ajax({
            url : "data/",
            type: "GET",
            data:{calltype: 'productid',
                product: product,
                warehouse: warehouse,
                date:date.split("/").reverse().join("-")},
            dataType: 'json',
                // handle a successful response
            success : function(jsondata) {
                $("#product_movement .data").remove();
                var count=0;
                var final_qty=0;
                var final_rate=0;
                $.each(jsondata, function(){
                    if (typeof(this.date) == 'undefined'){
                        $('#product_movement').append("<tr class='data' align='center'>"+
                        "<td hidden='true'></td>"+
                        "<td>"+trn_type[parseInt(this.transaction_type)]+"</td>"+
                        "<td></td>"+
                        "<td></td>"+
                        "<td>"+this.current_qty+"</td>"+
                        "<td>Rs."+this.current_val+"</td>"+
                        "</tr>");
                    }
                    else{
                        if (count == 0){
                            final_qty = this.current_qty;
                            final_rate = this.current_val;
                        }
                        count++;     
                        $('#product_movement').append("<tr class='data' align='center'>"+
                        "<td hidden='true'></td>"+
                        "<td>"+trn_type[parseInt(this.transaction_type)]+"</td>"+
                        "<td>"+this.date.split("-").reverse().join("-")+"</td>"+
                        "<td>"+this.quantity+"</td>"+
                        "<td>"+this.current_qty+"</td>"+
                        "<td>Rs."+this.current_val+"</td>"+
                        "</tr>");   
                    }
                })
                if (count >0){
                    $('#product_movement').prepend("<tr class='data' align='center'>"+
                        "<td hidden='true'></td>"+
                        "<td>Closing Balance</td>"+
                        "<td></td>"+
                        "<td></td>"+
                        "<td>"+final_qty+"</td>"+
                        "<td>Rs."+final_rate+"</td>"+
                        "</tr>");

                }
                console.log(final_qty);
            },
                // handle a non-successful response
            error : function() {
                swal("Oops...", "There was an error.", "error");
            }
        });
    }
});


});