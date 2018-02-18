$(function(){

transaction_types = ['', 'Debit', 'Credit']

load_journals()

// $('.all').click(function(){
//     load_invoices();
//     page_no+=1;
// });

// $('.apply_reset').click(function(){
//     load_invoices();
// });

function load_journals(){
    account_pk = pk;
    $.ajax({
        url : "/account/journallist/account-list/", 
        type: "GET",
        data:{ calltype:"all_journal",
            account_pk: account_pk},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#journal_table .data").remove();
            $.each(jsondata['object'], function(){
                var url='/account/journalview/'+this.journal__id+'/'
                date=this.journal__date;
                date=date.split("-").reverse().join("-")
                if (this.transaction_type == 1){
                    $('#journal_table').append("<tr class='data' align='center'>"+
                    "<td hidden = 'true'>"+this.id+"</td>"+
                    // "<td class='link' style='text-decoration: underline; cursor: pointer'>"+date+"</td>"+
                    "<td><a href="+url+" class='new_link'>"+date+"</td>"+
                    "<td align='left'>"+transaction_types[this.transaction_type]+"</td>"+
                    "<td>"+this.journal__remarks+"</td>"+
                    "<td>"+this.value+"</td>"+
                    "<td></td>"+
                    "<td><input type='checkbox'></td>"+
                    "<td hidden='true'>"+this.journal__transaction_bill_id+"</td>"+
                    "<td hidden='true'>"+this.journal__id+"</td>"+
                    "</tr>");
                }
                else{
                    $('#journal_table').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    // "<td class='link' style='text-decoration: underline; cursor: pointer'>"+date+"</td>"+
                    "<td><a href="+url+" class='new_link'>"+date+"</td>"+
                    "<td align='right'>"+transaction_types[this.transaction_type]+"</td>"+
                    "<td>"+this.journal__remarks+"</td>"+
                    "<td></td>"+
                    "<td>"+this.value+"</td>"+
                    "<td><input type='checkbox'></td>"+
                    "<td hidden='true'>"+this.journal__transaction_bill_id+"</td>"+
                    "<td hidden='true'>"+this.journal__id+"</td>"+
                    "</tr>");
                }
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch journal data. Kindly try after some time.", "error");
        }
    });
}

$('.deletebtn').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to delete the selected journals?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete the journals!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){delete_data()},600)            
        }
    })
});

function delete_data(){
    var items=[];
    var proceed=true;    
    
    $("#journal_table tr.data").each(function() {
        // console.log(proceed);
        var is_selected = $(this).find('td:nth-child(7) input').is(":checked");
        if (is_selected){
            // console.log("here");
            var entry_pk = $(this).find('td:nth-child(1)').html();
            var trn_bill_no = $(this).find('td:nth-child(8)').html();
            var journal_pk = $(this).find('td:nth-child(9)').html();
            if (isNaN(trn_bill_no) || trn_bill_no == null || trn_bill_no == 'null' || trn_bill_no == undefined || trn_bill_no == 'undefined'){
                $(this).closest('tr').removeClass("has-error");
                var item = {
                    entry_pk : entry_pk,
                    journal_pk: journal_pk
                };
                items.push(item);
            }
            else{
                proceed=false;
                swal({
                    title: "Oops..",
                    text: "Journal entry made against sales/purchase/return/payment/collection cannot be deleted via this option."+
                    " Kindly go to the respective sections to delete them.",
                    type: "error",
                    allowOutsideClick: true,
                    timer:2500,
                });
                $(this).closest('tr').addClass("has-error");
            }
        }
        
    });
    console.log(items)
    if (proceed == true){
        $.ajax({
        url : "/account/journallist/account-list/", 
        type: "POST",
        data:{ calltype:"delete_entries",
            items: JSON.stringify(items),
            csrfmiddlewaretoken: csrf_token},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            swal("Hooray", "Selected journals have been deleted/", "success");
            setTimeout(location.reload(true),1000);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not delte the journal data. Kindly note that you cannot delete any"+
                " journal data related to vendors/customers.", "error");
        }
    });
    }


    
}


});

