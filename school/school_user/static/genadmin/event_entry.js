$(function(){

// page is now ready, initialize the calendar...
$('#calendar').fullCalendar({
// put your options and callbacks here
    header: {
        left: 'myCustomButton',
        center: 'title',
        right: 'prev,next, month, agendaWeek, today',        
    },
    // dayClick: function(date, jsEvent, view) {
    //     alert('Clicked on: ' + date.format());
    // },
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
                    if (this.event_type == 1){
                        events.push({           
                                title: this.title,
                                id: this.id,
                                color: '#ea4d62',
                                start: moment(this.start).format('YYYY/MM/DD hh:mm'), // will be parsed . Error here.
                                end: moment(this.start).format('YYYY/MM/DD hh:mm'),
                                allDay: true,                                
                                })
                    }
                    else if (this.event_type == 2){
                        events.push({           
                                title: this.title,
                                id: this.id,
                                color: '#96bc6b',
                                start: moment(this.start).format('YYYY/MM/DD hh:mm'), // will be parsed . Error here.
                                end: moment(this.start).format('YYYY/MM/DD hh:mm'),
                                allDay: true,                                
                                })
                    }
                    else if (this.event_type == "Weekly"){
                        events.push({           
                                title: this.title,
                                color: '#9b000c',
                                start: moment(this.start).format('YYYY/MM/DD hh:mm'), // will be parsed . Error here.
                                end: moment(this.start).format('YYYY/MM/DD hh:mm'),
                                allDay: true,    
                                })
                    }
                    else{
                        events.push({           
                                title: this.title,                                
                                id: this.id,
                                start: moment(this.start).format('YYYY/MM/DD hh:mm'), // will be parsed . Error here.
                                end: moment(this.start).format('YYYY/MM/DD hh:mm'),
                                allDay: true,
                                })
                    }
                });
                callback(events)
            }
        });
    },    
    eventRender: function(event, element) {
        element.prop('title', event.title);
    },
    eventClick: function(calEvent) {
        // alert('Event: ' + calEvent.title);
        swal({
        title: "Want to delete?",
        text: "Please confirm if you want to delete the event: <p><b>" + calEvent.title+"<b><p>",
        type: "warning",
        showCancelButton: true,
        // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete event!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            // $('#calendar').fullCalendar('removeEvents', calEvent._id);
            setTimeout(function(){delete_event(calEvent.id, calEvent.start)},600)
            
        }
    })
    }
})

function delete_event(event_id, start){
    var proceed = true;        
    var items = [];    
    var curDate=new Date();
    var startDate=new Date(start);
    if (curDate>=startDate){
        proceed=false;
    }

    // console.log(event_id);
    if (proceed){
    //Send ajax function to back-end 
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ event_id:event_id,
                calltype: 'delete',
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
                // location.href = redirect_url;
                // console.log(jsondata);
                swal("Hooray..", "Event deleted successfully.", "success");
                $('#calendar').fullCalendar('removeEvents', event_id);
            },
            // handle a non-successful response
            error : function() {
                swal("Oops..", "There were some errors. Note you cannot delete event rules from here.", "error");                            
            }
        });
    }());    
    }
    else{
        swal("Bluhhh..", "You cannot delete events of previous dates.", "error");
    }
}



// $('.fc-myCustomButton-button').append('<i class="glyphicon glyphicon-plus"</i>')
$('.event').attr('data-toggle',"modal")
$('.event').attr('data-target',"#event")

$('.annualrule').attr('data-toggle',"modal")
$('.annualrule').attr('data-target',"#annualrule")


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
    console.log(eventtype);
    atttype=$("#attendance").find(':selected').data('id');
    console.log(atttype);
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
                        // location.reload();
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