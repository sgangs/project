$(function(){

//This variable will store the student list added via json
var student_list=[], classid=0, present_mark=0, absent_mark=0 ,total=0;
//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}


//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$('.date').datepicker({
    autoclose: true,
    startDate: new Date(min),
    // endDate: moment(),
    endDate: '0d',
    format: 'dd/mm/yyyy',    
});


//This function gets called as year is entered.
$( ".check" ).click(function() {
    var date=$(".date").val();
    classid=parseInt($(".classsection").find(':selected').data('id'));
    if (date != '' && classid>0){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { date: date.split("/").reverse().join("-"),
                    classid: classid,
                    calltype: 'details',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata){
                    present_mark=0, absent_mark=0 ,total=0;
                    $("#student_table .data").remove();
                    $('.total_data').remove();
                    $('.present_data').remove();
                    $('.absent_data').remove();
                    if (jsondata.length<1){
                        swal("Umm..", "Class and date combination doesn't have any attendance.", "info");
                        $('.details').attr('hidden', true);
                    }
                    else{
                        $('.details').attr('hidden', false);
                        $.each(jsondata, function(){
                            present="Not Present";
                            total+=1
                            if (this.is_present=="True"){
                                present="Present";
                                present_mark+=1
                            }
                            else{
                                absent_mark+=1
                            }
                            $('#student_table').append("<tr class='data'>"+
                            "<td class='key' hidden='true'>"+this.id+"</td>"+
                            "<td class='key'>"+this.key+"</td>"+
                            "<td class='local_id'>"+this.local_id+"</td>"+
                            "<td>"+this.first_name+"</td>"+
                            "<td>"+this.last_name+"</td>"+
                            "<td>"+present+"</td>"+
                            "<td>"+this.remarks+"</td>"+
                            "</tr>");                    
                        })
                        $('.total').append("<label class='total_data'>" + total+"</label>");
                        $('.present').append("<label class='present_data'>" + present_mark+"</label>");
                        $('.absent').append("<label class='absent_data'>" + absent_mark+"</label>");
                    }
                },
                // handle a non-successful response
                error : function() {
                    present_mark=0, absent_mark=0 ,total=0;
                    $('.details').attr('hidden', true);
                    $('.total_data').remove();
                    $('.present_data').remove();
                    $('.absent_data').remove();
                    swal("Oops..", "Class and date combination doesn't have any attendance.", "error");                    
                }
            });
        }());
    }
    else{
        swal("Oops..", "Class or date cannot be blank.", "error");
    }
});

});