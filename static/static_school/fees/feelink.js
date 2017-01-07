$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var year='';
var add_student="";
var monthly_fee="";


//This is called after the fee structure name is entered
// $( ".feename" ).change(function() {
//     fee_name=$(".feename").val();
//     $( ".submit" ).prop('disabled',false); 
// });
//This is called if month is changed
$( ".year" ).change(function() {
    year=parseInt($('.year').val());
});

//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });


$( ".save" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to link the class to fee structure?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
        var yearly_fees=[];
        var class_group = [];
        $.each($(".yearlyfee option:selected"), function(){
            feeid=$(this).data('id')
            var fee={
                fee_id: feeid
            };
            yearly_fees.push(fee);
        });
        $.each($(".classgroup option:selected"), function(){            
            classgroupid=$(this).data('id')
            var classgroup={
                classgroup_id: classgroupid
            }
           class_group.push(classgroup);
        });
        monthly_fee=$(".monthlyfee").find(':selected').data('id');
        //add_student=$(".addstudent").find(':selected').data('id');
        add_student="Yes"
            
        if (yearly_fees.length != 0 && typeof(monthly_fee) != "undefined" && year !='' && add_student != '' && class_group.length!=0){
            //console.log("Date: "+date);
            //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ classgroups: JSON.stringify(class_group),
                        monthlyfee: monthly_fee,
                        yearlyfees: JSON.stringify(yearly_fees),
                        year: year,
                        addstudent: add_student,
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                            // handle a successful response
                    success : function(jsondata) {
                            alert("Group Fee linked successfully");
                            //location.href = redirect_url;
                            //console.log(jsondata);
                    },
                            // handle a non-successful response
                    error : function() {
                            bootbox.alert({
                                size: "medium",
                                message: "Fee linking entry failed", 
                                onEscape: true });
                            clearmodal();
                    }
                });
            }());
            
        }
        else{
            bootbox.alert({
                size: "small",
                message: "Please enter all the fields. No field shall be left blank",
                onEscape: true });
            clearmodal();
        }
    
    }, //bracket for confirm closing
});


});