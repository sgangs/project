$(function(){

var class_selected="";
var year="";

//This is called after the class is entered
$( ".class" ).change(function() {
    class_selected=$('.class').find(':selected').data('id');
});

//This is called if month is changed
$( ".year" ).change(function() {
    year=parseInt($('.year').val());    
});

// $(".studenttable").on("click", ".student", function(){
//     st_name=$(this).find('td:nth-child(3)').html();
//     console.log(st_name);
// });

$("#student_table").on("click", ".studentkey",function(){
    student_id=$(this).closest('tr').find('td:nth-child(1)').html();
    // student_id=$(this).find('td:nth-child(1)').html();
    (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ student_id:student_id,
                        year:year,
                        calltype: 'fee_student',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        console.log(jsondata);
                    },
                    // handle a non-successful response
                    error : function() {
                        $('.fee-current').attr('hidden', true);
                        swal("Oops..", "There was an error!", "error");
                    }
                });
            }());
});


$( ".details" ).click(function() {    
    if (class_selected != "" && year !=""){
        //Send ajax function to back-end
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ class_selected: class_selected,
                    year: year,
                    calltype: 'details',
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    $('.fee-current').attr('hidden', false);
                    $(".feetable .data").remove();
                    $.each(jsondata, function(){
                        if (this.data_type=="Generic"){
                            $('.feetable').append("<tr class='data generic'>"+
                            "<td hidden='true'></td>"+
                            "<td>" + this.name + "</td>"+
                            "<td>" + this.month + "</td>"+
                            "<td>" + this.amount + "</td></tr>");
                        }                            
                    });                        
                },
                // handle a non-successful response
                error : function() {
                    $('.fee-current').attr('hidden', true);
                    swal("Oops..", "There was an error!", "error");
                }
            });
        }());
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ class_selected: class_selected,
                    year: year,
                    calltype: 'student',
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    $(".studenttable .data").remove();
                    $.each(jsondata, function(){
                        $('.fee-new').attr('hidden', false);
                        if (this.data_type=="Student"){
                            $('.studenttable').append("<tr class='data student'>"+
                            "<td hidden='true'>"+this.id+"</td>"+
                            "<td class='studentkey'>" + this.key + "</td>"+
                            "<td>" + this.local_id + "</td>"+
                            "<td>" + this.first_name+" "+this.last_name+ "</td>"+
                            "<td><input type='checkbox' class='is_added'/></td></tr>");
                        }                            
                    });                        
                },
                // handle a non-successful response
                error : function() {
                    $('.fee-new').attr('hidden', true);
                    swal("Oops..", "There was an error!", "error");
                }
            });
        }());
    }
    else{
        swal("Bluhh..", "Select Class and enter academic year!", "error");
    }
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo student fee linking!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, fee structure confirmed.",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)
            
        }
    })
});


function reconfirm() {
    swal({
        title: "Please Reconfirm!",
        text: "Reconfirm Fee Structure Linking",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, fee structure linking reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data("saving")},600)            
        }
        else{
            console.log("Not confirmed")
        }
    })
}

function save_data(called_for){
    var proceed=true;
    var items=[]
    var generic_fees=[]
    $("tr.student").each(function() {
        var student_id = $(this).find('td:nth-child(1)').html();
        var is_checked = $(this).find('td:nth-child(5) input').is(":checked");
        if (is_checked){
            var item = {
                student_id : student_id,
            };
        }
        items.push(item);        
    });
    if (items.length <1){
        proceed=false;
    }
    $.each($(".generic_fee_id option:selected"), function(){
        var feeid=$(this).data('id')
        var fee={
            fee_id: feeid
        };
        generic_fees.push(fee);
    });
    if (generic_fees.length <1){
        proceed=false;
    }
    console.log(items);
    console.log(generic_fees);
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ items: JSON.stringify(items),
                    generic_fees: JSON.stringify(generic_fees),
                    year:year,
                    calltype: 'save',
                csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                                        // handle a successful response
                success : function(jsondata) {
                    swal("Hooray..", "Fee structure successfully with students!!", "success");
                    setTimeout(location.reload(true),1200);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors!!", "error");
                }
            });
        }());
    }
    else{
        swal("Oops..", "Select altealst one fee structure and one student", "error");
    }
}

});