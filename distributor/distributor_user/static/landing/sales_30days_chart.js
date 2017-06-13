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

});





