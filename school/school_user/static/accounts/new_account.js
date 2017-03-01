$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}


//This is for the reset button to work
// $( ".reset" ).click(function() {
//     location.reload(true);
// });
var ledger = '';
var account_name = '';
var remarks ='';
var key ='';
var acct_type ='';
var sub_acct_type ='';
var period = '';
var bal_type ='';
var balance =0;
var accountnameproceed = true;
var keyproceed = true;

$( ".ledgergroup" ).change(function(){
    ledger=parseInt($(".ledgergroup").find(':selected').data('id'));
    $('.ledgergroupdiv').removeClass('has-error');
});

$( ".accountname" ).change(function(){
    account_name=$(".accountname").val();
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { account_name: account_name,
                calltype: 'account',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                if (jsondata['error'] == "Account with same name already exist."){
                    $(".accountnamediv").removeClass('has-success');
                    $(".accountnamediv").addClass('has-error');
                    bootbox.alert({
                        size: "medium",
                        message: jsondata['error'],
                        onEscape: true });
                    clearmodal();
                    accountnameproceed = false;
                }
                else{
                    accountnameproceed = true;
                    $(".accountnamediv").addClass('has-success');
                    $('.accountnamediv').removeClass('has-error');
                }
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Account name already exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
                accountnameproceed = true;
                $(".accountnamediv").addClass('has-success');
                $('.accountnamediv').removeClass('has-error');
            }
        });
    }());
});

$( ".remarks" ).change(function(){
    remarks=$(".remarks").val();
});

$( ".key" ).change(function(){
    key=$(".key").val();
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { key: key,
                calltype: 'key',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                if (jsondata['error'] == "Account with same key already exist."){
                    $(".keydiv").removeClass('has-success');
                    $(".keydiv").addClass('has-error');
                    bootbox.alert({
                        size: "medium",
                        message: jsondata['error'],
                        onEscape: true });
                    clearmodal();
                    keyproceed = false;
                }
                else{
                    keyproceed = true;   
                    $('.keydiv').removeClass('has-error');
                    $(".keydiv").addClass('has-success');
                }
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Account name already exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
                keyproceed = true;
                $(".keydiv").addClass('has-success');
                $('.accountnamediv').removeClass('has-error');
            }
        });
    }());
});

$( ".accounttype" ).change(function(){
    acct_type=$(".accounttype").find(':selected').data('id');
    $('.accounttypediv').removeClass('has-error');
    $(".subaccounttype").attr('disabled', false);
    if (acct_type == "Current Assets" || acct_type == "Long Term Assets" || acct_type == "Direct Expense" 
        || acct_type =="Indirect Expense"){
        $(".balancetype").val("Debit balance");
        // $('.balancetype" option[value="Debit Balance"]').attr("selected","selected");
    }
    else{
        $(".balancetype").val("Credit balance");
    }

    //This is used to check sub account via-a-vis  account type
    if (acct_type =="Current Liabilities"){
        if (sub_acct_type == 'PFERE' || sub_acct_type == 'ESERE'){
            $('.subaccounttypediv').addClass('has-error');
            $('.subaccount-p').attr('hidden', false);
            $('.subaccount-p').addClass('has-error');
            $('.submit').attr('disabled', true);
        }
        else{
            $('.subaccounttypediv').removeClass('has-error');
            $('.subaccount-p').attr('hidden', true);
            $('.submit').attr('disabled', false);
        }        
    }
    else if (acct_type =="Direct Expense" || acct_type == "Indirect Expense"){
        if (sub_acct_type == 'PFEEL' || sub_acct_type == 'PFERL' || sub_acct_type == 'ESEEL' || sub_acct_type == 'ESERL'){
            console.log("Error here");
            $('.subaccounttypediv').addClass('has-error');
            $('.subaccount-p').attr('hidden', false);   
            $('.subaccount-p').addClass('has-error');
            $('.submit').attr('disabled', true);
        }
        else{
            $('.subaccounttypediv').removeClass('has-error');
            $('.subaccount-p').attr('hidden', true);
            $('.submit').attr('disabled', false);
        }
    }
    else{
        if (sub_acct_type != '' && sub_acct_type != 'None' && sub_acct_type != 'undefined'){
            $('.subaccounttypediv').addClass('has-error');
            $('.subaccount-p').attr('hidden', false);
            $('.subaccount-p').addClass('has-error');
            $('.submit').attr('disabled', true);
        }
        else{
            $('.subaccounttypediv').removeClass('has-error');
            $('.subaccount-p').attr('hidden', true);
            $('.submit').attr('disabled', false);
        }
    }
});

