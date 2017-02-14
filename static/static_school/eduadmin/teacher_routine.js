$(function(){

var year='',day=8, teacherid='', year_data=false;

$( ".teacher" ).change(function() {
    teacherid=$('.teacher').find(':selected').data('id');
    $( ".year" ).attr('disabled',false);
    if (year_data){
        get_data()
    }
});




//This function gets called as year is entered.
$( ".year" ).change(function() {
    year = $(this).val();
    get_data()
    if (year > 1960 && year <2050){
        year_data=true;
    }
});

function get_data() {
    $.ajax({
        url : "", 
        type : "POST", 
        data : { year: year,
            teacherid:teacherid,
            calltype: 'year',
            csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) { 
            $(".data").html('');
            $.each(jsondata, function(){
                if (this.data_type=="Period"){
                    $('tr.'+this.period).find('.'+this.day+'').html('<p>'+this.class_section+'<//p><p>'+this.subject+'</p>')
                }
                else if (this.data_type=="Error"){
                    swal("Oops..", this.message, "error");                        
                }
            });
        },
        // handle a non-successful response
        error : function() {
            swal("Oops..", "Please recheck. Data is not available for this year-teacher combination", "error"); 
        }
    });
};

});//end of function load.
