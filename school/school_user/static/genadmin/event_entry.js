$(function(){

function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

// page is now ready, initialize the calendar...
$('#calendar').fullCalendar({
// put your options and callbacks here
    customButtons: {
        myCustomButton: {
            text: 'Add Event  ',
                // click: function() {
                //  alert('clicked the add event buton!');
                // }
        }
    },
    header: {
        left: 'myCustomButton',
        center: 'title',
        right: 'prev,next today'
    },
    
})
$.ajax({
        url: "",
        type: "POST",
        data: {csrfmiddlewaretoken: csrf_token,
            calltype: 'event'},
        success: function(jsondata){
            console.log (jsondata)
            var events=[]
            $.each(JSON.parse(jsondata), function(){
                events.push({           
                        title: this.title,
                        start: moment(this.start).format('YYYY/MM/DD hh:mm'), // will be parsed . Error here.
                        allDay: true,})
            });
            // var source = { events: [
            //     $.each(JSON.parse(jsondata), function(){
            //         console.log("Running")
            //         // events.push({
            //         //     title: "Christmas",
            //         //     start: "2016-12-25 00:00:00", // will be parsed
            //         //     allDay: true,
            //         // });
            //         title: "Christmas",
            //         start: "2016-12-25 00:00:00",
            //     })
            // ]};
            var source={events};
            console.log (source);
            $('#calendar').fullCalendar( 'addEventSource', source );
        }
});
$('.fc-myCustomButton-button').append('<i class="glyphicon glyphicon-plus"</i>')
$('.fc-myCustomButton-button').attr('data-toggle',"modal")
$('.fc-myCustomButton-button').attr('data-target',"#myModal")

//This variable will store the student list added via json

$( ".submit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to record the event?',
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
        var eventname=$(".eventname").val();
        var date=$(".date").val();
        //console.log ("Event: "+eventname+" Date:"+date );
        if (eventname=="" || date=="" ){
            bootbox.alert({
                size: "small",
                message: "Event name or date cannot be blank.",
                onEscape: true });
            clearmodal();
        }
        else{
                       
        
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ eventname: eventname,
                        date: date,
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                        alert("Event registered successfully");
                        location.reload();
                        //location.href = redirect_url;
                        //console.log(jsondata);
                    },
                        // handle a non-successful response
                    error : function() {
                        bootbox.alert({
                            size: "medium",
                            message: "Event entry failed", 
                            onEscape: true });
                        clearmodal();
                    }
                });
            })();
        }        
    }, //bracket for confirm closing

});

});