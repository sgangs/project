$(function(){
vat_type=["No VAT", "On MRP", "On actual"];
vat_type_reverse={"No VAT":0, "On MRP":1, "On actual":2};
var vat_input, vat_percent, unit_data, default_unit, unit_multi={}, unit_names={}, maintain_inventory, tsp, mrp, is_igst = false;


function round_off(value){
    value=parseInt(value*1000)/1000
    value=parseFloat(value.toFixed(2))
    return value
}


$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "/purchase/receipt/api/getproduct", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            var item_cgst = parseFloat(ui['item']['cgst']);
            var item_sgst = parseFloat(ui['item']['sgst']);
            var item_igst = item_cgst + item_sgst;

            maintain_inventory=ui['item']['inventory']
            $(el).closest('tr').find('td:nth-child(1) input').val(ui['item']['id']);
            console.log(ui['item']['id']);
            default_unit=ui['item']['unit']
            $(el).closest('tr').find('td:nth-child(6) .unit').val(ui['item']['unit_id']);
            // console.log(unit_multi[ui['item']['unit_id']]);
            $(el).closest('tr').find('td:nth-child(5)').html(unit_multi[ui['item']['unit_id']]);
            // $(el).closest('tr').find('td:nth-child(18) ').html(vat_type[ui['item']['vat_type']]);
            // vat_percent=ui['item']['tax']
            if (is_igst){
                $(el).closest('tr').find('td:nth-child(13) input').val(0);
                $(el).closest('tr').find('td:nth-child(15) input').val(0);
                $(el).closest('tr').find('td:nth-child(17) input').val(item_igst);
            }
            else{
                $(el).closest('tr').find('td:nth-child(13) input').val(item_cgst);
                $(el).closest('tr').find('td:nth-child(15) input').val(item_sgst);
                $(el).closest('tr').find('td:nth-child(17) input').val(0);
            }
            $('.unit').selectpicker('refresh');
            if (maintain_inventory){
                $(el).closest('tr').addClass("updating");
                get_product_warehouse(el, ui['item']['id'])
            }
        }
    });
});

function get_product_warehouse(el, product_id){
    warehouse_id=$('.warehouse').find(':selected').data('id');
    $.ajax({
        url : "/purchase/productinventorydetails/", 
        type: "GET",
        data:{product_id: product_id,
            warehouse_id: warehouse_id},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $(".prod_data .prod_indi_data").remove();
            $.each(jsondata, function(){
                $('.prod_data').append("<tr class='prod_indi_data'>"+
                "<td class='prod_pur'>"+this.purchase_price+"</td>"+
                "<td class='prod_tsp'>"+this.tentative_sales_price +"</td>"+
                "<td class='prod_mrp'>"+this.mrp+"</td>"+
                "<td class='prod_qa'>"+this.available+"</td>"+
                "<td class='prod_qa'>"+default_unit+"</td>"+
                "</tr>");
            })
            $('#productdetails').modal('show');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product inventory exist.", "error");
        }
    });
}

$('.prod_data').on('click','.prod_indi_data', function(){
    // console.log('clicked');
    updating_row=$('.details').find('.updating')
    purchase_rate=$(this).closest('tr').find('td:nth-child(1)').html()
    tsp=$(this).closest('tr').find('td:nth-child(2)').html()
    mrp=$(this).closest('tr').find('td:nth-child(3)').html()
    qty_avl=$(this).closest('tr').find('td:nth-child(4)').html()
    $(updating_row).find('td:nth-child(7)').html(qty_avl);
    $(updating_row).find('td:nth-child(8)').html(purchase_rate);
    $(updating_row).find('td:nth-child(9) input').val(purchase_rate);
    $(updating_row).find('td:nth-child(10)').html(tsp);
    $(updating_row).find('td:nth-child(11)').html(mrp);
    $(updating_row).removeClass('updating');
    $('#productdetails').modal('hide');
    // console.log(mrp)
});


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

load_units()

