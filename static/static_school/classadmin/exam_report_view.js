$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var classid=1;
var examid=1;


//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

//This is called after the class option is selected
$( ".classsection" ).change(function() {
    classid=parseInt($(".classsection").find(':selected').data('id'));
    $( ".classsection" ).prop('disabled',true); 
    $( ".exam" ).prop('disabled',false);
});


//This function gets called as exam is entered.
$( ".exam" ).change(function() {
    examid =parseInt($(".exam").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { examid: examid,
                classid: classid,
                calltype: 'details',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                $('.subjectdiv').attr('hidden', false);
                $('.exam').attr('disabled', true);
                $.each(jsondata, function(){
                    if (this.data_type=="Subject"){
                        $('.subject').append($('<option>',{
                            'data-id': this.id,
                            'text': this.name
                        }));
                    }
                })
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and exam combination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});

//This is called when subject is entered.
$( ".subject" ).change(function() {
    subjectid =parseInt($(".subject").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { examid: examid,
                classid: classid,
                subjectid: subjectid,
                calltype: 'subject',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                var i=0;
                var score=[];
                var internal=[];
                var external=[];
                var name=[];
                var average=[];
                $.each(jsondata, function(){
                    if (this.data_type=="Report w ext"){
                        score[i]=this. score;
                        internal[i]=this.internal;
                        external[i]=this.external;
                        name[i]=this.first_name+" "+this.last_name;
                        average[i]=this.average;
                        i++;
                    }
                    if (this.data_type=="Report w.o. ext"){
                        score[i]=this. score;
                        internal[i]=this.internal;
                        external[i]=0;
                        name[i]=this.first_name+" "+this.last_name;
                        average[i]=this.average;
                        i++;
                    }
                })
                draw_graph(name, internal, external, score, average);
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and exam combination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});


function draw_graph(name, internal, external, score, average){
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: name,
            datasets: [{
                label: 'Final Score',
                type: 'bar',
                data: score,
                backgroundColor: "rgba(255, 99, 132, 0.4)",
                borderColor: "rgba(255,99,132,1)",
                borderWidth: 1
                },
                {
                label: 'Internal Score',
                type: 'bar',
                data: internal,
                backgroundColor: "rgba(54, 162, 235, 0.4)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
                },
                {
                label: 'External Score',
                type: 'bar',
                data: external,
                backgroundColor: "rgba(255, 206, 86, 0.4)",
                borderColor: "rgba(255, 206, 86, 1)",
                borderWidth: 1
                },
                {
                type: 'line',
                fill: false,
                label: 'Class Average',
                backgroundColor: "rgba(0, 0, 10, 0.4)",
                borderColor: "rgba(0, 0, 10, 0.4)",
                data: average,
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Subject Wise Exam Report'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });

}


});