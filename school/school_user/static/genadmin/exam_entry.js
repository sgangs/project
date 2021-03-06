$(function(){

//This variable will store the student list added via json
var student_list=[];

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var classid=1;
var examid=1;


//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

//This is called after the class option is selected
$( ".classsection" ).change(function() {
    classid=parseInt($(".classsection").find(':selected').data('id'));
    $( ".classsection" ).prop('disabled',true); 
    $( ".exam" ).prop('disabled',false);
});

//This is called to provide the average in the final score column, when internal score is changed.
$( "#student_table" ).on("change",".internal",function() {
    var internal=parseInt($(".internal").val());
    var external=parseInt($(".external").val());
    if (isNaN(internal) || isNaN(external)){
            bootbox.alert({
                size: "small",
                message: "Please input a number.",
                onEscape: true });
            clearmodal();
    }
    else{
        if (external == 0){
            $(".final").val(internal);    
        }
        else{
            var final=(internal+external)/2;
            $(".final").val(final);    
        }
    }
            
});


//This is called to provide the average in the final score column, when external score is changed.
$( "#student_table" ).on("change",".external",function() {
    var internal=parseInt($(".internal").val());
    var external=parseInt($(".external").val());
    if (isNaN(internal) || isNaN(external)){
            bootbox.alert({
                size: "small",
                message: "Please input a number.",
                onEscape: true });
            clearmodal();
    }
    else{
        var final=(internal+external)/2;
        $(".final").val(final);    
    }
});


//This function gets called as exam is entered.
$( ".exam" ).change(function() {
    examid =parseInt($(".classsection").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { examid: examid,
                classid: classid,
                calltype: 'details',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                $('.subjectdiv').attr('hidden', false);
                $('.exam').attr('disabled', true);
                $('.submit').attr('disabled', false);
                $.each(jsondata, function(){
                    if (this.data_type=="Subject"){
                        $('.subject').append($('<option>',{
                            'data-id': this.id,
                            'text': this.name
                        }));
                    }
                    else if (this.data_type=="Student")
                    $('#student_table').append("<tr class='data'>"+
                    "<td hidden='true' class='pk'>"+this.id+"</td>"+
                    "<td class='key'>"+this.key+"</td>"+
                    "<td class='local_id'>"+this.local_id+"</td>"+
                    "<td class='first_name'>"+this.first_name+"</td>"+
                    "<td class='last_name'>"+this.last_name+"</td>"+
                    "<td><input type='text' class='internal' value=0 style='text-align:center;'/></td>"+
                    "<td><input type='text' class='external'value=0 style='text-align:center;' /></td>"+
                    "<td><input type='text' class='final' style='text-align:center;' /></td>"+
                    "<td><input type='text' class='remarks'/></td>"+
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



$( ".submit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to record the attendances?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
            
    //get all itemcode & quantity pair 
        var items = [];
        var subjectid=parseInt($(".subject").find(':selected').data('id'));
        console.log("Subject: "+subjectid);
        if (isNaN(subjectid) ){
            bootbox.alert({
                size: "small",
                message: "Please select the subject.",
                onEscape: true });
            clearmodal();
        }
        else{
            $("tr.data").each(function() {
                var student_id = $(this).find('td:nth-child(1)').html();
                var internal = parseInt($(this).find('.internal').val());
                var external = parseInt($(this).find('.external').val());
                var final = parseInt($(this).find('.final').val());
                var remarks = $(this).find('td:nth-child(8)').html();
                if (internal == 0 & external == 0){
                    final = 0;
                }
                var item = {
                    student_id : student_id,
                    internal: internal,
                    external: external,
                    final: final,
                    remarks: remarks,
                    };
                items.push(item);        
                });
            
        
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
                        alert("Exem report registered successfully");
                        //location.href = redirect_url;
                        //console.log(jsondata);
                    },
                        // handle a non-successful response
                    error : function() {
                        bootbox.alert({
                            size: "medium",
                            message: "Exem report entry failed", 
                            onEscape: true });
                        clearmodal();
                    }
                });
            })();
        }        
    }, //bracket for confirm closing
});

});