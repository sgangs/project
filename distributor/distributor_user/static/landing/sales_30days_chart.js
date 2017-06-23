$(function(){


var ctx = $("#sales");
var labels = [], data=[];
sales_daily=JSON.parse(sales_daily)
$.each(sales_daily, function() {
    labels.push(moment(new Date(this.date)).format('DD/MM/YYYY'));
    data.push(parseFloat(this.total));
});
var tempData = {
    labels : labels,
    datasets : [{
        label                : 'Total Sales',
        fill                 : false,
        // fillColor             : "rgba(151,187,205,0.2)",
        strokeColor           : "rgba(151,187,205,1)",
        pointColor            : "rgba(151,187,205,1)",
        pointStrokeColor      : "#fff",
        pointHighlightFill    : "#fff",
        pointHighlightStroke  : "rgba(151,187,205,1)",
        data                  : data
    }]
};
var myLineChart = new Chart(ctx, {
    type: 'line',
    data: tempData,
});


// var ctx_two = $("#retail");
// var labels = [], data=[];
// retail_sales_daily=JSON.parse(retail_sales_daily)
// $.each(retail_sales_daily, function() {
//     labels.push(moment(new Date(this.date)).format('DD/MM/YYYY'));
//     data.push(parseFloat(this.total));
// });
// var tempData_two = {
//     labels : labels,
//     datasets : [{
//         label                : 'Total Sales',
//         fill                 : false,
//         // fillColor             : "rgba(151,187,205,0.2)",
//         strokeColor           : "rgba(151,187,205,1)",
//         pointColor            : "rgba(151,187,205,1)",
//         pointStrokeColor      : "#fff",
//         pointHighlightFill    : "#fff",
//         pointHighlightStroke  : "rgba(151,187,205,1)",
//         data                  : data
//     }]
// };
// var myLineChart = new Chart(ctx_two, {
//     type: 'line',
//     data: tempData_two,
// });

});





