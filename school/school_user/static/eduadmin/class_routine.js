$(function(){

//This variable will store the student list added via json
var student_list=[];

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

//This function gets called as year is entered.
$( ".year" ).change(function() {
    var year = $(this).val();
    //alert (year)
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { year: year,
                calltype: 'year',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {  
                console.log(jsondata);
                $.each(jsondata, function(){
                    if (this.data_type=="Teacher"){
                        $('.classteacher').append(this.first_name+" "+this.last_name);
                        $('.classteacherdiv').attr('hidden',false);
                    }
                    else if (this.data_type=="Syllabus"){
                        $('.classsubjectdiv').attr('hidden',false);
                        $('#subject_table').append("<tr>"+
                        "<td>" + this.subject + "</td>"+
                        "<td>" + this.topics + "</td></tr>");
                        $('.selectsubject').append($('<option>',{
                        'data-id': this.id,
                        'text': this.subject
                        }));
                    }
                    else if (this.data_type=="Error"){
                        bootbox.alert({
                            message: this.message, 
                            onEscape: true }); // provide a bit more info about the error to the user
                        clearmodal();
                    }
                });
                $('.addperiod').prop('disabled', false);
                $('.year').prop('disabled', true);
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Data not available for selected year.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});

});
