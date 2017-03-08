$(function(){

//This variable will store the student list added via json
var student_list=[];

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var classid=0, examid=0, subjectid=0, year=0;


//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

//This is called after the class option is selected
$( ".classsection" ).change(function() {
    classid=parseInt($(".classsection").find(':selected').data('id'));
    $( ".classsection" ).prop('disabled',true); 
    $( ".year" ).prop('disabled',false);
    // $('.subjectdiv').attr('hidden', false);
});

$( ".year" ).change(function() {
    year=parseInt($(".year").val());
    if (!isNaN(year)){
        if (year<2080 && year >1980){
            $( ".exam" ).prop('disabled',false);
            $('.subjectdiv').attr('hidden', false);
        }
        else{
            $( ".exam" ).prop('disabled',true);
            $('.subjectdiv').attr('hidden', true);   
        }
    }
    else{
        $( ".exam" ).prop('disabled',true);
        $('.subjectdiv').attr('hidden', true);
    }
});

//This is called after the exam data are entered
$( ".exam" ).change(function() {
    examid =parseInt($(".exam").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { examid: examid,
                classid: classid,
                year: year,
                calltype: 'details',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                //console.log(jsondata);
                $('.subjectdiv').attr('hidden', false);
                $('.exam').attr('disabled', true);
                $('.year').attr('disabled', true);
                // $('.submit').attr('disabled', false);
                $.each(jsondata, function(){
                    if (this.data_type=="Subject"){
                        $('.subject').append($('<option>',{
                            'data-id': this.id,
                            'text': this.name
                        }));
                    }
                })
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and exam combination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});

// //This is called to provide the average in the final score column, when internal score is changed.
// $( "#student_table" ).on("change",".internal",function() {
//     var internal=parseInt($(this).find(".internal").val());
//     var external=parseInt($(this).find(".external").val());
//     if (isNaN(internal) || isNaN(external)){
//             bootbox.alert({
//                 size: "small",
//                 message: "Please input a number.",
//                 onEscape: true });
//             clearmodal();
//     }
//     else{
//         if (external == 0){
//             $(".final").val(internal);    
//         }
//         else{
//             var final=(internal+external)/2;
//             $(".final").val(final);    
//         }
//     }
            
// });


// //This is called to provide the average in the final score column, when external score is changed.
// $( "#student_table" ).on("change",".external",function() {
//     var internal=parseInt($(this).find(".internal").val());
//     var external=parseInt($(this).find(".external").val());
//     if (isNaN(internal) || isNaN(external)){
//             bootbox.alert({
//                 size: "small",
//                 message: "Please input a number.",
//                 onEscape: true });
//             clearmodal();
//     }
//     else{
//         var final=(internal+external)/2;
//         $(".final").val(final);    
//     }
// });


//This function gets called as exam is entered.
$( ".subject" ).change(function() {
    subjectid=parseInt($(".subject").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { examid: examid,
                classid: classid,
                year:year,
                subjectid: subjectid,
                calltype: 'subject',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                //console.log(jsondata);
                $('.subject').attr('disabled', true);
                $('.report').attr('hidden', false);
                $('.submit').attr('disabled', false);
                $.each(jsondata, function(){
                    if (this.data_type=="Student")
                    $('#student_table').append("<tr class='data'>"+
                    "<td hidden='true' class='pk'>"+this.id+"</td>"+
                    "<td class='key'>"+this.key+"</td>"+
                    "<td class='local_id'>"+this.local_id+"</td>"+
                    "<td class='last_name'>"+this.roll_no+"</td>"+
                    "<td class='first_name'>"+this.first_name+"</td>"+
                    "<td class='last_name'>"+this.last_name+"</td>"+
                    "<td><input type='text' class='form-control final' value=0 style='text-align:center;'/></td>"+
                    "<td><input type='text' class='form-control grade' style='text-align:center;' /></td>"+
                    "<td><input type='text' class='form-control grade_point' style='text-align:center;' /></td>"+
                    "<td><input type='text' class='form-control remarks'/></td>"+
                    "</tr>");
                })
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and exam combination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});


$( ".table" ).on('change', '.final',function() {
    score=$(this).val()
    table=$(this)
    $.each(grades, function(){
        if (score<=this.max_mark && score>=this.min_mark){
            table.closest("tr").find('td:nth-child(8) input').val(this.grade);
            table.closest("tr").find('td:nth-child(9) input').val(this.grade_point);
            return false;
        }
    });
});

$('.submit').click(function(e) {
    swal({
        title: "Record Marks/Grade?",
        text: "You cannot undo student fee payment!",
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
    var proceed=true;            
    //get all itemcode & quantity pair 
    var items = [];
    if (isNaN(subjectid) ){
        swal("Oops..", "Please select the subject.", "error");
        proceed=false;
    }
    else{
        $("tr.data").each(function() {
            var student_id = $(this).find('td:nth-child(1)').html();
            var final = parseInt($(this).find('.final').val());
            var grade = $(this).find('td:nth-child(8) input').val();
            var grade_point = parseFloat($(this).find('td:nth-child(9) input').val());
            var remarks = $(this).find('td:nth-child(10)').val();
            if ($.trim(grade).length<1 || typeof(grade) == "undefined" || typeof(grade_point) == "undefined" || isNaN(grade_point)){
                proceed=false;
            }
            var item = {
                student_id : student_id,
                final: final,
                grade: grade,
                grade_point: grade_point,
                remarks: remarks,
            };
            items.push(item);        
        });
        console.log(items);
        console.log("Listed");
        
        if (proceed){
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ details: JSON.stringify(items),
                        subjectid: subjectid,
                        classid: classid,
                        examid: examid,
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                        swal("Hooray..", "Exam report registered!!", "success");
                        setTimeout(location.reload(true),750);
                        //location.href = redirect_url;
                        //console.log(jsondata);
                    },
                        // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors!!", "error");
                    }
                });
            })();
        }
        else{
            swal("Oops..", "Pleae check the inputs. There has been errors!!", "error");
        }        
    }
};

});