$(function(){

income=0;
    expense=0;
    other_income=0;
    other_expense=0;
    opening=0;
    closing=0;
    console.log(accounts)
    var has_purchase = false;
    for (i in accounts){
      if (accounts[i].account == "Purchase"){
        has_purchase = true;
      }
      if (accounts[i].data_type=='opening'){
        opening=i;
        console.log("here");
      }
      else if (accounts[i].data_type=='closing'){
        closing=i;
      }
      else if (accounts[i].data_type=='income'){
        if (income == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>INCOME</td>"+
        "<td></td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");                    
        income+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='expense'){
        if (expense == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>EXPENSE</td>"+
        "<td></td>"+
        "</tr>");  
        }
        if (has_purchase){
          if (accounts[i].account == "Purchase"){
            $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
            "<td>Opening Stock</td>"+
            "<td>("+parseFloat(accounts[opening].income)+")</td>"+
            "</tr>");
            $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
            "<td>"+accounts[i].account+"</td>"+
            "<td>("+Math.abs(parseFloat(accounts[i].total))+")</td>"+
            "</tr>");
            $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
            "<td>Closing Stock</td>"+
            "<td>"+parseFloat(accounts[closing].income)+"</td>"+
            "</tr>");
          }
          else{
            $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
            "<td>"+accounts[i].account+"</td>"+
            "<td>("+Math.abs(parseFloat(accounts[i].total))+")</td>"+
            "</tr>");
          }
        }
        else{
          if (expense == 0){
            if (opening != 0){
              $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
              "<td>Opening Stock</td>"+
              "<td>("+parseFloat(accounts[opening].income)+")</td>"+
              "</tr>");
            }
            if (closing != 0){
              $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
              "<td>Closing Stock</td>"+
              "<td>"+parseFloat(accounts[closing].income)+"</td>"+
              "</tr>");
            }
          }          
          $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
            "<td>"+accounts[i].account+"</td>"+
            "<td>("+Math.abs(parseFloat(accounts[i].total))+")</td>"+
            "</tr>");
        }

        expense+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='gross'){
        if(parseFloat(accounts[i].income) >=0){
          $('#trail_balance').append("<tr class='success data' style='text-align: center'>"+        
          "<td><b>Gross Profit</b></td>"+
          "<td><b>Rs. "+parseFloat(accounts[i].income)+"</b></td>"+
          "</tr>");
        }
        else{
         $('#trail_balance').append("<tr class='danger data' style='text-align: center'>"+        
          "<td><b>Gross Loss</b></td>"+
          "<td><b>Rs. "+Math.abs(parseFloat(accounts[i].income))+"</b></td>"+
          "</tr>"); 
        }
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='other_income'){
        if (other_income == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>OTHER INCOME</td>"+
        "<td></td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");
        other_income+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='other_expense'){
        if (other_income == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>OTHER INCOME</td>"+
        "<td><b>-</b></td>"+
        "</tr>");  
        }
        if (other_expense == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>OTHER EXPENSE</td>"+
        "<td></td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>("+Math.abs(parseFloat(accounts[i].total))+")</td>"+
        "</tr>");
        other_income+=1;                   
        other_expense+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='net'){
        if (other_income == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>OTHER INCOME</td>"+
        "<td><b>-</b></td>"+
        "</tr>");  
        }
        if (other_expense == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>OTHER EXPENSE</td>"+
        "<td><b>-</b></td>"+
        "</tr>");  
        }
        if(parseFloat(accounts[i].income) >=0){
          $('#trail_balance').append("<tr class='success data' style='text-align: center'>"+
          "<td><b>Net Profit</b></td>"+
          "<td><b>Rs. "+parseFloat(accounts[i].income)+"</b></td>"+
          "</tr>");
        }
        else{
         $('#trail_balance').append("<tr class='danger data' style='text-align: center'>"+
          "<td><b>Net Loss</b></td>"+
          "<td><b>Rs. "+Math.abs(parseFloat(accounts[i].income))+"</b></td>"+
          "</tr>"); 
        }
        other_income+=1;                   
        other_expense+=1;
      }
    }


});