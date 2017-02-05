$(function(){

function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

// page is now ready, initialize the calendar...
$('#calendar').fullCalendar({
// put your options and callbacks here
    header: {
        left: 'myCustomButton',
        center: 'title',
        right: 'prev,next, month, agendaWeek, today'
    },

    height:400,

    events: function(start,end, timezone, callback){
        $.ajax({
            url: "",
            type: "POST",
            data: {csrfmiddlewaretoken: csrf_token,
                calltype: 'event',
                start:start.format(),
                end:end.format()},
            success: function(jsondata){
                events=[]
                var source={}
                $.each(JSON.parse(jsondata), function(){
                    events.push({           
                            title: this.title,
                            start: moment(this.start).format('YYYY/MM/DD hh:mm'), // will be parsed . Error here.
                            end: moment(this.start).format('YYYY/MM/DD hh:mm'),
                            allDay: true,
                            })
                });
                var source={events};

                callback(events)
            }
        });
    },    
})

// $('.fc-myCustomButton-button').append('<i class="glyphicon glyphicon-plus"</i>')
$('.event').attr('data-toggle',"modal")
$('.event').attr('data-target',"#event")

$('.annualrule').attr('data-toggle',"modal")
$('.annualrule').attr('data-target',"#annualrule")

//This variable will store the student list added via json

// $( ".submitevent" ).confirm({
//     title: 'Confirm!',
//     icon: 'fa fa-spinner fa-spin',
//     theme: 'black',
//     backgroundDismiss: true,
//     content: 'Are you sure to record the event?',
//     confirmButton: 'Yes!',
//     cancelButton: 'No!',
//     autoClose: 'cancel|6000',
//     confirmButtonClass: 'btn-success',
//     cancelButtonClass: 'btn-danger',
//     animation: 'rotateY',
//     closeAnimation: 'rotateXR',
//     animationSpeed: 750,
//     confirm: });


$('.submitevent').click(function(e) {
    swal({
        title: "Add Event?",
        text: "Are you sure you want to add the event!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add event!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){eventadd()},600)
            
        }
    })
});

$('.submitrule').click(function(e) {
    swal({
        title: "Add Rule?",
        text: "Are you sure you want to add the rule!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add rule!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){ruleadd()},600)
            
        }
    })
});



function eventadd(){            
    //get all itemcode & quantity pair 
    var eventname = "",
        date = "",
        eventtype="",
        atttype = ""

    eventname=$(".eventname").val();
    date=$(".date").val();
    eventtype=$(".eventtype").find(':selected').data('id');
    atttype=$("#attendance").find(':selected').data('id');
    if (eventname=="" || date=="" || atttype == "" || eventtype =="" || eventname==undefined 
            || date==undefined || atttype == undefined || eventtype ==undefined ){
            swal("Uhhh..", "All the four inputs shall be filled!", "error");
        }
        else{
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ eventname: eventname,
                        date: date,
                        eventtype: eventtype,
                        atttype: atttype,
                        calltype: 'eventsave',
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                        setTimeout(function(){swal("Hooray..", "Event added successfully!", "success")},1000);
                        location.reload();
                        //location.href = redirect_url;
                        //console.log(jsondata);
                    },
                        // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors!", "error");
                    }
                });

            })();
        }        
}// close of function eventadd




function ruleadd(){            
    //get all itemcode & quantity pair 
    var title = "",
        weekdata = [],
        day =8,
    
    title=$(".title").val();
    $.each($(".week option:selected"), function(){
        weekid=$(this).data('id')
        weekdata.push(weekid);
    });
    day=$(".day").find(':selected').data('id');
    
    if (title=="" || weekdata.length == 0 || day >6 || title==undefined || weekdata==undefined || day == undefined){
            swal("Uhhh..", "All the three inputs shall be filled!", "error");
    }
    else{
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ title: title,
                        week: JSON.stringify(weekdata),
                        day: day,
                        calltype: 'rulesave',
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                        setTimeout(function(){swal("Hooray..", "Rule added successfully!", "success")},1000);
                        location.reload();
                    },
                        // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors!", "error");
                    }
                });

            })();
    }        
}// close of function eventadd


});