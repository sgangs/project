$(function(){

var monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

var quarterNames=['Q4:Jan-Mar', 'Q1: Apr-Jun', 'Q2: Jul-Sep', 'Q3: Oct-Dec']

function draw_crossfilter(){

    var monthChart = dc.rowChart("#month-chart");
    var classChart = dc.rowChart("#class-chart");
    var quarterChart = dc.pieChart("#quarter-chart");
    //Maybe add a student chart. But that would be too clumsy
    // var collectionChart = dc.lineChart("#collection-move-chart");
    // var volumeChart = dc.barChart("#collection-volume-chart");  
    var dataTable = dc.dataTable("#table-graph");

    data.forEach(function (d){
        d.month = monthNames[(moment(d.date).month())]; // pre-calculate month for better performance
        d.quarter = quarterNames[moment(d.date).quarter()-1]; // pre-calculate quarter for better performance        
    });

    //data format should be: {student name/id, class name, amaount_paid, paid_on}
    var xdata=crossfilter(data);
    total=xdata.size()
    
    var dateDim = xdata.dimension(function (d) { return d.date; });
    var monthDim=xdata.dimension(function(d) {return d.month;});
    var quarterDim=xdata.dimension(function(d) {return d.quarter;});
    var classDim=xdata.dimension(function(d) {return d.class;});
    var studentDim=xdata.dimension(function(d) {return d.student;});
    
    dateGroup = dateDim.group().reduceSum(function(d) { return d.amount; });
    monthGroup = monthDim.group().reduceSum(function(d) { return d.amount; });
    quarterGroup = quarterDim.group().reduceSum(function(d) { return d.amount; });
    classGroup = classDim.group().reduceSum(function(d) { return d.amount; });
    studentGroup = studentDim.group().reduceSum(function(d) { return d.amount; });

    month_count=monthGroup.top(Infinity).length;
    class_count=classGroup.top(Infinity).length;
    
    function render_plots(){
        
        monthChart
                .height(month_count*80)
                // .width(300).height(200)
                .dimension(monthDim)
                .group(monthGroup)
                .renderTitle(true)
                .title(function (d) {
                  return (d.key+": Rs. "+d.value) ;
                })
                .xAxis().ticks(5);

        classChart
                .height(class_count*40)
                // .width(300).height(200)
                .dimension(classDim)
                .group(classGroup)
                .renderTitle(true)
                .title(function (d) {
                  return (d.key+": Rs. "+d.value) ;
                })
                .xAxis().ticks(5);

                
        quarterChart
                // .width(200).height(200)
                .dimension(quarterDim)
                .group(quarterGroup)
                .innerRadius(60)
                .renderLabel(true)
                .renderTitle(true)
                .title(function (d) {
                  return (d.key+": Rs. "+d.value) ;
                });

        // collectionChart /* dc.lineChart('#monthly-move-chart', 'chartGroup') */
        //         .renderArea(true)
        //         .width(990)
        //         .height(200)
        //         .transitionDuration(1000)
        //         // .margins({top: 30, right: 50, bottom: 25, left: 40})
        //         .dimension(dateDim)
        //         .mouseZoomable(true)
        //         .rangeChart(volumeChart)
        //         .x(d3.time.scale().domain([new Date(min), new Date(max)]))
        //         .round(d3.time.month.round)
        //         .xUnits(d3.time.months)
        //         .elasticY(true)
        //         .renderHorizontalGridLines(true)
        //          .group(dateGroup, 'Daily Collection')

        // volumeChart
        //         .width(990) /* dc.barChart('#monthly-volume-chart', 'chartGroup'); */
        //         .height(40)
        //         .margins({top: 0, right: 50, bottom: 20, left: 40})
        //         .dimension(dateDim)
        //         .group(dateGroup)
        //         .centerBar(true)
        //         .gap(1)
        //         .x(d3.time.scale().domain([new Date(min), new Date(max)]))
        //         .round(d3.time.month.round)
        //         .alwaysUseRounding(true)
        //         .xUnits(d3.time.months)
            

        // studentChart
        //         // .width(800).height(200)
        //         .dimension(studentDim)
        //         .group(studentAvgGroup, "Student wise score")
        //         .label(function (d) {
        //           return (d.key.split(' ')[1] +" "+d.key.split(' ')[2]) ;
        //         })
        //         .valueAccessor(function(p) { 
        //             //console.log("p.value.average: ", p.value.avg) //displays the avg fine
        //             return p.value.avg; 
        //         })
        //         .xAxis().ticks(20);
        //         // .xAxis(d3.scale.linear().domain([0, 100]));

        dataTable.width(800).height(800)
            .dimension(studentDim)
            .group(function(d) { return ""})
            .size(300)
            .columns([
                function(d) { return d.student.split(' ')[1] +" "+d.student.split(' ')[2]; },
                function(d) { return d.class;},
                function(d) { return d.amount;},
                function(d) { return (moment(d.date).format('DD-MMM-YYYY')); },
                function(d) { return d.fee_month;},
            ])
            .sortBy(function(d){ return d.paid_on+ " " + d.student; })
            // (optional) sort order, :default ascending
            .order(d3.ascending);


        dc.renderAll()
    };

    render_plots();


}; //End of crossfilter

draw_crossfilter();

});





