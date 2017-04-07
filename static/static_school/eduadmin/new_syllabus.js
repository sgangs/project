$(function(){

//This variable will store the student list added via json

var class_group_id="";
var subject_id="";

$(".delete").on('click', function() {
    $('.case:checkbox:checked').parents("tr").remove();
    $('.check_all').prop("checked", false); 
});

$(".addmore").on('click',function(){
    var data="<tr class='data'>"+
    "<td><input type='checkbox' class='case'/></td>"+
    "<td><input style='text-align: center' type='text' class='form-control'></td>"+
    "<td><input style='text-align: center' type='text' class='form-control'></td>";
    $('table').append(data);        
});

//This is called after the fee structure name is entered
$( ".class_group" ).change(function() {
    class_group_id=parseInt($(".class_group").find(':selected').data('id'));
});

$( ".subject" ).change(function() {
    subject_id=parseInt($(".subject").find(':selected').data('id'));
});


//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });

$('.submit').click(function(e) {
    swal({
        title: "Finalize Syllabus?",
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
    var is_additional= $('additional').is(":checked");
    var is_elective=$('elective').is(":checked");

    var is_additional= false
    var is_elective= false;

    $("tr.data").each(function() {
        var topic = $(this).find('td:nth-child(2) input').val();
        var month = $(this).find('td:nth-child(3) input').val();
        if (typeof(topic) == "undefined" || topic == ""){
            proceed=false;}
        var item = {
            topic : topic,
            month: month,            
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
                    class_group_id:class_group_id,
                    subject_id: subject_id,
                    is_elective:is_elective,
                    is_additional:is_additional,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                swal("Hooray..", "Syllabus registered successfully!!", "success");
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
        swal("Oops..", "Please check all entry. No row shall have the topic blank.", "error");
    }
};

});


