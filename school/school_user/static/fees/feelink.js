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


//This is called if month is changed
$( ".year" ).change(function() {
    year=parseInt($('.year').val());
});

//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });


// $( ".save" ).confirm({
//     title: 'Confirm!',
//     icon: 'fa fa-spinner fa-spin',
//     theme: 'black',
//     backgroundDismiss: true,
//     content: 'Are you sure to link the class to fee structure?',
//     confirmButton: 'Yes!',
//     cancelButton: 'No!',
//     autoClose: 'cancel|6000',
//     confirmButtonClass: 'btn-success',
//     cancelButtonClass: 'btn-danger',
//     animation: 'rotateY',
//     closeAnimation: 'rotateXR',
//     animationSpeed: 750,
//     confirm: save_data() });


$('.save').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo fee structure linking!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, link fee structure!",
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
    if (year !='' && add_student != '' && class_group.length!=0){
            //console.log("Date: "+date);
            //Send ajax function to back-end 
        if (yearly_fees.length != 0 || typeof(monthly_fee) != "undefined" )
        {
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
                                // alert("Group Fee linked successfully");
                        swal("Hooray", "Fee structure linked successfully!", "success");
                        setTimeout(function(){
                        location.href = redirect_url;
                        },2000);
                                //console.log(jsondata);
                        },
                                // handle a non-successful response
                    error : function() {
                                // bootbox.alert({
                                //     size: "medium",
                                //     message: "Fee linking entry failed", 
                                //     onEscape: true });
                                // clearmodal();
                        swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                    }
                });
            }());
        }
        else{
            swal("Oops...", "Recheck your inputs. Either yearly fees or monthly fees must be filled!", "error");
        }
    }
    else{
            // bootbox.alert({
            //     size: "small",
            //     message: "Please enter all the fields. No field shall be left blank",
            //     onEscape: true });
            // clearmodal();
    swal("Oops...", "Recheck your inputs. No fields shall be blank!", "error");
    }
}
    
    
});