$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.

var year="";
var month="";
var staffid=0;
var gross=0;
var net=0;
var employee=0;
var employer=0;

//This is called if month is changed
$( ".month" ).change(function() {
    month=$('.month').find(':selected').data('id');
});

$( ".year" ).change(function() {
    year=$(".year").val();
});

$( ".staff" ).change(function() {
    staffid=$('.staff').find(':selected').data('id');
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$('.submit').click(function(e) {
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ staffid: staffid,
                call_type:'generate',
                month:month,
                year:year,
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
            // location.href = redirect_url;
                if (jsondata =='Report Already Generated'){
                    swal("Slow Down!!", "Payslip for staff for given month is already generated!", "info");
                    setTimeout(function(){location.reload(true);},2500);  
                }
                else{
                    swal("Hooray!!", "The salary structure was successfully generated!", "success");
                    $('.staff-select').attr('hidden', true);
                    salaryCount=0
                    deductionCount=0
                    $('.salary_generated').attr('hidden',false);
                    $('.salary_metadata').attr('hidden',false);
                    $('.buttons').attr('hidden', false);
                    $('.personal_metadata').attr('hidden',false);
                    $('.personal').append("<div><label>Name: "+jsondata['Personal'].name+
                    "</label></div><div><label>Staff ID: "+jsondata['Personal'].id+
                    "</label></div><div><label class='net'>Net Payable: Rs. " +jsondata['Salary'].net+ "</label></div>");
                    $.each(jsondata, function(){
                        if (this.data_type=="Monthly"){
                            salaryCount=salaryCount++
                            gross+=parseInt(this.amount);
                            net+=parseInt(this.amount);
                            $('.salary_employee').append("<tr class='data monthly' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'>" + this.name + "</td>"+
                            "<td style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.amount+"></td></tr>");
                        }
                        else if (this.data_type=="Yearly"){
                            salaryCount=salaryCount++
                            gross+=parseInt(this.amount);
                            net+=parseInt(this.amount);
                            $('.deduction_employee').append("<tr class='data yearly' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'>" + this.name + "</td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.amount+"></td></tr>");
                        }
                        else if (this.data_type=="ESI Employee"){
                            deductionCount++;
                            net-=parseInt(this.amount);
                            employee+=parseInt(this.amount);
                            $('.deduction_employee').append("<tr class='data esi' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'>" + this.name + "</td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.amount+"></td></tr>");
                        }
                        else if (this.data_type=="EPF Employee"){
                            deductionCount++;
                            net-=parseInt(this.amount);
                            employee+=parseInt(this.amount);
                            $('.deduction_employee').append("<tr class='data epf' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'>" + this.name + "</td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.amount+"></td></tr>");
                        }
                    });
                    if (salaryCount > deductionCount){
                        for (var i=1; i<(salaryCount-deductionCount); i++){
                            $('.deduction_employee').append("<tr class='data deduction' style='height:40px;'>"+
                            "<td hidden='true'></td><td></td><td></td></tr>");
                        }
                    }
                    else{
                        for (var i=1; i<(deductionCount-salaryCount); i++){
                            $('.salary_employee').append("<tr class='data deduction' style='height:40px;'>"+
                            "<td hidden='true'></td><td></td><td></td></tr>");
                        }
                    }
                    $.each(jsondata, function(){
                        if (this.data_type=="Salary"){
                            $('.salary_employee').append("<tr class='data salary'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'><b>Gross Earning</b></td>"+
                            "<td style='height:20px;'>" + this.gross + "</td></tr>");
                            $('.deduction_employee').append("<tr class='data deduction'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'><b>Total Deduction</b></td>"+
                            "<td  style='height:20px;'>" + this.employee + "</td></tr>");
                            // $('.attribute').append("<tr class='data net'>"+
                            // "<td style='height:20px;'><b>Net Payable</b></td>"+
                            // "<td  style='height:20px;'>" + this.net + "</td></tr>");
                        }
                    });
                    $.each(jsondata, function(){
                        if (this.data_type=="EPS-EPF"){
                            employer+=parseInt(this.epf_value);
                            $('.employer').attr('hidden', false);
                            $('.employer_table').append("<tr class='data epf_employer' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'> Employer EPF Contribution </td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.epf_value+"></td></tr>");
                            if (this.eps_value>0){
                                employer+=parseInt(this.eps_value);
                                $('.employer_table').append("<tr class='data eps_employer' style='height:40px;'>"+
                                "<td hidden='true'></td>"+
                                "<td style='height:20px;'> Employer EPS Contribution </td>"+
                                "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.eps_value+"></td></tr>");
                            }
                            if (this.epf_admin_charges>0){
                                employer+=parseInt(this.epf_admin_charges);
                                $('.employer_table').append("<tr class='data epfac' style='height:40px;'>"+
                                "<td hidden='true'></td>"+
                                "<td style='height:20px;'> EPF Admin Charges </td>"+
                                "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.epf_admin_charges+"></td></tr>");
                            }
                        }
                    });
                    $.each(jsondata, function(){
                        if (this.data_type=="ESI Employer"){
                            employer+=parseInt(this.esi_value);
                            $('.employer').attr('hidden', false);
                            $('.employer_table').append("<tr class='data esi_employer' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'> Employer ESI Contribution </td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.esi_value+"></td></tr>");
                        }
                    });
                    $.each(jsondata, function(){
                        if (this.data_type=="EDLI"){
                            employer+=parseInt(this.edli_value);
                            employer+=parseInt(this.edliac_value);
                            $('.employer').attr('hidden', false);
                            $('.employer_table').append("<tr class='data edli' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'> Employer EDLI Contribution </td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.edli_value+"></td></tr>"+
                            "<tr class='data edliac' style='height:40px;'>"+
                            "<td hidden='true'></td>"+
                            "<td style='height:20px;'> EDLI Administrative Charges </td>"+
                            "<td  style='height:20px;'><input autocomplete='off' class='form-control salarydata' type='text'"+
                            "value="+this.edliac_value+"></td></tr>");
                        }
                    });
                    $('.employer_table').append("<tr class='data employer' style='height:40px;'>"+
                    "<td hidden='true'></td>"+
                    "<td style='height:20px;'> <b>Employer's Contributions</b> </td>"+
                    "<td  style='height:20px;'>"+jsondata['Salary'].employer+"</td></tr>");
                }            
            },
            // handle a non-successful response
            error : function() {
                swal("Oops..", "There were some errors. Most probably matching data does not exist!", "error");
            }
        });
    }());
});

$('.finalize').click(function(e) {
    swal({
        title: "Generate Payslip?",
        text: "Once generated this cannot be undone!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, generate payslip!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)
            
        }
    })
});
function reconfirm () {
    swal({
        title: "Generate Payslip? Please RECONFIRM",
        text: "Once generated this cannot be undone!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, payslip generation reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
};

function save_data(){
    var monthly=[];
    var yearly=[];
    var deduction=[];
    var gross=0;
    var net=0;
    var employee=0;
    var employer=0;
    var epf_employer=0;
    var eps_employer=0;
    var epfac=0;
    var esi_employer=0;
    var edli=0;
    var edliac=0;
    var epf_employee=0;
    var esi_employee=0;
    var proceed=true;
    $("tr.monthly").each(function() {
        var name = $(this).find('td:nth-child(2)').html();
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        gross+=amount;
        net+=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
        var item = {
            name : name,
            amount: amount,
        };
        monthly.push(item);
    });
    $("tr.yearly").each(function() {
        var name = $(this).find('td:nth-child(2)').html();
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            var yearly_data='balnk'
        }
        else{
            gross+=amount;
            net+=amount;
        }
        var item = {
            name : name,
            amount: amount,
        };
        yearly.push(item);
    });
    $("tr.deduction").each(function() {
        var name = $(this).find('td:nth-child(2)').html();
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            var deduction_data='blank'
        }
        else{
            gross+=amount;
            net+=amount;
        }
        var item = {
            name : name,
            amount: amount,
        };
        deduction.push(item);
    });
    $("tr.esi").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        net-=amount;
        employee+=amount;
        esi_employee=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.epf").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        net-=amount;
        employee+=amount;
        epf_employee=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.epf_employer").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        employer+=amount;
        epf_employer=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.eps_employer").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        employer+=amount;
        eps_employer=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.epfac").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        employer+=amount;
        epfac=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.esi_employer").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        employer+=amount;
        esi_employer=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.edli").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        employer+=amount;
        edli=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    $("tr.edliac").each(function() {
        var amount = parseFloat($(this).find('td:nth-child(3) input').val());
        employer+=amount;
        edliac=amount;
        if (isNaN(amount) || typeof(amount) === "undefined" ){
            proceed=false;}
    });
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ staffid: staffid,
                    call_type:'save',
                    month:month,
                    year:year,
                    monthly:JSON.stringify(monthly),
                    yearly:JSON.stringify(yearly),
                    deduction:JSON.stringify(deduction),
                    gross:gross,
                    net:net,
                    employee:employee,
                    employer:employer,
                    epf_employer:epf_employer,
                    eps_employer:eps_employer,
                    epfac:epfac,
                    esi_employer:esi_employer,
                    edli:edli,
                    edliac:edliac,
                    epf_employee:epf_employee,
                    esi_employee:esi_employee,
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                // location.href = redirect_url;
                swal("Hooray!!", "The payslip was successfully saved. Please proceed for payment!", "success");
                setTimeout(function(){location.reload(true);},2500);
                
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors.", "error");
                }
            });
        }());
    }
}


});
