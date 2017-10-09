$(function(){

load_modes()

function load_modes(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                // url="/account/journallist/account/"+this.id+"/"
                    $('#payment_mode').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    // "<td hidden='true'>"+url+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.payment_account+"</td>"+
                    "<td>"+this.default+"</td>"+
                    "</tr>");
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch data. Please try again later.", "error");
        }
    });
}


load_accounts()

function load_accounts(){
    $.ajax({
        url : "/account/account/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#account_list').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.name
                        }));
                    $('#account_list').selectpicker('refresh')
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Account list count not be fetched. Please try again later.", "error");
        }
    });
}


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a payment mode",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new payment mode!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_mode()},600)            
        }
    })
});
    
function new_mode(){
    var proceed=true;
    name=$('.name').val()
    account=$(".account_list").find(':selected').data('id');
    is_default = $(".default").is(":checked");

    console.log(account)

    if (name == '' || name =='undefined' || account == '' || account =='undefined' || typeof(account) =='undefined'){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{name: name,
                    account:account,
                    is_default: is_default,
                    calltype: "newmode",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New payment mode added", "success");
                        setTimeout(location.reload(true),1000);
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs.  There were some errors!", "error");
                }
            });
        }());
    }
    else{
        swal("Oops...", "Please note that payment mode name must not be blank and account must be selected.", "error");
    }
}

});