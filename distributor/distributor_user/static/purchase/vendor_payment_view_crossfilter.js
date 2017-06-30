$(function(){

//This variable will store the student list added via json

var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');

$('.date_range').daterangepicker({
    'showDropdowns': true,
    'locale': {
        format: 'DD/MM/YYYY',
    },
    "dateLimit": {
        "days": 90
    },
    'autoApply':true,
    // 'minDate': moment(start),
    // 'maxDate': moment(end)  
    // 'startDate' : start,
    // 'endDate' : end,
    },
    function(start, end, label) {
        startdate=start.format('YYYY-MM-DD');
        enddate=end.format('YYYY-MM-DD');
        $('.details').attr('disabled', false);
});

$( ".get_data" ).click(function() {
    // console.log("here");
    console.log(startdate);
    (function() {
        $.ajax({
            url : "data/", 
            type : "GET", 
            data : { start: startdate,
                end: enddate,
                calltype: 'purchase crossfilter',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                // console.log(jsondata);
                draw_crossfilter(jsondata);

            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "There were some errors. Please check the purchase data.", "error");
            }
        });
    }());
});


function draw_crossfilter(data){

    var vendorChart = dc.pieChart("#subject-chart");
    // var dateChart = dc.barChart("#class-chart");
    var productChart = dc.rowChart("#marks-chart");
    // var studentChart = dc.rowChart("#student-chart");
    // var dataTable = dc.dataTable("#table-graph");

    //data format should be: {student name/id, class name, final_score, subject name}
    //data format should be: {vendor_name, warehouse_address, line_total, supplier_invoice, date, product_sku}
    
    var xdata=crossfilter(data);
    total=xdata.size()

    console.log(data)
    console.log(total)
    
    var vendorDim=xdata.dimension(function(d) {return ""+d.purchase_receipt__vendor_name;});
    // var dateDim=xdata.dimension(function(d) {return d.purchase_receipt__date;});
    var productDim=xdata.dimension(function(d) {return d.product_sku;});
    // var marksDim = xdata.dimension(function(p) {
    //     if (p.marks <35){
    //         p.group = "0-35"
    //     }
    //     else if (p.marks >=35, p.marks<60){
    //         p.group = "35-60"
    //     }
    //     else if (p.marks >=60, p.marks<80){
    //         p.group = "60-80"
    //     }
    //     else{
    //         p.group = "80-100"
    //     }
    //     return p.group;
    // });

    // function reduceAdd(p, v) {
    //     ++p.count;
    //     p.total += v.marks;
    //     p.average = p.count ? p.total / p.count : 0;
    //     return p;
    // }
    // function reduceRemove(p, v) {
    //     --p.count;
    //     p.total -= v.marks;
    //     p.average = p.count ? p.total / p.count : 0;
    //     return p;
    // }
    // function reduceInitial() {
    //     return {count: 0, total: 0, average: 0};
    // }

        
    vendorSumGroup = vendorDim.group()
    // dateSumGroup = dateDim.group();
    productSumGroup = productDim.group();
    // marksGroup = marksDim.group();

    // subject_count=subjectAvgGroup.top(Infinity).length;
    product_count=productSumGroup.top(Infinity).length;
    
    // var reducer = reductio().avg(function(d) { return d.marks; });
    var reducer = reductio().sum(function(d) { return +d.line_total; });
    reducer(vendorSumGroup);
    // reducer(dateSumGroup);
    reducer(productSumGroup);

    console.log("data we got: ")
    
    // reductio().avg(function(d) { return +d.marks; })(subjectAvgGroup);
    // marksGroup = marksDim.groupAll()

    function render_plots(){
        $('.graphs').attr('hidden', false);
        vendorChart
                // .width(200).height(200)
                .dimension(vendorDim)
                .group(vendorSumGroup)
                .innerRadius(20)
                .renderLabel(true)
                .title(function (d) {
                    console.log(d)
                    return ("Vendor wise purchase " +d.key +": " + d.value.sum) ;
                });

        // classChart
        //         .height(class_count*100)
        //         // .width(300).height(200)
        //         .dimension(classDim)
        //         .group(classAvgGroup)
        //         .title(function (d) {
        //           return (d.key + " Average Marks: " + d.value.avg.toFixed(2)) ;
        //         })
        //         .valueAccessor(function(p) { 
        //             //console.log("p.value.average: ", p.value.avg) //displays the avg fine
        //             return p.value.avg; ;
        //         });

        productChart
                .height(product_count*100)
                // .width(300).height(200)
                .dimension(productDim)
                .group(productSumGroup)
                .valueAccessor(function(p) { 
                    //console.log("p.value.average: ", p.value.avg) //displays the avg fine
                    return p.value.sum; 
                })
                .title(function (d) {
                    return (d.key + " Total : " + d.value.sum) ;
                })
                .xAxis().ticks(5);


        // dataTable.width(800).height(800)
        //     .dimension(studentDim)
        //     .group(function(d) { return ""})
        //     .size(300)
        //     .columns([
        //         function(d) { return d.student_id.split(' ')[1] +" "+d.student_id.split(' ')[2]; },
        //         function(d) { return d.class;},
        //         function(d) { return d.subject;},
        //         function(d) { return d.marks; },
        //     ])
        //     .sortBy(function(d){ return d.class+ " " + d.student_id; })
        //     // (optional) sort order, :default ascending
        //     .order(d3.ascending);


        dc.renderAll()

    };

    render_plots();


} //End of crossfilter
});





