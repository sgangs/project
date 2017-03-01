$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var salary_name="";
var month="";


$(".delete").on('click', function() {
    $('.case:checkbox:checked').parents("tr").remove();
    $('.check_all').prop("checked", false); 
});



$(".addmore").on('click',function(){
    count=$('table tr').length;
    var data="<tr class='data'>"+
    "<td><input type='checkbox' class='case'/></td>"+
    "<td style='text-align: center'><select class='form-control select account'>"+
      "<option disabled selected hidden style='display: none' value>Select Account Name</option>"+
    "</select></td>"+
    "<td style='text-align: center'><input type='text' class='name' placeholder='Eg: Basic Salary' /></td>"+
    "<td style='text-align: center'><input type='number' class='name'/></td>"+
    "<td style='text-align: center'><input type='checkbox' class='name'/></td>"+
    "<td style='text-align: center'><input type='number' class='name'/></td>"+
    "<td style='text-align: center'><input type='checkbox' class='name'/></td>"+
    "<td style='text-align: center'><input type='checkbox' class='name'/></td>"+
    "<td style='text-align: center'><input type='checkbox' class='name'/></td></tr>";
    $('table').append(data);
    
    $.each(accounts, function(){
        $('table').find('tr:eq('+count+')').find('.account').append($('<option>',{
        //$('.account').append($('<option>',{
            'data-id': this.id,
            'text': this.name
        }));
    });
});






//This is called after the fee structure name is entered
$( ".salaryname" ).change(function() {
    salary_name=$(".salaryname").val();
    if (salary_name != ''){
        $( ".submit" ).prop('disabled',false); 
    }
    else{
        $( ".submit" ).prop('disabled',true);     
    }
});
//This is called if month is changed
$( ".month" ).change(function() {
    month=$('.month').find(':selected').data('id');
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$( ".accounthover" ).click(function() {
    console.log("Clicked")
    swal({
        type: "info",
        title: "How To",
        text: "These accounts are those defined under <b> Ledger Group - Salary </b>. If registered account is not available," +
        "that means they were registered under different Leger Group. Register (delete old account, if already created) to continue",
        html: true,
        timer: 15000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});

$('.accountname').change(function(){
    swal({
        type: "warning",
        title: "Statutory Law Alert!",
        text: "Basic Salary needs to have PF structure. Do select 'Use this for PF calculation' accordingly.",
        timer: 15000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo salary structure creation!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, create salary structure!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
});

function save_data(){    
        var items = [];
        var proceed = true;
        var month_entered=true
        salary_name=$(".salaryname").val()
        if ($('.month').is(":visible")){
            if (month ==''){
                month_entered=false
            }
        }
        if (salary_name != "" && month_entered){
            //console.log("Date: "+date);
            $("tr.data").each(function() {
                var account = $(this).find('td:nth-child(2)').find(':selected').data('id');
                var name = parseInt($(this).find('td:nth-child(3) input').val());
                var amount = parseInt($(this).find('td:nth-child(4) input').val());
                var display = $(this).find('td:nth-child(5) input').is(":checked");
                var serial_no = parseInt($(this).find('td:nth-child(6) input').val());
                var affect_pf = $(this).find('td:nth-child(7) input').is(":checked");
                var affect_esi = $(this).find('td:nth-child(8) input').is(":checked");
                var affect_lop = $(this).find('td:nth-child(9) input').is(":checked");
                if (isNaN(amount) || typeof(account) === "undefined" ){
                    proceed=false;}
                if (display){
                    if (isNaN(serial_no) || serial_no<1){
                        proceed=false;
                    }
                }
                var item = {
                    account : account,
                    amount: amount,
                    display: display,
                    serial_no: serial_no,
                    affect_pf: affect_pf,
                    affect_esi: affect_esi,
                    affect_lop: affect_lop
                    };
                items.push(item);        
            });
            console.log(items);
            if (proceed){
        //Send ajax function to back-end 
                (function() {
                    $.ajax({
                        url : "", 
                        type: "POST",
                        data:{ details: JSON.stringify(items),
                            salaryname: salary_name,
                            month:month,
                            csrfmiddlewaretoken: csrf_token},
                            dataType: 'json',               
                            // handle a successful response
                        success : function(jsondata) {
                            // location.href = redirect_url;
                            // console.log("Its cool in here")
                            // console.log(jsondata);
                            swal("Hooray!!", "The salary structure was successfully registered!", "success");
                            setTimeout(function(){location.reload(true);},600)
                        },
                            // handle a non-successful response
                        error : function() {
                            swal("Oops..", "There were some errors!", "error");
                        }
                    });
                }());                
            }
            else{
                swal("Bluhh..", "Select account & enter amount in every row. In case payslip display is selected, enter serial"+ 
                    "number of display in payslip", "error");

            }
        }
        else if (month_entered==false){
            swal("Bluhh..", "Please select the month to repeat!", "error");
        }
        else{
            swal("Bluhh..", "Please enter the name of the fee structure!", "error");
        }
    
}


});