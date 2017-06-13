$(function(){

load_customers()

function load_customers(){
    $.ajax({
        url : "getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#tax').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='name'>"+this.name+"</td>"+
                    "<td>"+this.percentage+"%"+"</td>"+
                    "</tr>");
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No tax structure exist.", "error");
        }
    });
}


$("#tax").on("click", ".name", function(){
    pk=$(this).closest('tr').find('td:nth-child(1)').html()
    console.log(pk);
    el=this;
    url="individual/"+pk+"/"
    (function() {
        $.ajax({
            url : url, 
            type: "GET",
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                console.log(jsondata);
            },
            // handle a non-successful response
            error : function() {
                console.log("here")
                swal("Oops...", "There were some error.", "error");
            }
        });
    }());
});



var name ='', key='', details ='';

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new tax structure?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new tax structure!",
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
    name=$('.name').val()
    percentage=$('.percent').val()
    
    if (name == '' || name =='undefined' || percentage == '' || percentage =='undefined' || isNaN(percentage)){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: name,
                    percentage:percentage,
                    calltype: "newtax",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New tax structure added", "success");
                        setTimeout(location.reload(true),1000);
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
    else{
        swal("Oops...", "Please note that name & percentage must be filled.", "error");
    }
}

});