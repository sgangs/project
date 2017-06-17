$(function(){

if (invoice_value == null || invoice_value == undefined || invoice_value == "None"){
    invoice_value=0
}
if (payment_value == null || payment_value == undefined || payment_value == "None"){
    payment_value=0
}

var ctx=$("#invoice-collection");
var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ["Total Invoiced", "Total Collected"],
        datasets: [{
            // label: '# of Votes',
            data: [invoice_value, payment_value],
            backgroundColor: [
                'rgba(162,125,255,0.5)',
                'rgba(0,179,167,0.5)',
            ],
            borderColor: [
                'rgba(162,125,255,1)',
                'rgba(0,179,167,1)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        // scales: {
        //     yAxes: [{
        //         ticks: {
        //             beginAtZero:true
        //         }
        //     }]
        // }
    }
});





});