function load_units(){
    $.ajax({
        url : "/master/dimensionunit/unitdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            unit_data=jsondata
            $.each(jsondata, function(){
                unit_multi[this.id]=parseFloat(this.multiplier);
                unit_names[this.id]=this.name;
                $('#unit').append($('<option>',{
                    'data-id': this.id,
                    'title':this.symbol,
                    'text': this.name,
                }));
            });
            $('#unit').selectpicker('refresh');
            // $('#unit').html('refresh',true);
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No unit is registered.", "error");
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



$('#vendor').on('change', function() {
    $('.adj_receipt').attr('disabled', false);
    $('.adj_receipt').val("");
})

$('.adj_receipt').on('change', function() {
    var proceed = true;
    var adjustment_receipt = $('.adj_receipt').val();
    var vendor_id = $('.vendor').find(':selected').data('id');
    
    if (adjustment_receipt == '' || adjustment_receipt == undefined || adjustment_receipt == 'undefined' || adjustment_receipt == null ||
        adjustment_receipt == 'null' || vendor_id == '' || vendor_id == undefined || vendor_id == 'undefined' || 
        vendor_id == null || vendor_id == 'null'){
        proceed = false;
        if (vendor_id == '' || vendor_id == undefined || vendor_id == 'undefined' || vendor_id == null || vendor_id == 'null'){
            swal("Oops...", "Please select a vendor.", "error");
        }
    }
    if (proceed){
        $.ajax({
            url : "/purchase/purchase-receipt-vendor/", 
            type: "GET",
            data:{receipt_no: adjustment_receipt,
                vendor_id: vendor_id},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                if (jsondata == 'No data'){
                    swal("Oops...", "Receipt does not exist or receipt is completely paid off.", "error");
                    $('.adj_receipt_found').val('not-found');    
                }
                else{
                    $('.adj_value_total').val(jsondata['total']);
                    var total = parseFloat(jsondata['total']);
                    var paid = parseFloat(jsondata['amount_paid']);
                    var due = total - paid
                    $('.adj_value_due').val(due);
                }
                // swal("Oops...", "No warehouse data exist.", "error");
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "Could not fetch data.", "error");
            }
        });
    }   
    
})


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

$(".details").on("keyup", ".qty", function(){
    var el=this;
    this.title=this.value;
    get_total();
    if (maintain_inventory){
        get_qty_avl(el);
    }
});
$(".details").on("keydown", ".qty", function(){
    var el=this;
    this.title=this.value;
    get_total();
    if (maintain_inventory){
        get_qty_avl(el);
    }
});


$(".details").on("keyup", ".pr", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".pr", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".dv", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".dv", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".dv2", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keydown", ".dv2", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".mrp", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".mrp", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".sr", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".sr", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".freet", function(){
    var el=this;
    this.title=this.value;
    get_total();
    if (maintain_inventory){
        get_qty_avl(el);
    }
});
$(".details").on("keydown", ".freet", function(){
    var el=this;
    this.title=this.value;
    get_total();
    if (maintain_inventory){
        get_qty_avl(el);
    }
});

$(".details").on("keyup", ".free", function(){
    var el=this;
    this.title=this.value;
    if (maintain_inventory){
        get_qty_avl(el);
    }
});

$(".details").on("keydown", ".free", function(){
    var el=this;
    this.title=this.value;
    if (maintain_inventory){
        get_qty_avl(el);
    }
});

$(".details").on("change", ".dt", function(){
    get_total();
    // this.title=this.value;
});

$(".details").on("change", ".discount_type2", function(){
    get_total();
    // this.title=this.value;
});

// $( ".gd" ).change(function() {
//     get_total();
// });

// $( ".gdt" ).change(function() {
//     get_total();
// });

// $( ".gdt" ).change(function() {
//     get_total();
// });

$('.is_igst').on('switchChange.bootstrapSwitch', function(event, state) {
    is_igst = state; // true | false
    if (is_igst) {
        $('.tax_type_label').html("Change if C/SGST");
        $(".details .data").remove();
        add_row();
        get_total();
    }
    else{
        $('.tax_type_label').html("Change if IGST");
        $(".details .data").remove();
        add_row();
        get_total();
    }
  //Based on state change, hide necessary columns and delete all rows.
});

