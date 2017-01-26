$(function(){

    assets=0;
    long_assets=0;
    depreciation=0;
    liabilities=0;
    long_liabilities=0;
    profit=0;
    for (i in accounts){
      if (accounts[i].data_type=='assets'){
        if (assets == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td><b>ASSETS</b></td>"+
        "<td></td>"+
        "</tr>");  
        $('#trail_balance').append("<tr class='data'>"+
        "<td>CURRENT ASSETS</td>"+
        "<td></td>"+
        "</tr>");
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");                    
        assets+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='long_assets'){
        if (expense == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>LONG TERM ASSETS</td>"+
        "<td></td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>("+Math.abs(parseFloat(accounts[i].total))+")</td>"+
        "</tr>");      
        long_assets+=1;              
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='depreciation'){
        if (long_assets == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>LONG TERM ASSETS<</td>"+
        "<td><b>-</b></td>"+
        "</tr>");  
        }
        if (depreciation == 0){
          $('#trail_balance').append("<tr class='success data' style='text-align: center'>"+        
          "<td><b>Depreciation</b></td>"+
          "<td><b>Rs. "+parseFloat(accounts[i].income)+"</b></td>"+
          "</tr>");
        }
        $('#trail_balance').append("<tr class='danger data' style='text-align: center'>"+        
          "<td>"+accounts[i].account+"</td>"+
          "<td><b>Rs. "+Math.abs(parseFloat(accounts[i].income))+"</b></td>"+
          "</tr>"); 
        long_assets+=1;
        depreciation+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='total_asset'){
        if (long_assets == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>LONG TERM ASSETS</td>"+
        "<td>-</td>"+
        "</tr>");  
        }
        if (depreciation == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>DEPRECIATION</td>"+
        "<td>-</td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data info'>"+
        "<td><b>TOTAL ASSETS</B></td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");
        long_assets+=1;                   
        depreciation+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='liability'){
        if (liabilities == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td><b>LIABILITIES</b></td>"+
        "<td></td>"+
        "</tr>");  
        $('#trail_balance').append("<tr class='data'>"+
        "<td>Current Liabilities</td>"+
        "<td></td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");
        liabilities+=1;
      }
    }   
    for (i in accounts){
      if (accounts[i].data_type=='long_liability'){
        if (liabilities == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td><b>LIABILITIES</b></td>"+
        "<td></td>"+
        "</tr>");
        $('#trail_balance').append("<tr class='data'>"+
        "<td>Current Liabilities</td>"+
        "<td>-</td>"+
        "</tr>");
        }
        if (long_liabilities == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>Long Term Liabilities</td>"+
        "<td>-</td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>"+accounts[i].account+"</td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");
        liabilities+=1;
        long_liabilities+=1;
      }
    }
    for (i in accounts){
      if (accounts[i].data_type=='profit'){
        if (liabilities == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td><b>LIABILITIES</b></td>"+
        "<td></td>"+
        "</tr>");
        $('#trail_balance').append("<tr class='data'>"+
        "<td>Current Liabilities</td>"+
        "<td>-</td>"+
        "</tr>");
        }
        if (long_liabilities == 0){
        $('#trail_balance').append("<tr class='data'>"+
        "<td>Long Term Liabilities</td>"+
        "<td>-</td>"+
        "</tr>");  
        }
        $('#trail_balance').append("<tr class='data' style='text-align: center'>"+
        "<td>Net Income Over Expenses</td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");
        liabilities+=1;
        long_liabilities+=1;
      }
    }
    
    for (i in accounts){
      if (accounts[i].data_type=='total_liability'){
      $('#trail_balance').append("<tr class='data info'>"+
        "<td><b> TOTAL LIABILITIES </b></td>"+
        "<td>"+parseFloat(accounts[i].total)+"</td>"+
        "</tr>");
        liabilities+=1;
      }
    }

});