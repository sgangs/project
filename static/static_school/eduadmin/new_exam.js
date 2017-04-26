$(function(){

var term_id='';
var exam_name='';
var exam_key='';
var exam_total='';
var exam_serial='';

$( ".key" ).change(function() {
    exam_key=$(".key").val();
    (function() {
    $.ajax({
        url : "", 
        type : "POST", 
        data : { exam_key: exam_key,
            calltype: 'Exam Key',
            csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            if (jsondata['name'] == "This item exists"){
                $(".keydiv").addClass('has-error');
                $('.submit').attr('disabled',true);
                swal("Opps..", "This key already exist!!", "error");
                exam_key='';
            }
            else{
                $('.submit').attr('disabled',false);
                $(".keydiv").removeClass('has-error');
                $(".keydiv").addClass('has-success');
            }
        },
        //handle a non-successful response
        error : function() {
            $('.submit').attr('disabled',false);
            $(".keydiv").removeClass('has-error');
            $(".keydiv").addClass('has-success');
        }
    });
    }());
});


$(".name").change(function() {
    $(".namediv").removeClass('has-error');
    $(".namediv").addClass('has-success');
});

$(".total").change(function() {
    $(".totaldiv").removeClass('has-error');
    $(".totaldiv").addClass('has-success');
});

$(".serial").change(function() {
    $(".serialdiv").removeClass('has-error');
    $(".serialdiv").addClass('has-success');
});

$(".term").change(function() {
    $(".termdiv").removeClass('has-error');
    $(".termdiv").addClass('has-success');
});

$(".group").change(function() {
    $(".groupdiv").removeClass('has-error');
    $(".groupdiv").addClass('has-success');
});
//The following function works as the save button is clicked - 
//sending the necessary details to back-end

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "This will create exam for the current academic year!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, exam creation confirmed",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
});


function save_data(save_type){
    var proceed=true;
    exam_name=$(".name").val();
    term_id=parseInt($(".term").find(':selected').data('id'));
    exam_total=parseInt($(".total").val());
    exam_serial=parseInt($(".serial").val());
    exam_weightage=1;
    var classgroups = [];
    $.each($(".classgroup option:selected"), function(){
        group_id=$(this).data('id')
        var group={
            group_id: group_id
        };
        classgroups.push(group);
    });
    if (exam_name == '' || exam_name == 'undefined'){
        proceed=false;
        $(".namediv").addClass('has-error');
    }
    if (term_id == '' || term_id == 'undefined' || isNaN(term_id)){
        proceed=false;
        $(".termdiv").addClass('has-error');
    }
    if (exam_total == '' || exam_total == 'undefined' || isNaN(exam_total)){
        proceed=false;
        $(".totaldiv").addClass('has-error');
    }
    if (exam_serial == '' || exam_serial == 'undefined' || isNaN(exam_serial)){
        proceed=false;
        $(".serialdiv").addClass('has-error');        
    }
    if (exam_key == '' || exam_key == 'undefined'){
        proceed=false;
        $(".keydiv").addClass('has-error');
    }
    if (classgroups.length==0){
        proceed=false;
        $(".groupdiv").addClass('has-error');
    }
    if (proceed){
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ classgroups: JSON.stringify(classgroups),
                    exam_name: exam_name,
                    term_id:term_id,
                    exam_key: exam_key,
                    exam_total: exam_total,
                    exam_weightage: exam_weightage,
                    exam_serial: exam_serial,
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    // if (save_type=="saveadd") {
                    //     location.reload(true);
                    //     }
                    // else{
                    //     location.href = redirect_url;
                    // }
                    swal("Hooray", "Exam created successfully!", "success");
                    setTimeout(function(){
                        location.href = redirect_url;
                        },2000);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops", "Exam creation has some error!", "error");
                }
            });
        }());
    }
    else {
        swal("Bluhhh..", "Please re-fill the form. Erorrs are highlighted!", "error");
    }
};

});