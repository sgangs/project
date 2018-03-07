$(function(){

var relation_name = [];

load_relations()

function load_relations(){
    $.ajax({
        url : "/account/relation-list/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            /*$.each(jsondata, function(){*/
                // // url="/account/journallist/account/"+this.id+"/"
                //     $('#payment_mode').append("<tr class='data' align='center'>"+
                //     "<td hidden='true'>"+this.id+"</td>"+
                //     // "<td hidden='true'>"+url+"</td>"+
                //     "<td>"+this.name+"</td>"+
                //     "<td>"+this.payment_account+"</td>"+
                //     "<td>"+this.default+"</td>"+
                //     "</tr>");
                // })

                relation_name = jsondata;

            $.each(relation_name, function(k,v){
                // console.log(k + ' is ' + v);
                $('#relation_list').append($('<option/>',{
                    'data-id': k,
                    'text': v
                }));
                $('#relation_list').selectpicker('refresh')
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch data. Please try again later.", "error");
        }
    });
}

load_related_account()

function load_related_account(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#payment_mode').append("<tr class='data' align='center'>"+
                // "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+relation_name[this.relation]+"</td>"+
                "<td>"+this.account__name+"</td>"+
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
        text: "Are you sure to create/update a account-relation link",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, create/update link!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){register_link()},600)            
        }
    })
});
    
function register_link(){
    var proceed=true;
    relation=$(".relation_list").find(':selected').data('id');
    account=$(".account_list").find(':selected').data('id');

    if (relation == '' || relation =='undefined' || typeof(relation) == undefined 
        || account == '' || account =='undefined' || typeof(account) == undefined){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{relation: relation,
                    account:account,
                    calltype: "account_relation",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Account-Relation Link Updated.", "success");
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
        swal("Oops...", "Please note that relation and account must be selected.", "error");
    }
}

});