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
        fillColor             : "rgba(151,187,205,0.2)",
        strokeColor           : "rgba(151,187,205,1)",
        pointColor            : "rgba(151,187,205,1)",
        pointStrokeColor      : "#fff",
        pointHighlightFill    : "#fff",
        pointHighlightStroke  : "rgba(151,187,205,1)",
        borderColor           : "rgba(151,187,205,1)",
        // lineTension           : 0,
        pointBackgroundColor  : "rgba(151,187,205,1)",
        pointBorderColor      : "rgba(151,187,205,1)",
        data                  : data
    }],
};

var myLineChart = new Chart(ctx, {
    type: 'line',
    data: tempData,
    options: {
        // animation: {
        //     duration: 0, // general animation time
        // },
        hover: {
            animationDuration: 2500, // duration of animations when hovering an item
        },
        // responsiveAnimationDuration: 0, // animation duration after a resize
    }
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

var ctx2 = $("#income-expense");
var labels = [], data_income=[], data_expense=[];
// console.log(labels);
$.each(income_expense, function() {
    labels.push(this.month);
    data_income.push(parseFloat(this.income));
    data_expense.push(parseFloat(this.expense));
});
labels.reverse();
data_income.reverse();
data_expense.reverse();

var incexpBarChart = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: "Income",
            backgroundColor: 'rgb(66, 244, 122)',
            borderColor: 'rgb(66, 244, 122)',
            hoverBackgroundColor: 'rgb(66, 211, 122)',
            hoverBorderColor: 'rgb(66, 211, 122)',
            data: data_income,
            // data: [450000, 652840, 478988,478745]
        },
        {
            label: "Expense",
            backgroundColor: 'rgb(245, 32, 2)',
            borderColor: 'rgb(245, 32, 2)',
            hoverBackgroundColor: 'rgb(215, 32, 2)',
            hoverBorderColor: 'rgb(215, 32, 2)',
            data: data_expense,
            // data: [350000, 512240, 358860,367855]
        }
        ],
    },
    options: {
        responsive: true,

        scales: {
            xAxes: [{
                barPercentage: 0.6,
            }],
            // yAxes: [{
                    // stacked: true
            // }]
            yAxes: [{
                ticks: {
                    beginAtZero:true
                },
                barPercentage: 0.6,
            }]
        },
    },
        // datasets: []
});

});





