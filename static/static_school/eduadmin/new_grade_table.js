$(function(){

//This variable will store the student list added via json


$(".delete").on('click', function() {
    $('.case:checkbox:checked').parents("tr").remove();
    $('.check_all').prop("checked", false); 
});

$(".addmore").on('click',function(){
    var data="<tr class='data'>"+
    "<td><input style='text-align: center' type='number' class='form-control max'></td>"+
    "<td><input style='text-align: center' class='form-control min'></td>"+
    "<td><input style='text-align: center; text-transform: uppercase;' type='text' class='form-control grade'></td>"+
    "<td><input style='text-align: center' type='text' class='form-control grade_point'></td>"+"</tr>";
    $('table').append(data);        
});

//This is called after the fee structure name is entered
// $( ".feename" ).change(function() {
//     fee_name=$(".feename").val();
//     $( ".submit" ).prop('disabled',false); 
// });


//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$('.submit').click(function(e) {
    swal({
        title: "Finalize Grade Table?",
        // text: "You cannot undo student fee payment!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
});


function save_data(){
    //get all itemcode & quantity pair
    var items = [];
    var proceed = true;
    var sl_no=1;
    $("tr.data").each(function() {
        var max = parseInt($(this).find('td:nth-child(1) input').val());
        var min = parseInt($(this).find('td:nth-child(2) input').val());
        var grade = $(this).find('td:nth-child(3) input').val();
        var grade_point = parseInt($(this).find('td:nth-child(4) input').val());
        if (isNaN(max) || typeof(max) == "undefined" || isNaN(min) || typeof(min) == "undefined" || 
            $.trim(grade).length<1 || typeof(grade) == "undefined"|| isNaN(grade_point)|| typeof(grade_point) == "undefined" ){
            proceed=false;}
        if (max<min){
            proceed=false;
            swal("Oops..", "Maximum should be more than minimum.", "error");
        }
        var item = {
            min : min,
            max: max,
            grade: grade.toUpperCase(),
            grade_point: grade_point,
            sl_no: sl_no
        };
        items.push(item);
        sl_no++;
    });
    console.log(items);
    if (proceed){
    //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details: JSON.stringify(items),
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                //alert("Fee Structure registered successfully");
                swal("Hooray..", "Grade Table registered successfully!!", "success");
                setTimeout(location.reload(true),600);
                //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors!!", "error");
                }
            });
        }());
    }
    else{
        swal("Oops..", "Please check all entry. No row shall be blank", "error");
    }
};

});


