$(function(){


function round_off(value){
    value=parseInt(value*1000)/1000
    value=parseFloat(value.toFixed(2))
    return value
}


load_warehouse()

function load_warehouse(){
    $.ajax({
        url : "/master/warehouse/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#warehouse').append($('<option>',{
                    'data-id': this.id,
                    'text': this.address_1 + " "+ this.address_2
                }));
            });
            $('#warehouse').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
        }
    });
}

load_vendor()

function load_vendor(){
    $.ajax({
        url : "/master/vendor/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#vendor').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#vendor').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No warehouse data exist.", "error");
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
    get_total();
});

$(".details").on("keyup", ".pr", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".pr", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".cgstp", function(){
    this.title=this.value;
    cgstp=$(this).closest('tr').find('td:nth-child(16) input').val()
    sgstp=$(this).closest('tr').find('td:nth-child(18) input').val(cgstp)
    get_total();
});
$(".details").on("keydown", ".cgstp", function(){
    this.title=this.value;
    cgstp=$(this).closest('tr').find('td:nth-child(16) input').val()
    sgstp=$(this).closest('tr').find('td:nth-child(18) input').val(cgstp)
    get_total();
});

$(".details").on("keyup", ".sgstp", function(){
    this.title=this.value;
    sgstp=$(this).closest('tr').find('td:nth-child(18) input').val()
    cgstp=$(this).closest('tr').find('td:nth-child(16) input').val(sgstp)
    get_total();
});
$(".details").on("keydown", ".sgstp", function(){
    this.title=this.value;
    sgstp=$(this).closest('tr').find('td:nth-child(18) input').val()
    cgstp=$(this).closest('tr').find('td:nth-child(16) input').val(sgstp)
    get_total();    
});

// $(".details").on("keyup", ".igstp", function(){
//     get_total();
//     this.title=this.value;
// });
// $(".details").on("keydown", ".igstp", function(){
//     get_total();
//     this.title=this.value;
// });

$(".details").on("change", ".name", function(){
    // console.log('here');
    this.title=this.value;
}); 

$(".billdata").on("keyup", ".round", function(){
    round_manual();
});
$(".billdata").on("keydown", ".round", function(){
    round_manual();
});

function round_manual(argument) {
    subtotal = parseFloat($('.subtotal_receipt').html());
    console.log(subtotal);
    taxtotal = parseFloat($('.taxtotal_receipt').html());
    console.log(taxtotal);
    round_value = parseFloat($('.round').val());
    if(isNaN(round_value)){
        round_value = 0.00;
    }
    total = round_off(subtotal + taxtotal + round_value);
    console.log(total);
    $('.total_receipt').html(total.toFixed(2));
}

