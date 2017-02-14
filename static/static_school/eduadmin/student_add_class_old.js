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
                student_list=jsondata;
                $.each(jsondata, function(){
                    $('.systemkey').append($('<option>',{
                        value: this.fields.id,
                        text: this.fields.key + " " +this.fields.local_id+ " " + this.fields.first_name + " "+this.fields.last_name
                    }));
                    // $('.localkey').append($('<option>',{
                    //     value: this.fields.key,
                    //     text: this.fields.local_id
                    // }));                    
                })
                $(".select").chosen({
                    no_results_text: "Oops, nothing found!",
                    width: "95%"
                });
                $(".btn").attr('disabled', false); 
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Student does not exist", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});





$(".delete").on('click', function() {
    $('.case:checkbox:checked').parents("tr").remove();
    $('.check_all').prop("checked", false); 
    check();

});

$(".addmore").on('click',function(){
    count=$('table tr').length;
    var data="<tr>"+
    "<td><input type='checkbox' class='case'/></td>"+
    "<td><select class='form-control select systemkey'>"+
      "<option disabled selected hidden style='display: none' value>Select system generated key</option>"+
    "</select></td>"+
    "<td><select class='form-control select localkey'>"+
      "<option disabled selected hidden style='display: none' value>Select internal student key</option>"+
    "</select></td>"+
    "<td></td>"+
    "<td></td></tr>";
    $('table').append(data);

    $.each(student_list, function(){
        $('.systemkey').append($('<option>',{
            value: this.fields.key,
            text: this.fields.key + " " + this.fields.first_name + " " +this.fields.last_name
        }));
        $('.localkey').append($('<option>',{
            value: this.fields.key,
            text: this.fields.local_id
        }));                    
    });

    $(".select").chosen({
    no_results_text: "Oops, nothing found!",
    width: "95%"
});
});

function select_all() {
    $('input[class=case]:checkbox').each(function(){ 
        if($('input[class=check_all]:checkbox:checked').length == 0){ 
            $(this).prop("checked", false); 
        } else {
            $(this).prop("checked", true); 
        } 
    });
}

obj=$('table tr').find('span');
$.each( obj, function( key, value ) {
    id=value.id;
    $('#'+id).html(key+1);
});



$('.select').on('change', function() {
  key=this.value;
  var el=this;
  alert(key);
  alert(this);
  $('option:not(:selected)').attr('disabled', true);
})




// $("#student_table").on("focus", ".systemkey", function(){
//     $(this).data("initialText", $(this).val());
//         //alert( "On focus for systemkey called." );
// });
// $("#student_table").on("blur", ".systemkey", function(){
//         //alert( "On blur for table inventory called." );
//     var input = $(this).val();
//     if ($(this).data("initialText") !== $(this).val()) {
//         var el = this;      
//         (function() {
//             $.ajax({
//                 url : "", 
//                 type : "POST", 
//                 data : { item_code: input,
//                     calltype: 'systemkey',
//                     csrfmiddlewaretoken: csrf_token}, // data sent with the post request
//                 dataType: 'json',
//                 // handle a successful response
//                 success : function(jsondata) {  
//                     $(el).closest('tr').find('td:nth-child(1) span').attr("contenteditable",false);
//                     $(el).closest('tr').find('td:nth-child(2) span').val(jsondata['schoolkey'])
//                     $(el).closest('tr').find('td:nth-child(3) span').val(jsondata['first_name'])
//                     $(el).closest('tr').find('td:nth-child(4) span').val(jsondata['last_name'])
//                 },
//                 // handle a non-successful response
//                 error : function() {
//                     bootbox.alert({
//                         message: "Student does not exist", 
//                         onEscape: true }); // provide a bit more info about the error to the user
//                     clearmodal();
//                 }
//             });
//         }());
//     }
// });


});