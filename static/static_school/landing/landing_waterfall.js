$(function(){

  for (i in accounts){
    if (accounts[i].data_type=='income'){
      income=parseFloat(accounts[i].amount)
    }
    else if (accounts[i].data_type=='expense'){
      expense=parseFloat(accounts[i].amount)*(-1)
    }
    else if (accounts[i].data_type=='other_income'){
      other_income=parseFloat(accounts[i].amount)
    }
    else if (accounts[i].data_type=='other_expense'){
      other_expense=parseFloat(accounts[i].amount)*(-1)
    }
    else if (accounts[i].data_type=='profit'){
      profit=(parseFloat(accounts[i].amount))
    }
  }

// This code should support any data in this structure changing the data here
    // should be dealt with by the the code below.  The y axis min and max must
    // be able to contain the data required or the results will be incorrect.
    // Also the "bar" elements must have the correct value (sum of previous "bar"
    // + intervening "var" elements)
    var yMax = (Math.max((expense+other_expense)*(-1),income+other_income))+500,
        yMin =  yMax*(-1),
        xLabel = "Income & Expense",
        yLabel = "Amount";
        data = [
      { "label":"Direct Revenue", "value":income, "type":"var" },
      { "label":"Indirect Revenue", "value":other_income, "type":"var" },
      { "label":"Direct Expense", "value":expense, "type":"var" },
      { "label":"Indirect Expense", "value":other_expense, "type":"var" },
      { "label":"Profit", "value":profit, "type":"bar" },
      ];

    // Create the svg as usual
    var svg = dimple.newSvg("#waterfall", 600, 300);
    // The waterfall requires some data manipulation in a similar
    // way that one would create a waterfall in Excel.  The data
    // will be padded and rearranged for display
    var waterfallData = [];
    // Maintain a running total for padding
    var runningTotal = 0;
    // Calculate the base level of padding, this is to deal with
    // waterfalls which cross the x-axis
    var padBase = Math.abs(yMin);
    // Rearrange the data
    data.forEach(function (d, i) {
      // Add the padding bar, this will be removed later but is used
      // for positioning
      waterfallData.push({
        x: i,
        y: padBase
          + (d.type === "var" ? runningTotal : 0)
          + (d.value < 0 ? d.value : 0),
        series: "pad" });
      // Add the bar itself.  The values are always positive here.  The labels in
      // popups will be changed later.
      waterfallData.push({
        x: i,
        y: Math.abs(d.value),
        series: (d.type === "bar" ?
          "bar" : (d.value < 0 ?
          "negative" : "positive")) });
        // Move the running total for managing the flow
        runningTotal = (d.type === "var" ? runningTotal : 0) + d.value;
    });

    // Create the chart from the updated data
    var myChart = new dimple.chart(svg, waterfallData);
    myChart.setBounds(60, 30, 510, 250)
    var x = myChart.addCategoryAxis("x", "x");

    // By default bar charts are ordered by value, this forces the ordering by
    // name (which at this point includes a leading string for positioning)
    x.addOrderRule("x");

    // We need 2 y axes.  The bars will be positioned using
    // the second axis (all positive) and the first axis
    // will be used to draw the visible axis, In an all positive waterfall
    // both axes will be the same but for a negative the y2 axis will go from 0
    // to abs(yMin) + yMax to allow axis crossing
    var y1 = myChart.addMeasureAxis("y", yLabel);
    y1.overrideMin = padBase * -1;
    y1.overrideMax = yMax;
    var y2 = myChart.addMeasureAxis("y", "y");
    y2.overrideMin = 0;    
    y2.overrideMax = padBase + yMax;
    y2.hidden = true;

    // Add the series    
    var s = myChart.addSeries(["series"], dimple.plot.bar, [x, y2]);

    // Assign blue, red and green using the default colors, these can
    // be any colors. We could assign transparency to the "pad" bars but
    // to avoid tooltips we delete the bars after drawing instead
    myChart.assignColor("bar", myChart.defaultColors[0].fill);
    myChart.assignColor("positive", myChart.defaultColors[3].fill);
    myChart.assignColor("negative", myChart.defaultColors[1].fill);
    // myChart.assignColor("Profit", myChart.defaultColors[1].fill);
    

    // Draw the chart.  Code beyond this point manipulates the objects
    // and hacks some changes to the chart which would break in the event
    // of redrawing.
    // var storyboard = myChart.setStoryboard("Direct Revenue");
    // storyboard.frameDuration = 2000;
    myChart.draw(2000);

    // Remove the axis titles here
    x.titleShape.remove();
    y1.titleShape.remove();

    // Remove the leading numbers from the x axis text
    x.shapes.selectAll("text").text(function (d) {
      return (d === "" ? "" : data[parseInt(d)].label);
    });

    // Remove the padding elements entirely
    svg.selectAll(".dimple-pad").remove();

    // Change the measure name and the category names for the tooltips
    s.y.measure = yLabel;
    s.x.categoryFields = [xLabel];

    // Remove the category fields from the series, to remove from  the tooltips
    s.categoryFields = [];

    s.shapes.each(function (d) {
      // Get the index from the original data
      var j = parseInt(d.xField[0]);
      // Remove the unwanted x label prefixes from the shapes for the tooltips
      d.xField[0] = data[j].label;
      // Change the values back to negatives where necessary for tooltips
      d.height = data[j].value;
    });

});