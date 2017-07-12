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



$('.get_data').click(function(){
    load_invoices();
});

function load_invoices(){
    date=$('.date').val()
    warehouse=$('.warehouse').find(':selected').data('id');
    (function() {    
        $.ajax({
            url : "data/", 
            type: "GET",
            data:{ warehouse: warehouse,
                date: date.split("/").reverse().join("-"),
                calltype:"eod_report"},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                $("#report_table .data").remove();
                console.log(jsondata);
                $.each(jsondata, function(){
                    $('#report_table').append("<tr class='data' align='center'>"+
                    "<td>"+this.product__name+"</td>"+
                    "<td>"+$.trim(this.sold_quantity)+"</td>"+
                    "<td>"+$.trim(this.value_sold)+"</td>"+
                    "<td>"+$.trim(this.returned_quantity)+"</td>"+
                    "<td>"+$.trim(this.value_returned)+"</td>"+
                    "</tr>");
                })
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "No sales invoice exist.", "error");
            }
        });
    }());
}

// Taking care of navigation

// function navigation(){
// }

});