$( ".subaccounttype" ).change(function(){
    sub_acct_type=$(".subaccounttype").find(':selected').data('id');
    $('.subaccounttypediv').removeClass('has-error');
    $('.subaccount-p').attr('hidden', true);

    //This is used to check sub account via-a-vis  account type
    if (acct_type =="Current Liabilities"){
        if (sub_acct_type == 'PFERE' || sub_acct_type == 'ESERE'){
            $('.subaccounttypediv').addClass('has-error');
            $('.subaccount-p').attr('hidden', false);
            $('.subaccount-p').addClass('has-error');
            $('.submit').attr('disabled', true);
        }
        else{
            $('.subaccounttypediv').removeClass('has-error');
            $('.subaccount-p').attr('hidden', true);
            $('.submit').attr('disabled', false);
        }        
    }
    else if (acct_type =="Direct Expense" || acct_type == "Indirect Expense"){
        if (sub_acct_type == 'PFEEL' || sub_acct_type == 'PFERL' || sub_acct_type == 'ESEEL' || sub_acct_type == 'ESERL'){
            $('.subaccounttypediv').addClass('has-error');
            $('.subaccount-p').attr('hidden', false);   
            $('.subaccount-p').addClass('has-error');
            $('.submit').attr('disabled', true);
        }
        else{
            $('.subaccounttypediv').removeClass('has-error');
            $('.subaccount-p').attr('hidden', true);
            $('.submit').attr('disabled', false);
        }
    }
    else{
        if (sub_acct_type != '' && sub_acct_type != 'None' && sub_acct_type != 'undefined'){
            $('.subaccounttypediv').addClass('has-error');
            $('.subaccount-p').attr('hidden', false);
            $('.subaccount-p').addClass('has-error');
            $('.submit').attr('disabled', true);
        }
        else{
            $('.subaccounttypediv').removeClass('has-error');
            $('.subaccount-p').attr('hidden', true);
            $('.submit').attr('disabled', false);
        }
    }
});

$( ".accountingperiod" ).change(function(){
    period=$(".accountingperiod").find(':selected').data('id');
    $('.accountingperioddiv').removeClass('has-error');
});

$( ".balancetype" ).change(function(){
    bal_type=$(".balancetype").find(':selected').data('id');
});

$( ".balance" ).change(function(){
    balance=Math.abs(parseFloat($(".balance").val()));
});

$( ".submit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to record the journal entry?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
        var blank=false;
        $('.error').remove();
        if (sub_acct_type == 'undefined' || sub_acct_type == 'None'){
            sub_acct_type = '';
        }
        bal_type=$(".balancetype").find(':selected').data('id');
        //get all the input details
        if (ledger == ''){
            blank=true
            $('.ledgergroupdiv').addClass('has-error');
        }
        if (account_name == ''){
            blank=true
            $('.accountnamediv').addClass('has-error');
        }
        if (key == ''){
            blank=true
            $('.keydiv').addClass('has-error');
        }
        if (acct_type == ''){
            blank=true
            $('.accounttypediv').addClass('has-error');
        }
        if (period == ''){
            blank=true
            $('.accountingperioddiv').addClass('has-error');
        }

        if ( !blank && accountnameproceed && keyproceed){
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ ledgerid: ledger,
                        name: account_name,
                        remarks: remarks,
                        key: key,
                        acct_type: acct_type,
                        sub_acct_type: sub_acct_type,
                        periodid: period,
                        balancetype: bal_type,
                        balance: balance,
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                    success : function(jsondata) {
                        alert("Entry registered successfully");
                        location.href = redirect_url;
                            //console.log(jsondata);
                    },
                    // handle a non-successful response
                    error : function() {
                        bootbox.alert({
                            size: "medium",
                            message: "Account entry failed", 
                            onEscape: true });
                        clearmodal();
                    }
                });
            }()); //end of ajax function call
        }
        else{
            if ( !keyproceed ){
                // bootbox.alert({
                //     size: "large",
                //     message: "Account with same key exist. ", 
                //     onEscape: true });
                // clearmodal();
                $('.alert').prop('hidden',false);
                $('.alert').append("<p class='error'><strong>Oh snap!</strong> Account with same key exist.</p>");
            }
            if (!accountnameproceed) {
                // bootbox.alert({
                //     size: "large",
                //     message: "Account with same name exist. ", 
                //     onEscape: true });
                // clearmodal();
                $('.alert').prop('hidden',false);
                $('.alert').append("<p class='error'><strong>Oh snap!</strong> Account with same name exist.</p>");
            }
            if(blank){
                // bootbox.alert({
                //     size: "large",
                //     message: "All items marked * should be filled.", 
                //     onEscape: true });
                // clearmodal();
                $('.alert').prop('hidden',false);
                $('.alert').append("<p class='error'><strong>Oh snap!</strong> All items marked * should be filled.</p>");
            }
        }
                
    }, //bracket for confirm closing
});




});