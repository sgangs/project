$(function(){

//This will help parse quantity to proper float value.
function parseFloatHTML(item) {
    return parseFloat(item.replace(/[^\d\.\-]+/g, ''));
}

//This is used to remove the alert modal
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}


//get address of customer from database

var classgroup='';
var classname='';
var room='';
var classteacher='';
var year='';
var teacher_added=false;
var classnameproceed=true;
$( ".classgroup" ).change(function() {
    classgroup=$(".classgroup").find(':selected').data('id');
    $( ".classname" ).attr('disabled',false); 
});
$( ".classname" ).change(function() {
    classname=$(".classname").val();
    (function() {
    $.ajax({
        url : "", 
        type : "POST", 
        data : { classname: classname,
            calltype: 'classname',
            csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            if (jsondata['name'] == "Class Exist"){
                $(".classnamediv").addClass('has-error');
                alert ("Error with div");
                classnameproceed == false;
            }
            
            //console.log("success"); // another sanity check
        },
        //handle a non-successful response
        error : function() {
        }
    });
    }());
});

$( ".room" ).change(function() {
    room=$(".room").val();
});
$( ".classteacher" ).change(function() {
    classteacher=$(".classteacher").find(':selected').data('id');
    if (classteacher != ''){
        teacher_added=true;
    }
    
});
$( ".year" ).change(function() {
    year=$(".year").val();
});


//The following function works as the save button is clicked - 
//sending the necessary details to back-end


$( ".save" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to add class?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
    save_class("save")}
});

//If credit note is of cash refund type
$( ".saveadd" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to add class?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
    save_class("saveadd")}
});




function save_class(save_type){
    if (classgroup =='' && classname == ''){
        $( ".classnamediv" ).addClass('has-error');
        $( ".classgroupdiv" ).addClass('has-error');
        bootbox.alert({
            size: "medium",
            message: "Please note classgroup and new class name cannot be blank.",
            onEscape: true });
        clearmodal();
    }
    else if (classgroup ==''){
        $( ".classgroupdiv" ).addClass('has-error');
        bootbox.alert({
            size: "medium",
            message: "Please note classgroup cannot be blank.",
            onEscape: true });
        clearmodal();
    }
    else if (classname == ''){
            $( ".classnamediv" ).addClass('has-error');
        bootbox.alert({
            size: "medium",
            message: "Please note new class name cannot be blank.",
            onEscape: true });
        clearmodal();    
    }
    else{
        //check whether teacher is added. If teacher is added, make sure year is also added.
        var proceed=false;
        if (teacher_added == false && classnameproceed == true){
            proceed=true;
        }
        else if (teacher_added=true && year !='' && classnameproceed == true){
            proceed=true
        }
        //Ajax function sending data to backend if customer is not blank, else request user to enter customer details
        if (proceed){
            //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ classgroup: classgroup,
                        classname: classname,
                        room:room,
                        classteacher: classteacher,
                        year: year,
                        teacher_added: teacher_added,
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                    success : function(jsondata) {
                        if (save_type=="saveadd") {
                            //console.log(jsondata['name'])
                            location.reload(true);
                        }
                        else{
                            //alert("Sales Invoice generated successfully");
                            location.href = redirect_url;
                            //console.log(jsondata);
                        }                    
                    },

                    // handle a non-successful response
                    error : function() {
                        bootbox.alert({
                            size: "small",
                            message: "Class creation failed.", 
                            onEscape: true });
                        clearmodal();
                    }
                });
            }());
        }
        else if (classnameproceed == true){
                bootbox.alert({
                    size: "medium",
                    message: "Class teacher entry must have corresponding year.",
                    onEscape: true });
                clearmodal();
                    //location.reload(true);
        }
        else {
                bootbox.alert({
                    size: "medium",
                    message: "Class teacher entry must have corresponding year.",
                    onEscape: true });
                clearmodal();
                    //location.reload(true);
        }
    }
};

});