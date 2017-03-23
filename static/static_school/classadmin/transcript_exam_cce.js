$(function(){

$( ".classsection" ).change(function() {
    classsection=parseInt($(".classsection").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { classsection: classsection,
                calltype:'class',
                csrfmiddlewaretoken: csrf_token,}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                $('#student option').remove();
                $('#student').selectpicker('refresh');
                $('#student').append($('<option/option selected hidden style="display: none" value>Select Student</option>'))
                $.each(jsondata, function(){
                    $('#student').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.roll_no+" "+this.first_name+" "+this.last_name
                    }));
                });
                $('#student').selectpicker('refresh')
            },
            // handle a non-successful response
            error : function() {
                
            }
        });
    }());
    
});

$( "#student" ).change(function() {
    student=parseInt($("#student").find(':selected').data('id'));
    console.log(student);
    
});


$('.submit').click(function() {
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { classsection: classsection,
                student: student,
                calltype:'student',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                $("#student_table .data").remove();
                $.each(jsondata, function(){
                    if (this.data_type=="Subject"){
                        $('#student_table').append($('<tr class="data '+this.name+'">'+
                            '<td class="name">'+this.name+'</td>'+'<td class="FA1"></td>'+'<td class="FA2"></td>'+
                            '<td class=SA1></td>'+'<td class=FA3></td>'+'<td class=FA4></td>'+'<td class=SA2></td>'+
                            '<td class=OFA></td>'+'<td class=OSA></td>'+'<td class=OG></td>'+'<td class=GP></td></tr>'
                            ));
                    }            
                    else if (this.data_type=="Exam"){
                        $('tr.'+this.subject).find('.'+this.name+'').html('<p>'+this.grade+'</p>')
                    }
                });
            },
            // handle a non-successful response
            error : function() {
                
            }
        });
    }());
});


});