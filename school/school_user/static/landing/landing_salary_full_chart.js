$(function(){

if (paid == null || paid == undefined || paid == "None"){
    paid=0
}
if (total == null || total == undefined || paid == "None"){
    total=0
}

var ctx=$("#salary-chart");
var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ["Remaining", "Collected"],
        datasets: [{
            label: '# of Votes',
            data: [(total-paid), paid],
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