function get_total(){
    var subtotal=0, total=0, tax_total=0, cgst_grand_total=0, sgst_grand_total=0, igst_grand_total=0;
    for (var a = document.querySelectorAll('table.details tbody tr'), i = 0; a[i]; ++i) {
        // get all cells with input field
        cells = a[i].querySelectorAll('input:last-child');
        // console.log(cells);
        var quantity=1;
        
        var pur_rate=$(cells[5]).val()
        var mrp=$(cells[7]).val()
        
        discount_type=$(a[i]).find('td:nth-child(11) :selected').data('id');
        discount_val=$(cells[8]).val();
        discount_type_2=$(a[i]).find('td:nth-child(13) :selected').data('id');
        discount_val_2=$(cells[9]).val();
        // vat_input=parseInt(vat_type_reverse[$(a[i]).find('td:nth-child(17)').html()]);
        // vat_percent=parseFloat($(a[i]).find('td:nth-child(18)').html());
        cgst_percent=parseFloat($(cells[10]).val());
        sgst_percent=parseFloat($(cells[11]).val());
        igst_percent=parseFloat($(cells[12]).val());
        if(isNaN(pur_rate)){
            pur_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        if(isNaN(mrp)){
            mrp=0;
        }

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        if(isNaN(igst_percent)){
            igst_percent=0;
        }
        // console.log(free_tax_qty);
        
        var this_total=round_off(quantity*pur_rate)
        var this_total_plus_free=round_off((quantity)*pur_rate)
        var pur_disc_rate=round_off((quantity)*pur_rate)

        // console.log(discount_type);
        // console.log(discount_type_2)
		// console.log(pur_disc_rate);

        if (discount_type == 1){
            pur_disc_rate=pur_disc_rate-(discount_val*this_total/100);
            this_total=(this_total)-(discount_val*this_total/100);
        }
        else if(discount_type == 2){
            pur_disc_rate=pur_disc_rate - discount_val;
            this_total=(this_total - discount_val);
        }
        if (discount_type_2 == 1){
            pur_disc_rate=pur_disc_rate-(discount_val_2*this_total/100);
            this_total=(this_total)-(discount_val_2*this_total/100);
        }
        else if(discount_type_2 == 2){
            pur_disc_rate=pur_disc_rate - discount_val_2;
            this_total=(this_total - discount_val_2);
        }

        cgst_total=round_off((pur_disc_rate*cgst_percent)/100);
        sgst_total=round_off((pur_disc_rate*sgst_percent)/100);
        igst_total=round_off((pur_disc_rate*igst_percent)/100);
        $(a[i]).find('td:nth-child(17) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(19) ').html(sgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(21) ').html(igst_total.toFixed(2))
        
        $(a[i]).find('td:nth-child(15) ').html(this_total.toFixed(2));
        this_final_total=round_off(this_total+cgst_total+sgst_total+igst_total);
        $(a[i]).find('td:nth-child(22) ').html(this_final_total.toFixed(2));
        subtotal=round_off(subtotal+this_total);
        tax_total+=cgst_total+sgst_total+igst_total;
        cgst_grand_total+=cgst_total;
        sgst_grand_total+=sgst_total;
        igst_grand_total+=igst_total;
    }
    tax_total=round_off(tax_total);
    cgst_grand_total=round_off(cgst_grand_total);
    sgst_grand_total=round_off(sgst_grand_total);
    igst_grand_total=round_off(igst_grand_total);
    total=round_off(subtotal+tax_total);
    round_value=round_off((Math.round(total)-total));
    payable=round_off(total+round_value);
    
    
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.cgsttotal_receipt').html(cgst_grand_total.toFixed(2))
    $('.sgsttotal_receipt').html(sgst_grand_total.toFixed(2))
    $('.round').val(round_value.toFixed(2))
    $('.total_receipt').html(payable.toFixed(2))
};

$('.addmore').click(function(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<td hidden=""><input class="id"></td>'+
    '<th colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></th>'+
    '<td colspan="3"><input class="form-control name"></td>'+
    '<td colspan="1" hidden><input class="form-control qty"></td>'+
    // '<td colspan="1"><input class="form-control free"></td>'+
    '<td colspan="1" hidden><input class="form-control freet"></td>'+
    '<td colspan="1" hidden><input class="unitid"></td>'+
    '<td colspan="1" hidden><select class="form-control selectpicker unit" id="unit"></select></td>'+
    '<td colspan="1"><input class="form-control pr"></td>'+
    '<td colspan="1" hidden><input class="form-control tsr"></td>'+
    '<td colspan="1" hidden><input class="form-control mrp"></td>'+
    '<td colspan="1" hidden>'+
        '<select class="form-control selectpicker dt">'+
            '<option data-id=0 title="-">No Disc.</option>'+
            '<option data-id=1 title="%">Percent(%)</option>'+
            '<option data-id=2 title="V">Value</option>'+
    '</select></td>'+
    '<td colspan="1" hidden><input class="form-control dv"></td>'+
    '<td colspan="1" hidden>'+
        '<select class="form-control selectpicker dt2">'+
            '<option data-id=0 title="-">No Disc.</option>'+
            '<option data-id=1 title="%">Percent(%)</option>'+
            '<option data-id=2 title="V">Value</option>'+
    '</select></td>'+
    '<td colspan="1" hidden><input class="form-control dv2"></td>'+
    '<td colspan="1" hidden class="total">0.00</td>'+
    // '<td colspan="1" class="vt"></td>'+
    // '<td colspan="1" class="vp"></td>'+
    '<td colspan="1" ><input class="form-control cgstp"></td>'+
    '<td colspan="1" class="cgstv">0.00</td>'+
    '<td colspan="1"><input class="form-control sgstp"></td>'+
    '<td colspan="1" class="sgstv">0.00</td>'+
    '<td colspan="1" hidden><input class="form-control igstp"></td>'+
    '<td colspan="1" class="igstv" hidden>0.00</td>'+
    '<td colspan="1" class="tv">0.00</td>';
    $('.details').append(data);

    $('.dt').selectpicker('refresh');
    $('.dt2').selectpicker('refresh');
    
    // $.each(unit_data, function(){
    //     $('.details').find('tr:eq('+count+')').find('#unit').append($('<option>',{
    //         'data-id': this.id,
    //         'title':this.symbol,
    //         'text': this.name,
    //     }));
    // });
    // $('.unit').selectpicker('refresh');
})


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to create a new receipt?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add create new receipt!",
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
    var items=[];
    var proceed=true;
    vendorid=$('.vendor').find(':selected').data('id');
    warehouseid=$('.warehouse').find(':selected').data('id');
    invoice_no=$('.invoice').val()
    date=$('.date').val()
    duedate=$('.duedate').val()
    // grand_discount_type=$('.gdt').find(':selected').data('id');
    // grand_discount_value=$('.gd').val();
    subtotal=round_off(parseFloat($('.subtotal_receipt').html()));
    // taxtotal=parseFloat($('.taxtotal_receipt').html());
    var cgsttotal=0, sgsttotal=0, igsttotal=0;
    round_value=round_off(parseFloat($('.round').val()));
    total=round_off(parseFloat($('.total_receipt').html()));

    order_pk=$('.order_pk').html()

    if (vendorid == '' || typeof(vendorid) =='undefined' || warehouseid == '' || typeof(warehouseid) == 'undefined' ||
        $.trim(invoice_no) == '' || typeof(invoice_no) =='undefined' || $.trim(date) == '' || typeof(date) =='undefined'){
            proceed = false;
    }


    $(".details tr.data").each(function() {
        var description = $(this).find('td:nth-child(3) input').val();
        if (description == '' || description =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a product ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var purchase = $(this).find('td:nth-child(8) input').val();
        if (purchase == '' || purchase =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter the actual purchase rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var cgst_p = parseFloat($(this).find('td:nth-child(16) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(17)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }

        cgsttotal+=cgst_v
        
        var sgst_p = parseFloat($(this).find('td:nth-child(18) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(19)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }

        sgsttotal+=sgst_v

        var igst_p = parseFloat($(this).find('td:nth-child(20) input').val());
        var igst_v = parseFloat($(this).find('td:nth-child(21)').html());
        if (isNaN(igst_p)){
            igst_p=0;
            igst_v=0;
        }

        igsttotal+=igst_v

        var taxable_total = $(this).find('td:nth-child(15)').html();
        var line_total = $(this).find('td:nth-child(22)').html();
        

        var item = {
            description : description,
            purchase: purchase,
            cgst_p: cgst_p,
            cgst_v:cgst_v,
            sgst_p: sgst_p,
            sgst_v: sgst_v,
            igst_p: igst_p,
            igst_v: igst_v,
            taxable_total: purchase,
            line_total: line_total,
        };
        items.push(item);
    });
    cgsttotal = round_off(cgsttotal);
    sgsttotal = round_off(sgsttotal);
    igsttotal = round_off(igsttotal);
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{supplier_invoice: invoice_no,
                    vendor:vendorid,
                    warehouse:warehouseid,
                    date:date.split("/").reverse().join("-"),
                    order_pk: order_pk,
                    subtotal: subtotal,
                    // calledfrom : calledfrom,
                    cgsttotal: cgsttotal,
                    sgsttotal: sgsttotal,
                    igsttotal: igsttotal,
                    round_value: round_value,
                    total: total,
                    duedate: duedate.split("/").reverse().join("-"),
                    bill_details: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New purchase receipt added", "success");
                        var url='/purchase/receipt/detailview/'+jsondata+'/'
                        location.href = url;
                        // setTimeout(location.reload(true),1000);
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
    else{
        swal("Oops...", "Please note that vendor and warehouse details must be filled."+
            "Also please check the highlightd rows", "error");
    }
}

});