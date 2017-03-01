$(function(){

var year="", cadre='', proceed=true;


$( ".year" ).change(function() {
    year=$(".year").val();
});

$( ".cadre" ).change(function() {
    cadre=$(".cadre").find(':selected').data('id');
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo cadre-leave linking!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, link cadre-leave!",
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
    teachers=[]
    $.each($(".teacher option:selected"), function(){            
        teacherid=$(this).data('id')
        var teacher={
            teacherid: teacherid
        }
        teachers.push(teacher);
    });
    if (year == "" || year == undefined || cadre == "" || cadre == undefined || 
        teachers == "" || teachers == undefined || teachers == []){
        proceed=false}
    // console.log(items);
    if (proceed){
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details: JSON.stringify(teachers),
                    cadre: cadre,
                    year: year,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    swal("Hooray..", "Staff & Cadre Liknked successfully!!", "success");
                    setTimeout(location.reload(true),900)
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors. Recheck your input data while we check behind the curtains", "error");
                }
            });
        }());
    }
    else{
        swal("Oops..", "Check if all entry were correct. Year, cadre  or staff(teacher) cannot be blank.", "error");
    }
} 
});