$(".details").on("keyup", ".cgstp", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".cgstp", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".sgstp", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".sgstp", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("keyup", ".igstp", function(){
    get_total();
    this.title=this.value;
});
$(".details").on("keydown", ".igstp", function(){
    get_total();
    this.title=this.value;
});

$(".details").on("change", ".name", function(){
    this.title=this.value;
});

$(".billdata").on("keyup", ".round", function(){
    round_manual();
});
$(".billdata").on("keydown", ".round", function(){
    round_manual();
});


$(".details").on("change", ".unit", function(){
    var unit_id = $(this).find(':selected').data('id');
    unit_multi_selected=unit_multi[unit_id]
    $(this).closest('tr').find('td:nth-child(7)').html(unit_multi_selected);
    if (maintain_inventory){
        var el=this;
        get_qty_avl(el);
    }
    // get_total();
});


function round_manual(argument) {
    subtotal = parseFloat($('.subtotal_receipt').html());
    taxtotal = parseFloat($('.taxtotal_receipt').html());
    round_value = parseFloat($('.round').val());
    total = round_off(subtotal + taxtotal + round_value);
    $('.total_receipt').html(total.toFixed(2));
}



function get_qty_avl(el){
    var unit_id = $(el).closest('tr').find('td:nth-child(6) .unit :selected').data('id');
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());

    if (isNaN(quantity_avl)){
        quantity_avl=0;
    }
    
    var unit_multi_selected = ($(el).closest('tr').find('td:nth-child(5)').html());

    quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than available quantity. <br>"+
                        " Total available quantity: "+quantity_avl+" "+unit_names[unit_id]+".",
                type: "warning",
                showCancelButton: false,
                closeOnConfirm: true,
                closeOnCancel: true,
                html: true,
            });
            $(el).closest('tr').addClass("has-error");
            return false;
        }
        else{
            $(el).closest('tr').removeClass("has-error");
            return true;
        }
    }
    if ((quantity)<=quantity_avl){
        $(el).closest('tr').removeClass("has-error");
        return true;
    }
}



