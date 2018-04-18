$(function(){

trn_type=["Closing Balance", "Purchase", "Sales", "Sales Return", "Other Inward", "Purchase Return", "Other Outward", "Transfer Outward", 
        "Transfer Inward", "Retail Sales", "Retail Sales Return"];

var manufacturer, warehouse, date, month, year;
var products = []
var day_list = []

// load_current_inventory()

function getDaysInMonth(month, year) {
     var date = new Date(year, month, 1);
     var days = [];
     while (date.getMonth() === month) {
        date.setDate(date.getDate() + 1);
        days.push(new Date(date).toISOString().slice(0,10));        
     }
     $("#product_movement #main_data").remove();
     $.each(days,function(){
            var rowRef = document.getElementById("product_header");
            var newCell   = rowRef.insertCell(-1);
            new_date = new Date(this).getDate()
            var newText  = document.createTextNode(new_date)
            newCell.appendChild(newText);
            newCell.id = 'main_data';

        });
     return days;
}


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
            $('#warehouse').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
        }
    });
}


load_manufacturer()

function load_manufacturer(){
    $.ajax({
        url : "/master/manufacbrand/manufacdata/",
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#manufacturer').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            $('#manufacturer').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch manufacturer.", "error");
        }
    });
}

$('.get_data').click(function (){
    manufacturer = $('.manufacturer').find(':selected').data('id');
    warehouse = $('.warehouse').find(':selected').data('id');
    date=$('.date').val()
    proceed = true;
    if ($.trim(warehouse).length == 0 || typeof(warehouse) == 'undefined' || typeof(warehouse) == undefined){
        swal("Ughh...", "Please select a warehouse", "error");
        proceed = false;
    }

    if ($.trim(manufacturer).length == 0 || typeof(manufacturer) == 'undefined' || typeof(manufacturer) == undefined){
        swal("Ughh...", "Please select a warehouse", "error");
        proceed = false;
    }

    if ($.trim(date).length == 0 || typeof(date) == 'undefined' || typeof(date) == undefined){
        swal("Ughh...", "Please select a month", "error");
        proceed = false;
    }


    month = date.split("-")[0];
    year = date.split("-")[1];

    if(proceed){
        load_products();
    }
});

function load_products(){
    manufacturer=$('.manufacturer').find(':selected').data('id');

    $.ajax({
        url : "product/", 
        type: "GET",
        data:{calltype: 'product-manufacturer',
                manufacturer: manufacturer},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            products = jsondata
            actual_month = parseInt(month) - 1;
            day_list = getDaysInMonth(actual_month,2018);
            // $.each(products, function(){

            create_table();
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch products. Kindly retry", "error");
        }
    });
}

function create_table(){
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{month: month,
            year: year,
            manufacturer: manufacturer,
            warehouse: warehouse},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#product_movement .data").remove();
            $.each(products, function(){
                var product_id = this.id
                var rowId = 'data_'+product_id
                $('#product_movement').append("<tr class='data' id='"+rowId+"' align='center'>"+
                    "<td hidden>"+product_id+"</td>"+
                    "<td><small>"+this.name+": "+this.sku+"</small></td>");
                $.each(day_list,function(){
                    search_key = product_id + "_" + this
                    var rowRef = document.getElementById(rowId);
                    var newCell   = rowRef.insertCell(-1);
                    newCell.id = search_key;
                    if (this_data = jsondata[search_key]){
                        quantity = this_data['sales_total']
                        if (quantity == null || quantity == 'null' || quantity == 'None' || quantity == ''){
                            quantity = 0;
                        }
                        if (quantity != 0){
                            var newText  = document.createTextNode(Math.round(quantity * 1000)/1000)
                        }
                        else{
                            var newText = document.createTextNode(" ");
                        }
                        newCell.appendChild(newText);
                    }
                    else{
                        var newText  = document.createTextNode(" ");
                        newCell.appendChild(newText);
                    }

                });
            });
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were errors in fetching data. Kindly retry.", "error");
        }
    });
    // day_list = getDaysInMonth(1,2018)
}


});