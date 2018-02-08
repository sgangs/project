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
                url="/account/journallist/account/"+this.id+"/"
                    $('#account').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td hidden='true'>"+url+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.name+"</td>"+
                    "<td>"+this.key+"</td>"+
                    "<td>"+this.type+"</td>"+
                    "<td>"+this.debit+"</td>"+
                    "<td>"+this.credit+"</td>"+
                    "</tr>");

                $('#account_opening_update').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
                $('#account_opening_update').selectpicker('refresh');
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could note fetch account list. Kindly try later.", "error");
        }
    });
}

load_account_year()

function load_account_year(){
    $.ajax({
        url : "/account/accountperiod/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                start_date = this.start.split("-").reverse().join("-")
                end_date = this.end.split("-").reverse().join("-")
                $('#year_opening_update').append($('<option>',{
                    'data-id': this.id,
                    'text': start_date + " to " + end_date
                }));
                $('#year_opening_update').selectpicker('refresh');
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could note fetch account period list. Kindly try later.", "error");
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

$("#account").on("click", ".link", function(){
    url=$(this).closest('tr').find('td:nth-child(2)').html();
    window.location = url;
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new account?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new account!",
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
                    calltype: "newaccount",
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

$('.register_update_opening').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to update opening balance for selected accountd?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add update opening balance!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){update_opening()},600)
        }
    })
});
    
function update_opening(){
    var proceed = true;

    var account_id = $('.account_opening_update').find(':selected').data('id');
    if (account_id == '' || account_id =='undefined' || account_id == undefined){
        proceed = false;
        swal("Oops...", "Please select an account.", "error");
    }
    var period_id = $('.year_opening_update').find(':selected').data('id');
    if (period_id == '' || period_id =='undefined' || period_id == undefined){
        proceed = false;
        swal("Oops...", "Please select an accounting year", "error");
    }
    
    var opendebit=$('.opendebit_update').val()
    var opencredit=$('.opencredit_update').val()
        
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{account_id: account_id,
                    period_id: period_id,
                    opendebit: opendebit,
                    opencredit: opencredit,
                    calltype: "update_opening",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Opening balance Updated", "success");
                        setTimeout(location.reload(true),1000);
                    }
                },
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    }
}

});