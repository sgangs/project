$(function(){

var account_lists=[]

load_groups()

function load_groups(){
    $.ajax({
        url : "/account/journalgroup/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#group').append($('<option>',{
                    'data-id': this.name,
                    'text': this.name
                }));
            });
            $('#group').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in getting journal groups.", "error");
        }
    });
}

load_account()

function load_account(){
    $.ajax({
        url : "/account/account/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            account_lists=jsondata
            console.log(account_lists)
            $.each(account_lists, function(){
                $('#account').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
            });
            // $('#account').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in getting account list.", "error");
        }
    });
}


$('.details').on("mouseenter", ".first", function() {
    $( this ).children( ".delete" ).show();
});

$('.details').on("mouseleave", ".first", function() {
    $( this ).children( ".delete" ).hide();
});

$('.details').on("click", ".delete", function() {
    $(this).parent().parent().remove();
});

$('.addmore').click(function(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
    '<td colspan="1">'+
        '<select class="form-control select trn" id="trn">'+
            '<option disabled selected hidden style=:display: none" value>Select Transaction</option>'+
            '<option data-id=1>Debit</option>'+
            '<option data-id=2>Credit</option>'+
        '</select></td>'+
    '<td colspan="1"><select class="form-control select acct" id="account">'+
        '<option disabled selected hidden style="display: none" value>Select Account</option></select></td>'+
    '<td colspan="1"><input type="number" class="form-control debit" disabled></td>'+
    '<td colspan="1"><input type="number" class="form-control credit" disabled></td>'+
    '</tr>';
    $('.details').append(data);

    // $('#trn').selectpicker('refresh');
    
    $.each(account_lists, function(){
        $('.details').find('tr:eq('+count+')').find('#account').append($('<option>',{
            'data-id': this.id,
            'text': this.name,
        }));
    });
    // $('.unit').selectpicker('refresh');
})

$(".details").on("change", "#trn", function(){
    trn_type=$(this).find(':selected').data('id');
    if (trn_type == 1){
        $(this).closest('tr').find('td:nth-child(4) input').attr('disabled',false);
        $(this).closest('tr').find('td:nth-child(5) input').attr('disabled',true);
        value=$(this).closest('tr').find('td:nth-child(5) input').val();
        $(this).closest('tr').find('td:nth-child(4) input').val(value);
        $(this).closest('tr').find('td:nth-child(5) input').val('');
    }
    else if (trn_type == 2){
        $(this).closest('tr').find('td:nth-child(5) input').attr('disabled',false);
        $(this).closest('tr').find('td:nth-child(4) input').attr('disabled',true);
        value=$(this).closest('tr').find('td:nth-child(4) input').val();
        $(this).closest('tr').find('td:nth-child(5) input').val(value);
        $(this).closest('tr').find('td:nth-child(4) input').val('');
    }
});


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