function get_total(){
    var subtotal=0, total=0, tax_total=0;
    for (var a = document.querySelectorAll('table.details tbody tr'), i = 0; a[i]; ++i) {
        // get all cells with input field
        cells = a[i].querySelectorAll('input:last-child');
        
        var quantity=parseFloat($(cells[2]).val());
        var qty_avl=parseFloat($(a[i]).find('td:nth-child(7)').html());
        // var free_tax_qty=parseFloat($(cells[4]).val());
        var free_tax_qty=0;
        var purchase_rate=$(cells[3]).val()
        // var vat_total=0
        
        cgst_percent=parseFloat($(cells[4]).val());
        sgst_percent=parseFloat($(cells[5]).val());
        igst_percent=parseFloat($(cells[6]).val());

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        if(isNaN(igst_percent)){
            igst_percent=0;
        }
        
        if(isNaN(purchase_rate)){
            purchase_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        if(isNaN(mrp)){
            mrp=0;
        }
        // if(isNaN(free_tax_qty)){
            // free_tax_qty=0;
        // }
        
        var this_total=quantity*purchase_rate
        
        cgst_total=round_off((this_total*cgst_percent)/100);
        sgst_total=round_off((this_total*sgst_percent)/100);
        igst_total=round_off((this_total*igst_percent)/100);
        
        $(a[i]).find('td:nth-child(14) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(16) ').html(sgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(18) ').html(igst_total.toFixed(2))

        $(a[i]).find('td:nth-child(12) ').html(this_total.toFixed(2))
        
        this_final_total=round_off(this_total+cgst_total+sgst_total+igst_total)
        $(a[i]).find('td:nth-child(19) ').html(this_final_total.toFixed(2))
        
        subtotal=subtotal+this_total
        tax_total=tax_total+cgst_total+sgst_total+igst_total
    }
    subtotal = round_off(subtotal)
    tax_total = round_off(tax_total)
    total=round_off(subtotal+tax_total);
    round_value=round_off((Math.round(total)-total));
    payable=round_off(total+round_value);
    
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.round').val(round_value.toFixed(2))
    show_total = round_off(total+round_value);
    due_total = $('.adj_value_due').val();
    if (show_total > due_total){
        if ($('.adj_receipt_error').val() == 'error'){}
        else{
            swal("Oops...", "Total purchase return amount cannot be more than amount due against selected purchase receipt.", "error");
            $('.adj_receipt_error').val('error');
        }
    }
    else{
        $('.adj_receipt_error').val('');
    }
    $('.total_receipt').html(show_total.toFixed(2))
};

$('.addmore').click(function(){
    add_row();
});


function add_row(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<td hidden><input class="id"></td>'+
    '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
    '<td colspan="3"><input class="form-control name"></td>'+
    '<td colspan="1"><input class="form-control qty"></td>'+
    '<td colspan="1" hidden="" class="unit_multi"></td>'+
    '<td colspan="1"><select class="form-control selectpicker unit" id="unit"></select></td>'+
    '<td colspan="1" hidden class="qty_available"></td>'+
    '<td colspan="1" hidden class="original_pr"></td>'+
    '<td colspan="1"><input class="form-control pr"></td>'+
    '<td colspan="1" class="tsr"></td>'+
    '<td colspan="1" class="mrp"></td>'+
    '<td colspan="1" class="total">0.00</td>'+
    // '<td colspan="1" class="vt"></td>'+
    // '<td colspan="1" class="vp"></td>'+
    '<td colspan="1" class="csgst"><input class="form-control cgstp"></td>'+
    '<td colspan="1" class="cgstv csgst"></td>'+
    '<td colspan="1" class="csgst"><input class="form-control sgstp"></td>'+
    '<td colspan="1" class="sgstv csgst"></td>'+
    '<td colspan="1" class="igst"><input class="form-control igstp"></td>'+
    '<td colspan="1" class="igstv igst"></td>'+
    '<td colspan="1" class="tv">0.00</td></tr>'
    $('.details').append(data);

    $('.dt').selectpicker('refresh');
    $('.dt2').selectpicker('refresh');
    
    $.each(unit_data, function(){
        $('.details').find('tr:eq('+count+')').find('#unit').append($('<option>',{
            'data-id': this.id,
            'title':this.symbol,
            'text': this.name,
        }));
    });
    $('.unit').selectpicker('refresh');

    if (is_igst){
        $('.csgst').attr('hidden', true);
        $('.igst').attr('hidden', false);    
    }
    else{
        $('.igst').attr('hidden', true);
        $('.csgst').attr('hidden', false);
    }
}


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to generate a new sales invoice?",
        type: "info",
        showCancelButton: true,
        confirmButtonColor: "#11BB55",
        confirmButtonText: "Yes, generate new sales invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data(false)},600)            
        }
    })
});

$('.submit_final').click(function(e) {
    // speak_text("Are you sure you want to create and finalize a new invoice? Note that you cannot edit this invoice once finalized.");
    // var msg = new SpeechSynthesisUtterance("Are you sure you want to create and finalize a new invoice?"+
    //         " Note that you cannot edit this invoice once finalized.");
    // window.speechSynthesis.speak(msg);
    swal({
        title: "Are You Sure To Finalize?",
        text: "Are you sure you want to create and finalize a new sales invoice?<p>Note that you cannot edit this invoice once finalized.</p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, finalize & generate new sales invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)            
        }
    })
});

