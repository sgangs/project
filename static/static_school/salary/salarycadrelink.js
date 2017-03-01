$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var year=0;
var cadre=0;
var monthly_salary=0;
var epsepf=0;
var epf_employee=0;
var esi_employee=0;
var esi_employer=0;
var edli_employer=0;


$( ".year" ).change(function() {
    year=parseInt($('.year').val());
});


$( ".cadre" ).change(function() {
    cadre=parseInt($(".cadre").find(':selected').data('id'));
});

//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });



$('.save').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "<b>You cannot undo salary structure linking!</b> This Salary Structure shall be fixed for the whole academic year.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, link fee structure! COnfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
});

function reconfirm () {
    swal({
        title: "Please Reconfirm",
        text: "<b>You cannot undo salary structure linking!</b> This Salary Structure shall be fixed for the whole academic year.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, link salary structure! Reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
};
    
function save_data(){
    var yearly_salary=[];
    var class_group = [];
    $.each($(".yearly_salary option:selected"), function(){
        salaryid=$(this).data('id')
        var salary={
            salary_id: salaryid
        };
        yearly_salary.push(salary);
    });
    monthly_salary=$(".monthly_salary").find(':selected').data('id');
    epsepf=$(".epsepf").find(':selected').data('id');
    epf_employee=$(".epf_employee").find(':selected').data('id');
    esi_employer=$(".esi_employer").find(':selected').data('id');
    esi_employee=$(".esi_employee").find(':selected').data('id');
    edli_employer=$(".edli_employer").find(':selected').data('id');
        //add_student=$(".addstudent").find(':selected').data('id');
    if (year !='' && monthly_salary != '' && monthly_salary != 'undefined' && year>1980 && year<2100 ){
            //console.log("Date: "+date);
            
        if (cadre>0)
        {
            console.log("Proceed");
            // Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ cadre: cadre,
                        monthly_salary: monthly_salary,
                        yearly_salary: JSON.stringify(yearly_salary),
                        year: year,
                        epsepf:epsepf,
                        epf_employee:epf_employee,
                        esi_employer:esi_employer,
                        esi_employee:esi_employee,
                        edli_employer: edli_employer,
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                                // alert("Group Fee linked successfully");
                        swal("Hooray", "Salary structure linked successfully!", "success");
                        // setTimeout(function(){location.href = redirect_url;},2000);
                        setTimeout(function(){location.reload(true);},2000);
                                //console.log(jsondata);
                        },
                                // handle a non-successful response
                    error : function() {
                        swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                    }
                });
            }());
        }
        else{
            swal("Oops...", "Recheck your inputs. Cadre must be selected to link with salary structure.", "error");
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