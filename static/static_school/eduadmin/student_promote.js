$(function(){


$(".old").hover(function(){
    $('.hint1').attr('hidden',false);
},function(){
    $('.hint1').attr('hidden', true);
});

$(".new").hover(function(){
    $('.hint2').attr('hidden',false);
},function(){
    $('.hint2').attr('hidden', true);
});



var from_classid="";
var from_year="";

$( ".class1" ).change(function() {
    from_classid=$('.class1').find(':selected').data('id');
});

//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });


$( ".year1" ).change(function() {
    from_year=$(".year1").val();
});

$('.fetch').click(function(e) {
    if (from_classid != '' && from_year != '' && from_classid != undefined && from_year != undefined){
        (function(){
            $.ajax({
                url : "", 
                type: "POST",
                data:{from_classid:from_classid,
                    from_year:from_year,
                    calltype: 'students',
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',
                // handle a successful response
                success : function(jsondata) {
                // location.href = redirect_url;
                console.log(jsondata);
                $.each(jsondata, function(){
                    $('.new').prop('hidden',false);
                    $('.table-responsive').prop('hidden',false);
                    $('#student_table').append("<tr class='data'>"+
                    "<td hidden>"+this.id+"</td>"+
                    "<td>"+this.key+"</td>"+
                    "<td>"+this.local_id+"</td>"+
                    "<td>"+this.first_name+" "+this.first_name+"</td>"+
                    "<td><input type='checkbox' class='promote'/></td>"+

                    "</tr>");
                })
                },
                // handle a non-successful response
                error : function() {
                    swal("Umm..", "Student doesn't exist or all students of the batch & year combination already has class ", "error");
                }
            });
        }());
    }
    else{
        swal("Oops..", "All the three fields must be filled.", "error");
    }
})


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Please confirm adding student(s) to class for selected academic year!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add student(s)!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)
            
        }
    })
});

function save_data(){
            
    //get all itemcode & quantity pair
    console.log($('.month').is(":visible")); 
        var items = [];
        var proceed = true;
        var month_entered=true
        fee_name=$(".feename").val();
        if ($('.month').is(":visible")){
            if (month ==''){
                month_entered=false
            }
        }
        if (fee_name != "" && month_entered){
            //console.log("Date: "+date);
            $("tr.data").each(function() {
                var account = $(this).find('td:nth-child(2)').find(':selected').data('id');
                var amount = parseInt($(this).find('td:nth-child(3) input').val());
                if (isNaN(amount) || typeof(account) === "undefined" ){
                    proceed=false;}
                var item = {
                    account : account,
                    amount: amount,
                    };
                items.push(item);        
            });
            console.log(items);
            if (proceed){
        //Send ajax function to back-end 
                (function() {
                    $.ajax({
                        url : "", 
                        type: "POST",
                        data:{ details: JSON.stringify(items),
                            feename: fee_name,
                            month:month,
                            csrfmiddlewaretoken: csrf_token},
                            dataType: 'json',               
                            // handle a successful response
                        success : function(jsondata) {
                            //alert("Fee Structure registered successfully");
                            location.href = redirect_url;
                            //console.log(jsondata);
                        },
                            // handle a non-successful response
                        error : function() {
                            bootbox.alert({
                                size: "medium",
                                message: "Fee Structure entry failed", 
                                onEscape: true });
                            clearmodal();
                        }
                    });
                }());
            }
            else{
                bootbox.alert({
                    size: "small",
                    message: "Please select Account and enter values in all rows.",
                    onEscape: true });
                clearmodal();

            }
        }
        else if (month_entered==false){
            bootbox.alert({
                size: "small",
                message: "Please enter the name of fee structure or the month.",
                onEscape: true });
            clearmodal();
        }
        else{
            bootbox.alert({
                size: "small",
                message: "Please enter the name of fee structure.",
                onEscape: true });
            clearmodal();
        }
    
}

});