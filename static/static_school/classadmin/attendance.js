$(function(){

//This variable will store the student list added via json
var student_list=[];
var date="";
var items=[];
var total_present=0;
var total_absent=0;

var classid="";
//This will help to remove the error modal.

$('.date').datepicker({
    autoclose: true,
    startDate: new Date(min),
    // endDate: moment(),
    endDate: '0d',
    format: 'dd/mm/yyyy',    
});


//This is called after the class option is selected
$( ".classsection" ).change(function() {
    classid=parseInt($(".classsection").find(':selected').data('id'));
    $( ".classsection" ).prop('disabled',true); 
    $(".datediv").attr('hidden', false);
    // $( ".year" ).prop('disabled',false);
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$( ".date" ).change(function() {
    date=$('.date').val()
    // year =parseInt($(this).val());
    classid=parseInt($(".classsection").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { classid: classid,
                date: date.split("/").reverse().join("-"),
                // year: year,
                calltype: 'details',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                $("#student_table .data").remove();
                $('.details').attr('hidden', false);
                $.each(jsondata, function(){
                    $('#student_table').append("<tr class='data'>"+
                    "<td hidden='true' class='pk'>"+this.id+"</td>"+
                    "<td class='key'>"+this.key+"</td>"+
                    "<td class='local_id'>"+this.local_id+"</td>"+
                    "<td>"+this.first_name+"</td>"+
                    "<td>"+this.last_name+"</td>"+
                    "<td><input type='checkbox' class='is_present'/></td>"+
                    "<td><input type='text' class='reason'  /></td>"+
                    "</tr>");
                })
                $(".date").attr('disabled', true);
                $(".btn").attr('disabled', false); 
                // $(".year").attr('disabled', true);
                $( ".classsection" ).prop('disabled',true); 
            },
            // handle a non-successful response
            error : function() {
                $("#student_table .data").remove();
                $('.details').attr('hidden', true);
                swal("Oops..", "Attendance is already taken. Please recheck", "error");                
            }
        });
    }());
});

//Check why is this not working, even after the class is getting added - Bootstrap issue
$( "#student_table" ).on("change",".is_present",function() {
    if ($(this).is(":checked")){
        $(this).parent().parent().addClass("table-success");
    }
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo attendance record!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, record attendance.",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            get_data()
            setTimeout(function(){reconfirm()},600)
            
        }
    })
});


function get_data(){
    items=[];
    total_present=0;
    total_absent=0;
    date=$('.date').val()
    if (date != ""){
        $("tr.data").each(function() {
            var student_id = $(this).find('td:nth-child(1)').html();
            var is_present = $(this).find('td:nth-child(6) input').is(":checked");
            var remarks = $(this).find('td:nth-child(7) input').val();
            var item = {
                student_id : student_id,
                is_present: is_present,
                remarks: remarks,
            };
            items.push(item);
            if (is_present){
                total_present++;
            }
            else{
                total_absent++;
            }
        });
    }
}

function reconfirm() {
    swal({
        title: "Please Reconfirm!",
        text: "<p>Date: "+date+" </p><p> Total Present: "+total_present+"</p><p> Total Absent: "+total_absent+"</p>",
        type: "info",
        showCancelButton: true,
        // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, please confrim.",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)            
        }
    })
}

function save_data(){            
    // var items = [];
    // date=$('.date').val()
    if (date != ""){
        // Get data function defined earlier gets the attendance.
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details: JSON.stringify(items),
                    date: date.split("/").reverse().join("-"),
                    classid: classid,
                    // year: year,
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                success : function(jsondata) {
                    //alert("Attendance registered successfully");
                    location.href = redirect_url;
                    //console.log(jsondata);
                },
                    // handle a non-successful response
                error : function() {
                    swal("Oops..", "Attendance entry failed. Please check if attendance was already taken for " +date, "error");                    
                }
            });
        }());
    }
    else{
        swal("Oops..", "Please enter the date.", "error");
    }
};

});