$(function(){

load_accounts()

function load_accounts(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#account').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td>"+this.name+"</td>"+
                    "<td>"+this.key+"</td>"+
                    "<td>"+this.type+"</td>"+
                    "<td>"+this.debit+"</td>"+
                    "<td>"+this.credit+"</td>"+
                    "</tr>");
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No account exist.", "error");
        }
    });
}

load_ledgers()

function load_ledgers(){
    $.ajax({
        url : "/account/ledgergroup/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#ledger').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.name
                        }));
                    $('#ledger').selectpicker('refresh')
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No ledger group exist.", "error");
        }
    });
}

load_acct_type()

function load_acct_type(){
    $.ajax({
        url : "/account/getaccounttype/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            $.each(jsondata, function(){
                $('#type').append($('<option/>',{
                    'data-id': this[0],
                    'text': this[1]
                }));
                $('#type').selectpicker('refresh')
            });
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No ledger group exist.", "error");
        }
    });
}


// var name ='', key='', details ='';


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
    var name=$('.name').val()
    if (name == '' || name =='undefined'){
        proceed = false;
        swal("Oops...", "Please enter account name", "error");
    }
    var key=$('.key').val()
    if (key == '' || key =='undefined'){
        proceed = false;
        swal("Oops...", "Please enter account key", "error");
    }
    var ledger = $('.ledger').find(':selected').data('id');
    if (ledger == '' || ledger =='undefined'){
        proceed = false;
        swal("Oops...", "Please select a ledger group", "error");
    }
    var account_type = $('.type').find(':selected').data('id');
    if (account_type == '' || account_type =='undefined'){
        proceed = false;
        swal("Oops...", "Please select the type of account", "error");
    }
    var remarks=$('.remarks').val()

    var opendebit=$('.opendebit').val()
    var opencredit=$('.opencredit').val()
    var debit=$('.debit').val()
    var credit=$('.credit').val() 
    
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{name: name,
                    key: key,
                    ledger: ledger,
                    account_type: account_type,
                    remarks: remarks,
                    opendebit: opendebit,
                    opencredit: opencredit,
                    debit:debit,
                    credit:credit,
                    calltype: "newtax",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New account added", "success");
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
}

});