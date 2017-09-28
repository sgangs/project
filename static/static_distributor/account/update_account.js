$(function(){

load_account()

load_accountyear()

function load_account(){
    $.ajax({
        url : "/account/account/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#account').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            $('#account').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in getting account list.", "error");
        }
    });
}

function load_accountyear(){
    $.ajax({
        url : "/account/accountperiod/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                if (this.is_first_year == true){
                    open_date=this.start.split("-").reverse().join("/")
                    end_date=this.end.split("-").reverse().join("/")
                    $('.open_year').html(open_date+" : "+end_date)
                    $('.open_year_id').html(this.id)

                }
            });
            $('#account').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in getting account list.", "error");
        }
    });
}


$('.account').on('change', function() {
    accountid=$('.account').find(':selected').data('id')
    account_period=$('.open_year_id').html()

    $.ajax({
        url : "/account/account-accountyear/data/", 
        type: "GET",
        data:{accountid: accountid,
            account_period: account_period },
        dataType: 'json',
        // beforeSend: function(){
        //     $('#loadingdetails').modal('show');
        // },
        // handle a successful response
        success : function(jsondata) {
            // $('#loadingdetails').modal('hide');
            $('.open_debit_record').html(jsondata[0]['opening_debit'])
            $('.open_credit_record').html(jsondata[0]['opening_credit'])
            $('.debit').attr('disabled', false);
            $('.credit').attr('disabled', false);       
        },
        // handle a non-successful response
        error : function() {
            // $('#loadingdetails').modal('hide');
            swal("Oops...", "No customer data exist.", "error");
        }
    });
})





$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to register the journal entry?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, register journal entry!",
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
    var items=[], total_debit=0, total_credit=0, proceed=true;
    groupname=$('#group').find(':selected').data('id');
    remarks=$('.remarks').val();
    date=$('.date').val();

    
    if (groupname == '' || groupname =='undefined' || typeof(groupname) == 'undefined' || date == '' || typeof(date) == 'undefined'
        || date =='undefined'){
        proceed = false;
        console.log("here");
        swal({
            title: "Oops..",
            text: "Please select a journal group and enter date.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });
    }
    $(".details tr.data").each(function() {
        var trn_type=$(this).find('td:nth-child(2) :selected').data('id');
        var accountid=$(this).find('td:nth-child(3) :selected').data('id');
        if (isNaN(accountid) || accountid<=0 || accountid=='undefined' || typeof(accountid) == 'undefined' ){
            proceed=false;
            console.log("here");
            swal({
                title: "Oops..",
                text: "Please select an account.",
                type: "error",
                allowOutsideClick: true,
                timer:2500,
            });
            $(this).closest('tr').addClass("has-error");    
        }

        if (trn_type == 1){
            var value = parseFloat($(this).find('td:nth-child(4) input').val());
            total_debit+=value
            if (isNaN(value) || value<=0){
                proceed=false;
                console.log("here");
                swal({
                    title: "Oops..",
                    text: "Debit must be a positive number.",
                    type: "error",
                    allowOutsideClick: true,
                    timer:2500,
                });
                $(this).closest('tr').addClass("has-error");    
            }
            else{
                $(this).closest('tr').removeClass("has-error");   
            }
        }
        else if (trn_type == 2){
            var value = parseFloat($(this).find('td:nth-child(5) input').val());
            console.log(value);
            total_credit+=value
            if (isNaN(value) || value<=0){
                proceed=false;
                console.log("here");
                swal({
                    title: "Oops..",
                    text: "Credit must be a positive number.",
                    type: "error",
                    allowOutsideClick: true,
                    timer:2500,
                });
                $(this).closest('tr').addClass("has-error");    
            }
            else{
                $(this).closest('tr').removeClass("has-error");   
            }
        }
        var item = {
            trn_type : trn_type,
            accountid : accountid,
            value : value,
        };
        items.push(item);
    });
    console.log(items);
    
    if (total_debit != total_credit){
        proceed=false;
        console.log("here");
        swal({
            title: "Oops..",
            text: "Total debit value must be equal to total creidt value.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });
    }
    if (total_debit == 0 || total_credit == 0){
        console.log(total_debit);
        console.log(total_credit);
        proceed=false;
        console.log("here");
        swal({
            title: "Oops..",
            text: "Debit and credit value must both be equal and greater than zero.",
            type: "error",
            allowOutsideClick: true,
            timer:2500,
        });
    }
    console.log(proceed);
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{groupname: groupname,
                    remarks:remarks,
                    date:date.split("/").reverse().join("-"),
                    entries: JSON.stringify(items),
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New customer added", "success");
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