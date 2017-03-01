$(function(){

var year="";

$(".delete").on('click', function() {
    $('.case:checkbox:checked').parents("tr").remove();
    $('.check_all').prop("checked", false); 
});

$(".addmore").on('click',function(){
    count=$('table tr').length;
    var data="<tr class='data'>"+
    "<td><input type='checkbox' class='case'/></td>"+
    "<td style='text-align: center'><select class='form-control select cadre'>"+
      "<option disabled selected hidden style='display: none' value>Select Employee Cadre</option>"+
    "</select></td>"+
    "<td style='text-align: center'><select class='form-control select leave'>"+
      "<option disabled selected hidden style='display: none' value>Select Leave Type</option>"+
    "</select></td>"+
    "<td style='text-align: center'><input type='number' class='numbers'/></td>"+"</tr>";
    $('table').append(data);
    
    $.each(cadres, function(){
        $('table').find('tr:eq('+count+')').find('.cadre').append($('<option>',{
            'data-id': this.id,
            'text': this.name
        }));
    });
    $.each(leaves, function(){
        $('table').find('tr:eq('+count+')').find('.leave').append($('<option>',{
            'data-id': this.id,
            'text': this.name
        }));
    });
});

$( ".year" ).change(function() {
    year=$(".year").val();
});

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo cadre-leave linking!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, link cadre-leave!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)
        }
    })
});

function save_data(){
    var items = [];
    var proceed = true;
    var numbers_entered=true
    fee_name=$(".feename").val();
    $("tr.data").each(function() {
        var cadreid = $(this).find('td:nth-child(2)').find(':selected').data('id');
        var leaveid = $(this).find('td:nth-child(3)').find(':selected').data('id');
        var numbers = parseInt($(this).find('td:nth-child(4) input').val());
        if (isNaN(numbers) || typeof(cadreid) === "undefined" || typeof(leaveid) === "undefined" ){
            proceed=false;}
        var item = {
            cadreid : cadreid,
            leaveid: leaveid,
            numbers: numbers,
        };
        items.push(item);        
    });
    if (year == "" || year == undefined){
        proceed=false}
    // console.log(items);
    if (proceed){
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details: JSON.stringify(items),
                    year: year,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    swal("Hooray..", "Fees payment registered successfully!!", "success");
                    setTimeout(location.reload(true),900)
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors. Recheck your input data while we check behind the curtains", "error");
                }
            });
        }());
    }
    else{
        swal("Oops..", "Check if all entry were correct. Year cannot be blank. Delete table rows, but don't keep blank rows", "error");
    }
} 
});