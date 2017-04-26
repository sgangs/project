$(function(){

var student_roll={},student_name={}, class_name='';

$( ".classsection" ).change(function() {
    classsection=parseInt($(".classsection").find(':selected').data('id'));
    class_name=$(".classsection").find(':selected').val();
    console.log(class_name)
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
                    student_roll[this.id]=this.roll_no
                    student_name[this.id]=this.first_name+" "+this.last_name
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
                $('.details').attr('hidden',true);
                $('.report').attr('hidden',false);
                exam_array=[]
                $('.name').append($('<label class=metadata>'+student_name[student]+'</label>'));
                $('.roll').append($('<label class=metadata>'+student_roll[student]+'</label>'));
                $('.class').append($('<label class=metadata>'+class_name+'</label>'));
                $.each(jsondata, function(){
                    if (this.data_type=="Exam Name"){
                        exam_array.push(this.id)
                        $('#header').append($('<td class='+this.id+'>'+this.name+'</td>'));
                    }
                })
                $.each(jsondata, function(){
                    if (this.data_type=="Subject"){
                        $('#student_table').append($('<tr class="data '+this.id+'">'+
                            '<td class="name">'+this.name+'</td></tr>'
                            ));
                        for (var i=0; i<exam_array.length; i++){
                            $('.'+this.id+'').append($('<td class='+exam_array[i]+'></td>'))
                        }
                    }
                    else if (this.data_type=="Exam Report"){
                        $('tr.'+this.subject_id).find('.'+this.exam_id+'').html('<p>'+this.marks+'</p>')
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