function reconfirm() {
    // speak_text("Please reconfirm you want to finalize this invoice.");
    swal({
        title: "Please Reconfirm.",
        text: "<p>Are you sure you want to finalize a new sales invoice?</p><p>Note that it cannot be edited</p>",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, finalize & generate new sales invoice!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_data(true)},600)            
        }
    })
};

    
function new_data(is_final){
    var items=[];
    var proceed=true;
    
    var is_igst = $('.is_igst').is(':checked');

    vendor_id=$('.vendor').find(':selected').data('id');
    warehouseid=$('.warehouse').find(':selected').data('id');
    date = $('.date').val();
    supplier_note_no = $('.supplier_note_no').val();
    adjustment_receipt_no = $('.adj_receipt').val();
    adj_receipt_error = $('.adj_receipt_error').val();

    subtotal=round_off(parseFloat($('.subtotal_receipt').html()));
    var cgsttotal=0, sgsttotal=0, igsttotal=0;
    total=round_off(parseFloat($('.total_receipt').html()));
    round_value=round_off(parseFloat($('.round').val()));
    
    if (vendor_id == '' || typeof(vendor_id) =='undefined' || warehouseid == '' || typeof(warehouseid) =='undefined' ||
        $.trim(date) == '' || typeof(date) =='undefined'){
        proceed = false;
        swal("Oops...", "Please select/enter vendor name, warehouse and bill date. ", "error");
    }
    if (adj_receipt_error == 'error'){
        proceed = false;
        swal("Oops...", "Error in adjustmenr receipt. Check if available balance is more than return balance.", "error");
    }

    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(1) input').val();
        if (product_id == '' || product_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a product ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var quantity = parseFloat($(this).find('td:nth-child(4) input').val());
        var quantity_avl = parseFloat($(this).find('td:nth-child(7)').html());
        if (quantity == '' || quantity =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        if (maintain_inventory){
            var qty_proceed= get_qty_avl(this);
        }
        else{
            qty_proceed = true;
        }
        
        if (!qty_proceed){
            swal("Oops...", "You don't have enough quantity available. ", "error");
            proceed=false;
        }

        var unit_id = $(this).find('td:nth-child(6) :selected').data('id');
        if (unit_id == '' || unit_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter the purchase unit ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var purchase_real = $(this).find('td:nth-child(8)').html();
        var purchase = $(this).find('td:nth-child(9) input').val();
        var tsp = $(this).find('td:nth-child(10)').html();
        var mrp = $(this).find('td:nth-child(11)').html();
        
        if (purchase == '' || purchase =='undefined' || typeof(purchase) == undefined || purchase == null){
            proceed=false;
            swal("Oops...", "Please enter a purchase rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        var cgst_p = parseFloat($(this).find('td:nth-child(13) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(14)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }
        cgsttotal+=cgst_v
        
        var sgst_p = parseFloat($(this).find('td:nth-child(15) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(16)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }
        sgsttotal+=sgst_v

        var igst_p = parseFloat($(this).find('td:nth-child(17) input').val());
        var igst_v = parseFloat($(this).find('td:nth-child(18)').html());
        if (isNaN(igst_p)){
            igst_p=0;
            igst_v=0;
        }
        igsttotal+=igst_v
        
        var taxable_total = $(this).find('td:nth-child(12)').html();
        var line_total = $(this).find('td:nth-child(19)').html();
        
        var item = {
            product_id : product_id,
            quantity: quantity,
            unit_id: unit_id,
            purchase: purchase,
            purchase_real: purchase_real,
            tsp:tsp,
            mrp: mrp,
            cgst_p: cgst_p,
            cgst_v:cgst_v,
            sgst_p: sgst_p,
            sgst_v: sgst_v,
            igst_p: igst_p,
            igst_v: igst_v,
            taxable_total: taxable_total,
            line_total: line_total,
        };
        items.push(item);
    });
    // console.log(cgsttotal);
    cgsttotal = round_off(cgsttotal);
    sgsttotal = round_off(sgsttotal);
    igsttotal = round_off(igsttotal);

    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{vendor:vendor_id,
                    warehouse:warehouseid,
                    date:date.split("/").reverse().join("-"),
                    subtotal: subtotal,
                    round_value: round_value,
                    supplier_note_no: supplier_note_no,
                    adjustment_receipt_no: adjustment_receipt_no,
                    is_igst: is_igst, 
                    cgsttotal: cgsttotal,
                    sgsttotal: sgsttotal,
                    igsttotal: igsttotal,
                    total: total,
                    bill_details: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    console.log(jsondata);
                    if (typeof(jsondata["id"]) == "undefined"){
                        swal("Oops...", "Recheck your inputs. "+jsondata, "error");        
                    }
                    else{
                        swal("Hooray", "New purchase return generated", "success");
                        // var url='/sales/invoice/detailview/'+jsondata['invoice_id']+'/'
                        // location.href = url;
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
        // swal("Oops...", "Please note that vendor and warehouse details must be filled."+
        //     "Also please check the highlightd rows", "error");
    }


}

});