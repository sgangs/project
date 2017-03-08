$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var classid=1;
var examid=1;


//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });

//This is called when subject is entered.
$( ".exam" ).change(function() {
    examid =parseInt($(".exam").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { examid: examid,
                // classid: classid,
                // subjectid: subjectid,
                calltype: 'subject',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                draw_crossfilter(jsondata);
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and exam combination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});


function draw_crossfilter(data){

    var subjectChart = dc.rowChart("#subject-chart");
    var classChart = dc.rowChart("#class-chart");
    var marksChart = dc.pieChart("#marks-chart");
    var studentChart = dc.rowChart("#student-chart");
    var dataTable = dc.dataTable("#table-graph");

    //data format should be: {student name/id, class name, final_score, subject name}
    var xdata=crossfilter(data);
    
    // var typeDimension = livingThings.dimension(function(d) { return d.type; });
    // var n = livingThings.groupAll().reduceCount().value();
    // console.log("There are " + n + " living things in my house.") // 6
    // var legMeasure = typeDimension.group().reduceSum(function(fact) { return fact.legs; });
    // var a = legMeasure.top(4);
    // console.log("There are " + a[0].value + " " + a[0].key + " legs in my house.");
    // console.log(“There are ” + a[1].value + “ ” + a[1].key + “ legs in my house.”);
    // console.log(“There are ” + a[2].value + “ ” + a[2].key + “ legs in my house.”);
    // console.log(“There are ” + a[3].value + “ ” + a[3].key + “ legs in my house.”);

    

    var subjectDim=xdata.dimension(function(d) {return ""+d.subject;});
    var classDim=xdata.dimension(function(d) {return d.class;});
    var studentDim=xdata.dimension(function(d) {return d.student_id;});
    var marksDim = xdata.dimension(function(p) {
        if (p.marks <35){
            p.group = "Less than 35"
        }
        else if (p.marks >=35, p.marks<60){
            p.group = "35-60"
        }
        else if (p.marks >=60, p.marks<80){
            p.group = "60-80"
        }
        else{
            p.group = "80-100"
        }
        return p.group;
    });

    function reduceAdd(p, v) {
        ++p.count;
        p.total += v.marks;
        p.average = p.count ? p.total / p.count : 0;
        return p;
    }
    function reduceRemove(p, v) {
        --p.count;
        p.total -= v.marks;
        p.average = p.count ? p.total / p.count : 0;
        return p;
    }
    function reduceInitial() {
        return {count: 0, total: 0, average: 0};
    }

        
    subjectAvgGroup = subjectDim.group()
    classAvgGroup = classDim.group();
    studentAvgGroup = studentDim.group();
    marksGroup = marksDim.group();
    
    var reducer = reductio().avg(function(d) { return d.marks; });
    reducer(subjectAvgGroup);
    reducer(classAvgGroup);
    reducer(studentAvgGroup);
    // reductio().avg(function(d) { return +d.marks; })(subjectAvgGroup);
    // marksGroup = marksDim.groupAll()

    function render_plots(){
        $('.graphs').attr('hidden', false);
        subjectChart
                // .width(300).height(200)
                .dimension(subjectDim)
                .group(subjectAvgGroup)
                .valueAccessor(function(p) { 
                    //console.log("p.value.average: ", p.value.avg) //displays the avg fine
                    return p.value.avg; 
                })
                .title(function (d) {
                  return (d.key + " Average Marks: " + d.value.avg.toFixed(2)) ;
                })
                .xAxis().ticks(5);

        classChart
                // .width(300).height(200)
                .dimension(classDim)
                .group(classAvgGroup)
                .title(function (d) {
                  return (d.key + " Average Marks: " + d.value.avg.toFixed(2)) ;
                })
                .valueAccessor(function(p) { 
                    //console.log("p.value.average: ", p.value.avg) //displays the avg fine
                    return p.value.avg; ;
                });

        marksChart
                // .width(200).height(200)
                .dimension(marksDim)
                .group(marksGroup)
                .innerRadius(20)
                .renderLabel(true)
                .title(function (d) {
                  return ("No. of students in range " +d.key +": " + d.value) ;
                });


        studentChart
                // .width(800).height(200)
                .dimension(studentDim)
                .group(studentAvgGroup, "Student wise score")
                .label(function (d) {
                  return (d.key.split(' ')[1] +" "+d.key.split(' ')[2]) ;
                })
                .title(function (d) {
                  return (d.key.split(' ')[1] +" "+d.key.split(' ')[2] + " Average Marks: " + d.value.avg.toFixed(2)) ;
                })
                .valueAccessor(function(p) { 
                    //console.log("p.value.average: ", p.value.avg) //displays the avg fine
                    return p.value.avg; 
                })
                .xAxis().ticks(20);
                // .xAxis(d3.scale.linear().domain([0, 100]));

        dataTable.width(800).height(800)
            .dimension(studentDim)
            .group(function(d) { return ""})
            .size(300)
            .columns([
                function(d) { return d.student_id.split(' ')[1] +" "+d.student_id.split(' ')[2]; },
                function(d) { return d.class;},
                function(d) { return d.subject;},
                function(d) { return d.marks; },
            ])
            .sortBy(function(d){ return d.class+ " " + d.student_id; })
            // (optional) sort order, :default ascending
            .order(d3.ascending);


        dc.renderAll()

        // marksChart.on ("renderlet", function(chart) {
        //     dc.events.trigger(function() {
        //         console.log(marksChart.filters());
        //     });
        // })
        
        // subjectChart.turnOnControls(true)
        // classChart.turnOnControls(true)
        // marksChart.turnOnControls(true)
        // studentChart.turnOnControls(true)

    };

    render_plots();


} //End of crossfilter
});





