$(function(){

if (paid == null || paid == undefined || paid == "None"){
    paid=0
}
if (total == null || total == undefined || paid == "None"){
    total=0
}

console.log("Paid: "+paid)

var ctx=$("#salary-chart");
var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ["Total", "Collected"],
        datasets: [{
            label: '# of Votes',
            data: [total, paid],
            backgroundColor: [
                'rgba(0,255,0,0.2)',
                'rgba(75, 192, 192, 0.2)',
            ],
            borderColor: [
                'rgba(0,255,0,1)',
                'rgba(75, 192, 192, 1)',
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