$(function(){

income=0;
    expense=0;
    other_income=0;
    other_expense=0;
    for (i in accounts){
      if (accounts[i].data_type=='income'){
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
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>("+Math.abs(parseFloat(accounts[i].total))+")</td>"+
        "</tr>");      
        expense+=1;              
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='gross'){
        if(parseFloat(accounts[i].income) >=0){
          $('#trail_balance').append("<tr class='success data' style='text-align: center'>"+        
          "<td><b>Gross Income Over Expenditure</b></td>"+
          "<td><b>Rs. "+parseFloat(accounts[i].income)+"</b></td>"+
          "</tr>");
        }
        else{
         $('#trail_balance').append("<tr class='danger data' style='text-align: center'>"+        
          "<td><b>Gross Expenditure Over Income</b></td>"+
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
          "<td><b>Net Income Over Expense</b></td>"+
          "<td><b>Rs. "+parseFloat(accounts[i].income)+"</b></td>"+
          "</tr>");
        }
        else{
         $('#trail_balance').append("<tr class='danger data' style='text-align: center'>"+
          "<td><b>Net Expense Over Income</b></td>"+
          "<td><b>Rs. "+Math.abs(parseFloat(accounts[i].income))+"</b></td>"+
          "</tr>"); 
        }
        other_income+=1;                   
        other_expense+=1;
      }
    }


});