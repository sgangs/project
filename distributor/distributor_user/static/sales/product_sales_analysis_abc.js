$(function(){

var warehouse = '';

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


$('.get_data').click(function (){
    warehouse = $('.warehouse').find(':selected').data('id');
    date=$('.date').val()
    proceed = true;
    if ($.trim(warehouse).length == 0 || typeof(warehouse) == 'undefined' || typeof(warehouse) == undefined){
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
    $.ajax({
        url : "/sales/analysis/abc/",
        type: "GET",
        data:{calltype: 'abc-analysis',
                month: month,
                year: year,
                warehouse: warehouse},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // console.log(jsondata)
            create_line_chart(jsondata);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not generate report. Kindly retry", "error");
        }
    });
}

function create_line_chart(chart_data){
    var a_count = parseFloat(chart_data['a_count']);
    var b_count = parseFloat(chart_data['b_count']);
    var c_count = parseFloat(chart_data['c_count']);


    var a_count_cum = a_count
    var a_total_cum = parseFloat(chart_data['a_total'])
    var b_count_cum = a_count + b_count
    var b_total_cum = parseFloat(chart_data['a_total']) + parseFloat(chart_data['b_total'])
    var c_count_cum = a_count + b_count + c_count
    var c_total_cum = parseFloat(chart_data['a_total']) + parseFloat(chart_data['b_total']) + parseFloat(chart_data['c_total'])

    // console.log(a_count_cum);
    // console.log(a_total_cum);
    var ctx=$("#abc-graph");
    // var myChart = new Chart(ctx, {
    //     type: 'line',
    //       data: {
    //         labels: [0, a_count, b_count, c_count],
    //         datasets: [{ 
    //             data: [0, a_total_cum, b_total_cum, c_total_cum],
    //             label: "Total No. of products in Category",
    //             borderColor: "#3e95cd",
    //             fill: false 
    //           }
    //         ]
    //       },
    //       options: {
    //         title: {
    //           display: true,
    //           text: 'ABC Analysis (% of Sales Value)'
    //         }
    //       }
    // });

    var myChart = new Chart(ctx, {
        type: 'scatter',
          data: {
            datasets: [{ 
                data: [{
                    x:0,
                    y:0
                },{
                    x:a_count_cum,
                    y:a_total_cum
                },{
                    x:b_count_cum,
                    y:b_total_cum
                },{
                    x:c_count_cum,
                    y:c_total_cum
                }],
                label: "Total No. of prods in Category",
                borderColor: "#3e95cd",
                fill: false 
              }
            ]
          },
          options: {
            title: {
              display: true,
              text: 'ABC Analysis (% of Sales Value)'
            }
          }
    });


}



});