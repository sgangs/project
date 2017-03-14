$(function(){


// $(".old").hover(function(){
//     $('.hint1').attr('hidden',false);
// },function(){
//     $('.hint1').attr('hidden', true);
// });

// $(".new").hover(function(){
//     $('.hint2').attr('hidden',false);
// },function(){
//     $('.hint2').attr('hidden', true);
// });

$( ".hint1" ).click(function() {
    swal({
        type: "info",
        title: "How To",
        text: "Select the class (section) and enter the current (old) academic year of the students",
        html: true,
        timer: 15000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});

$( ".hint2" ).click(function() {
    swal({
        type: "info",
        title: "How To",
        text: "Select the new class (section) and enter the start year of the academic year  where the students will be promoted."+ 
        "Then select the students who shall have to be promoted.",
        html: true,
        timer: 15000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});

//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });

var from_classid="";
var from_year="";

$( ".class1" ).change(function() {
    from_classid=$('.class1').find(':selected').data('id');
});

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
                    $("#student_table .data").remove();
                    if (Object.keys(jsondata).length == 0){
                        swal("Umm..", "Student doesn't exist for said combination.", "warning");
                    }
                    else{
                        $('.class1').attr('disabled',true);
                        $('.year1').attr('disabled',true);
                        $('.new').prop('hidden',false);

                        $.each(jsondata, function(){                    
                            $('.table-responsive').prop('hidden',false);
                            $('#student_table').append("<tr class='data'>"+
                            "<td hidden>"+this.id+"</td>"+
                            "<td>"+this.key+"</td>"+
                            "<td>"+this.local_id+"</td>"+
                            "<td>"+this.first_name+" "+this.last_name+"</td>"+
                            "<td style='text-align: center'><input type='checkbox' class='promote'/></td>"+
                            "<td><input type='text' class='form-control roll'/></td>"+
                            "</tr>");
                        })
                    }
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

var to_classid=0;
var to_year=0;

$( ".class2" ).change(function() {
    to_classid=$('.class2').find(':selected').data('id');
});

$( ".year2" ).change(function() {
    to_year=$(".year2").val();
});

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Please confirm promoting/movings student(s) to new class/academic year! This cannot be undone.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, promote/move student(s)!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
});

function save_data(){
    var proceed = true;        
    var items = [];    
    if (to_classid != 0 && to_year != 0 && typeof(to_classid) != "undefined" && typeof(to_year) != "undefined"){
        $("tr.data").each(function() {
            var student_id = parseInt($(this).find('td:nth-child(1)').html());
            var is_promoted = $(this).find('td:nth-child(5) input').is(":checked");
            var roll_no = parseInt($(this).find('td:nth-child(6) input').val());
            if (is_promoted){
                console.log("here")
                if (isNaN(roll_no) || typeof(roll_no) === "undefined" ){  
                    proceed=false;
                    console.log("Here");
                }
            }                
            var item = {
                student_id : student_id,
                is_promoted: is_promoted,
                roll_no: roll_no
            };
            items.push(item);        
        });
        console.log(proceed);
        if (proceed){
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ from_classid:from_classid,
                        from_year:from_year,
                        to_classid: to_classid,
                        to_year: to_year,
                        details: JSON.stringify(items),
                        calltype: 'promote',
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                        // location.href = redirect_url;
                        // console.log(jsondata);
                        swal("Hooray..", "Data recorder successfully.", "success");
                        setTimeout(function(){location.reload(true);},750);
                    },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors.", "error");                            
                    }
                });
            }());
        }
        else{
            swal("Oops..", "All promoted students must have a roll no.", "error");
        }
        }
    else{
        swal("Oops..", "Please select class and academic year before clicking submit", "error");
    }
    
}

});