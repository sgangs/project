$(function(){

load_groups()

function load_groups(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#group').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td class='name'>"+this.name+"</td>"+
                "</tr>");
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No service group exist.", "error");
        }
    });
}


// $("#tax").on("click", ".name", function(){
//     pk=$(this).closest('tr').find('td:nth-child(1)').html()
//     console.log(pk);
//     el=this;
//     var url="individual/"+pk+"/";
//     (function() {
//         $.ajax({
//             url : url, 
//             type: "GET",
//             dataType: 'json',
//             // handle a successful response
//             success : function(jsondata) {
//                 console.log(jsondata);
//             },
//             // handle a non-successful response
//             error : function() {
//                 // console.log("here")
//                 swal("Oops...", "There were some error.", "error");
//             }
//         });
//     }());
// });


var name ='';

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new service group?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new service group!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data()},600)            
        }
    })
});
    
function new_data(){
    var proceed=true;
    var name=$('.newname').val();
    var percentage=parseFloat($('.newpercent').val());
    console.log(name);
    console.log(percentage);
    
    if (name == '' || name =='undefined' || $.trim(name).length < 1){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{name: name,
                    calltype: "newgroup",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New service group added", "success");
                        setTimeout(location.reload(true),1000);
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors! Note, Service Group Names must be unique.", "error");
                }
            });
        }());
    }
    else{
        swal("Oops...", "Please note that name must be filled.", "error");
    }
}

});