$(function(){


//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });

//This is called when subject is entered.
get_data();

function get_data() {
    // examid =parseInt($(".exam").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "data/", 
            type : "GET", 
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                draw_crossfilter(jsondata);
            },
            // handle a non-successful response
            // error : function() {
            //     bootbox.alert({
            //         message: "Class and exam combination doesn't exist.", 
            //         onEscape: true }); // provide a bit more info about the error to the user
            //     clearmodal();
            // }
        });
    }());
};


function draw_crossfilter(data){

    // var productChart = dc.pieChart("#product-chart");
    var customerChart = dc.rowChart("#customer-chart");
    var taxChart = dc.rowChart("#tax-chart");
    var productChart = dc.rowChart("#product-chart");
    // var studentChart = dc.rowChart("#student-chart");
    var dataTable = dc.dataTable("#table-graph");

    //data format should be: {student name/id, class name, final_score, subject name}
    var xdata=crossfilter(data);
    var all = xdata.groupAll();
    total=xdata.size()
    
    var productDim=xdata.dimension(function(d) {return ""+d.product_name;});
    var customerDim=xdata.dimension(function(d) {return d.customer_name;});
    var taxDim=xdata.dimension(function(d) {return d.cgst_percent;});
    
    var invoiceDim=xdata.dimension(function(d) {return d.invoice_no;});

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

        
    productAvgGroup = productDim.group()
    customerAvgGroup = customerDim.group();
    taxAvgGroup = taxDim.group();
    invoiceAvgGroup = invoiceDim.group();
    // marksGroup = marksDim.group();
    var itemCount = dc.dataCount('.dc-data-count');
    
    customer_count=customerAvgGroup.top(Infinity).length;
    tax_count=taxAvgGroup.top(Infinity).length;
    // console.log(extraAvgGroup.top(Infinity)[0])
    product_count=productAvgGroup.top(Infinity).length;
    
    
    var reducer = reductio().sum(function(d) { return parseFloat(d.line_total); });
    reducer(productAvgGroup);
    reducer(customerAvgGroup);
    reducer(taxAvgGroup);

    // reductio().avg(function(d) { return +d.marks; })(subjectAvgGroup);
    // marksGroup = marksDim.groupAll()

    function render_plots(){
        $('.graphs').attr('hidden', false);
        customerChart
                // .width(300)
                .height(customer_count*30)
                // .width(300).height(200)
                .dimension(customerDim)
                .group(customerAvgGroup)
                .valueAccessor(function(p) { 
                    return p.value.sum; 
                })
                .title(function (d) {
                  return (d.key + "'s Total Purchase: Rs." + d.value.sum.toFixed(2)) ;
                })
                .transitionDuration(1000)
                .xAxis().ticks(5);

        taxChart
                // .width(300)
                .height(tax_count*100)
                // .width(300).height(200)
                .dimension(taxDim)
                .group(taxAvgGroup)
                .label(function (d) {
                  return (d.key*2+"%") ;
                })
                // .title(function (d) {
                  // return (d.key + " Average Marks: " + d.value.avg.toFixed(2)) ;
                // })
                .valueAccessor(function(p) { 
                    //console.log("p.value.average: ", p.value.avg) //displays the avg fine
                    return p.value.sum; ;
                })
                .title(function (d) {
                  return ("Total Sales: Rs. "+d.value.sum.toFixed(2)) ;
                })
                .transitionDuration(1000)
                .xAxis().ticks(5);

        // productChart
        //         // .width(200).height(200)
        //         .dimension(productDim)
        //         .group(productAvgGroup)
        //         .innerRadius(20)
        //         .renderLabel(true)
        //         .title(function (p) {
        //             console.log(p)
        //           return ("Value of products sold: " +p.value.sum) ;
        //         });
        productChart
                // .width(300)
                .height(product_count*30)
                // .width(300).height(200)
                .dimension(productDim)
                .group(productAvgGroup)
                // .title(function (d) {
                  // return (d.key + " Average Marks: " + d.value.avg.toFixed(2)) ;
                // })
                .valueAccessor(function(p) { 
                    //console.log("p.value.average: ", p.value.avg) //displays the avg fine
                    return p.value.sum; ;
                })
                .title(function (d) {
                  return (d.key + "'s Total Sales : Rs." + d.value.sum.toFixed(2)) ;
                })
                .transitionDuration(1000)
                .xAxis().ticks(5);

        itemCount
                .dimension(xdata)
                .group(all)
                .html({
                    some: '<strong>%filter-count</strong> selected out of <strong>%total-count</strong> records' +
                        ' | <a href=\'javascript:dc.filterAll(); dc.renderAll();\'><b>Reset All</b></a>',
                    all: 'All records selected. Please click on the graph to apply filters.'
                });


        // studentChart
        //         .height(total/subject_count*25)
        //         // .width(800)
        //         .dimension(studentDim)
        //         .group(studentAvgGroup, "Student wise score")
        //         .label(function (d) {
        //           return (d.key.split(' ')[1] +" "+d.key.split(' ')[2]) ;
        //         })
        //         .title(function (d) {
        //           return (d.key.split(' ')[1] +" "+d.key.split(' ')[2] + " Average Marks: " + d.value.avg.toFixed(2)) ;
        //         })
        //         .valueAccessor(function(p) { 
        //             //console.log("p.value.average: ", p.value.avg) //displays the avg fine
        //             return p.value.avg; 
        //         })
        //         .xAxis().ticks(20);
        //         // .xAxis(d3.scale.linear().domain([0, 100]));

        dataTable.width(800).height(800)
            .dimension(invoiceDim)
            .group(function(d) { return ""})
            // .group(invoiceAvgGroup)
            .size(50)
            .columns([
                function(d) { return d.invoice_no; },
                function(d) { return d.customer_name;},
                function(d) { return d.product_name;},
                function(d) { return parseFloat(d.quantity).toFixed(3);},
                function(d) { return d.line_total;},
                // function(d) { return d.marks; },
            ])
            .sortBy(function(d){ return d.invoice_no; })
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





