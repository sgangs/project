$(function(){
vat_type=["No VAT", "On MRP", "On actual"];
vat_type_reverse={"No VAT":0, "On MRP":1, "On actual":2};
var vat_input, vat_percent, unit_data, default_unit, unit_multi={}, unit_names={};

$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "api/getproduct", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            console.log(ui['item']);
            $(el).closest('tr').addClass("updating");
            $(el).closest('tr').find('td:nth-child(1) input').val(ui['item']['id']);
            default_unit=ui['item']['unit']
            $(el).closest('tr').find('td:nth-child(6) .unit').val(ui['item']['unit_id']);
            $(el).closest('tr').find('td:nth-child(7)').html(unit_multi[ui['item']['unit_id']]);
            // $(el).closest('tr').find('td:nth-child(18) ').html(vat_type[ui['item']['vat_type']]);
            // vat_percent=ui['item']['tax']
            $(el).closest('tr').find('td:nth-child(16) input').val(ui['item']['cgst']);
            $(el).closest('tr').find('td:nth-child(18) input').val(ui['item']['sgst']);
            $(el).closest('tr').find('td:nth-child(20) input').val(ui['item']['igst']);
            $('.unit').selectpicker('refresh');
            get_product_warehouse(el, ui['item']['id'])
        }
    });
});

function get_product_warehouse(el, product_id){
    warehouse_id=$('.warehouse').find(':selected').data('id');
    $.ajax({
        url : "api/getproductwarehouse", 
        type: "GET",
        data:{product_id: product_id,
            warehouse_id: warehouse_id},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $(".prod_data .prod_indi_data").remove();
            $.each(jsondata, function(){
                $('.prod_data').append("<tr class='prod_indi_data'>"+
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
    mrp=$(this).closest('tr').find('td:nth-child(2)').html()
    tsp=$(this).closest('tr').find('td:nth-child(1)').html()
    qty_avl=$(this).closest('tr').find('td:nth-child(3)').html()
    $(updating_row).find('td:nth-child(5)').html(qty_avl);
    $(updating_row).find('td:nth-child(8)').html(tsp);
    $(updating_row).find('td:nth-child(9)').html(mrp);
    $(updating_row).find('td:nth-child(10) input').val(tsp);
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

load_customers()

function load_customers(){
    $.ajax({
        url : "/master/customer/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#customer').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#customer').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No customer data exist.", "error");
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

$(".details").on("keyup", ".qty", function(){
    var el=this;
    get_total();
    get_qty_avl(el);
});
$(".details").on("keydown", ".qty", function(){
    var el=this;
    get_total();
    get_qty_avl(el);
});


$(".details").on("keyup", ".pr", function(){
    get_total();
});
$(".details").on("keydown", ".pr", function(){
    get_total();
});

$(".details").on("keyup", ".dv", function(){
    get_total();
});
$(".details").on("keydown", ".dv", function(){
    get_total();
});

$(".details").on("keyup", ".dv2", function(){
    get_total();
});
$(".details").on("keydown", ".dv2", function(){
    get_total();
});

$(".details").on("keyup", ".mrp", function(){
    get_total();
});
$(".details").on("keydown", ".mrp", function(){
    get_total();
});

$(".details").on("keyup", ".sr", function(){
    get_total();
});
$(".details").on("keydown", ".sr", function(){
    get_total();
});

$(".details").on("keyup", ".freet", function(){
    var el=this;
    get_total();
    get_qty_avl(el);
});
$(".details").on("keydown", ".freet", function(){
    var el=this;
    get_total();
    get_qty_avl(el);
});

$(".details").on("keyup", ".free", function(){
    var el=this;
    get_qty_avl(el);
});

$(".details").on("keydown", ".free", function(){
    var el=this;
    get_qty_avl(el);
});

$(".details").on("change", ".dt", function(){
    get_total();
});

$(".details").on("change", ".dt2", function(){
    get_total();
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

$(".details").on("keyup", ".cgstp", function(){
    get_total();
});
$(".details").on("keydown", ".cgstp", function(){
    get_total();
});

$(".details").on("keyup", ".sgstp", function(){
    get_total();
});
$(".details").on("keydown", ".sgstp", function(){
    get_total();
});

$(".details").on("keyup", ".igstp", function(){
    get_total();
});
$(".details").on("keydown", ".igstp", function(){
    get_total();
});


$(".details").on("change", ".unit", function(){
    var unit_id = $(this).find(':selected').data('id');
    unit_multi_selected=unit_multi[unit_id]
    $(this).closest('tr').find('td:nth-child(7)').html(unit_multi_selected);
    get_qty_avl(this);
});



function get_qty_avl(el){
    var unit_id = $(el).closest('tr').find('td:nth-child(6) .unit :selected').data('id');
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(5)').html());
    if (isNaN(quantity_avl)){
        quantity_avl=0;
    }
    // var free = parseInt($(el).closest('tr').find('td:nth-child(6) input').val());
    // if (isNaN(free)){
        free=0;
    // }
    // var free_tax = parseInt($(el).closest('tr').find('td:nth-child(7) input').val());
    // if (isNaN(free_tax)){
        free_tax=0;
    // }
    var unit_multi_selected = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());
    quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity+free+free_tax)>quantity_avl ){
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
    if ((quantity+free+free_tax)<=quantity_avl){
        $(el).closest('tr').removeClass("has-error");
        return true;
    }
}



function get_total(){
    var subtotal=0, total=0, tax_total=0;
    for (var a = document.querySelectorAll('table.details tbody tr'), i = 0; a[i]; ++i) {
        // get all cells with input field
        cells = a[i].querySelectorAll('input:last-child');
        console.log(cells)
        var quantity=parseFloat($(cells[2]).val());
        var qty_avl=parseFloat($(a[i]).find('td:nth-child(5)').html());
        // var free_tax_qty=parseFloat($(cells[4]).val());
        var free_tax_qty=0;
        var sales_rate=$(cells[3]).val()
        var mrp=$(a[i]).find('td:nth-child(9)').html();
        // var vat_total=0
        
        discount_type=$(a[i]).find('td:nth-child(11) :selected').data('id');
        discount_val=$(cells[4]).val();
        discount_type_2=$(a[i]).find('td:nth-child(13) :selected').data('id');
        discount_val_2=$(cells[5]).val();
        console.log(discount_type_2)
        console.log(discount_val_2)

        cgst_percent=parseFloat($(cells[6]).val());
        sgst_percent=parseFloat($(cells[7]).val());
        igst_percent=parseFloat($(cells[8]).val());

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        if(isNaN(igst_percent)){
            igst_percent=0;
        }
        
        // vat_input=parseInt(vat_type_reverse[$(a[i]).find('td:nth-child(18)').html()]);
        // vat_percent=parseFloat($(a[i]).find('td:nth-child(19)').html());
        
        if(isNaN(sales_rate)){
            sales_rate=0;
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
        
        var this_total=quantity*sales_rate
        
        sales_disc_rate=sales_rate
        if (discount_type == 1){
            sales_disc_rate=sales_disc_rate-(discount_val*this_total/100);
            this_total=(this_total)-(discount_val*this_total/100);
        }
        else if(discount_type == 2){
            sales_disc_rate=sales_disc_rate - discount_val/quantity;
            this_total=(this_total - discount_val);
        }
        if (discount_type_2 == 1){
            sales_disc_rate=sales_disc_rate-(discount_val_2*this_total/100);
            this_total=(this_total)-(discount_val_2*this_total/100);
        }
        else if(discount_type_2 == 2){
            sales_disc_rate=sales_disc_rate - discount_val_2/quantity;
            this_total=(this_total - discount_val_2);
        }
        // if (vat_input == 1){
        //     vat_total=(mrp*(quantity+free_tax_qty))-(mrp*(quantity+free_tax_qty))/(100+vat_percent)*100;
        // }
        // else if (vat_input == 2){
        //     vat_total=((sales_disc_rate*(quantity+free_tax_qty))*vat_percent)/100;
        // }

        cgst_total=(this_total*cgst_percent)/100;
        sgst_total=(this_total*sgst_percent)/100;
        igst_total=(this_total*igst_percent)/100;
        $(a[i]).find('td:nth-child(17) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(19) ').html(sgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(21) ').html(igst_total.toFixed(2))

        $(a[i]).find('td:nth-child(15) ').html(this_total.toFixed(2))
        vat_total=0;
        // this_final_total=this_total+vat_total
        this_final_total=this_total+cgst_total+sgst_total+igst_total
        $(a[i]).find('td:nth-child(22) ').html(this_final_total.toFixed(2))
        subtotal=subtotal+this_total
        tax_total=tax_total+cgst_total+sgst_total+igst_total
    }
    total=subtotal+tax_total
    gd_type=$('.gdt').find(':selected').data('id')
    gd_value=parseFloat($('.gd').val())
    var gd_calculated=0;
    if(isNaN(gd_value)){
        gd_value=0;
    }
    if (gd_type == 1){
        gd_calculated=(gd_value*subtotal/100)
        total=total-gd_calculated;
    }
    else if(gd_type == 2){
        gd_calculated=gd_value
        total=(total-gd_calculated);
    }
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    // $('.grand_discount').html(gd_calculated.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.total_receipt').html(total.toFixed(2))
};

$('.addmore').click(function(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<td hidden><input class="id"></td>'+
    '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
    '<td colspan="3"><input class="form-control name"></td>'+
    '<td colspan="1"><input class="form-control qty"></td>'+
    '<td colspan="1" class="qty_avl" hidden>'+0+'</td>'+
    // '<td colspan="1"><input class="form-control free"></td>'+
    // '<td colspan="1"><input class="form-control freet"></td>'+
    '<td colspan="1"><select class="form-control selectpicker unit" id="unit"></select></td>'+
    '<td colspan="1" hidden="" class="unit_multi"></td>'+
    '<td colspan="1" hidden class="tsr"></td>'+
    '<td colspan="1" hidden class="mrp"></td>'+
    '<td colspan="1"><input hidden class="form-control sr"></td>'+
    '<td colspan="1"><select class="form-control selectpicker dt">'+
        '<option data-id=0 title="-">No Discount</option>'+
        '<option data-id=1 title=%>Percent(%)</option>'+
        '<option data-id=2 title="V">Value(V)</option>'+
        '</select></td>'+
    '<td colspan="1"><input class="form-control dv"></td>'+
    '<td colspan="1"><select class="form-control selectpicker dt2">'+
        '<option data-id=0 title="-">No Discount</option>'+
        '<option data-id=1 title=%>Percent(%)</option>'+
        '<option data-id=2 title="V">Value(V)</option>'+
        '</select></td>'+
    '<td colspan="1"><input class="form-control dv2"></td>'+
    '<td colspan="1" class="total">0.00</td>'+
    // '<td colspan="1" class="vt"></td>'+
    // '<td colspan="1" class="vp"></td>'+
    '<td colspan="1" class="cgstp"><input class="form-control dv2"></td>'+
    '<td colspan="1" class="cgstv"></td>'+
    '<td colspan="1" class="sgstp"><input class="form-control dv2"></td>'+
    '<td colspan="1" class="sgstv"></td>'+
    '<td colspan="1" class="igstp"><input class="form-control dv2"></td>'+
    '<td colspan="1" class="igstv"></td>'+
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
})




$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure you want to generate a new sales invoice?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, generate new sales invoice!",
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
    customerid=$('.customer').find(':selected').data('id');
    warehouseid=$('.warehouse').find(':selected').data('id');
    date=$('.date').val()
    duedate=$('.duedate').val()
    grand_discount_type=$('.gdt').find(':selected').data('id');
    grand_discount_value=$('.gd').val();
    subtotal=parseFloat($('.subtotal_receipt').html());
    taxtotal=parseFloat($('.taxtotal_receipt').html());
    total=parseFloat($('.total_receipt').html());
    if (customerid == '' || typeof(customerid) =='undefined' || warehouseid == '' || typeof(warehouseid) =='undefined' ||
        $.trim(date) == '' || typeof(date) =='undefined'){
        proceed = false;
        swal("Oops...", "Please select/enter customer name, warehouse and bill date. ", "error");
    }
    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(1) input').val();
        if (product_id == '' || product_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a product ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var quantity = parseFloat($(this).find('td:nth-child(4) input').val());
        var quantity_avl = parseFloat($(this).find('td:nth-child(5)').html());
        if (quantity == '' || quantity =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        // var free = parseInt($(this).find('td:nth-child(6) input').val());

        // if (isNaN(free)){
        //     free=0;
        // }
        
        // var free_tax = parseInt($(this).find('td:nth-child(7) input').val());
        // if (isNaN(free_tax)){
        //     free_tax=0;
        // }
        
        var qty_proceed= get_qty_avl(this);
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

        var tsp = $(this).find('td:nth-child(8)').html();
        var mrp = $(this).find('td:nth-child(9)').html();
        
        var sales = $(this).find('td:nth-child(10) input').val();
        if (sales == '' || sales =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a sales rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        var disc_type = $(this).find('td:nth-child(11) :selected').data('id');
        var disc = parseFloat($(this).find('td:nth-child(12) input').val());
        if (isNaN(disc)){
            disc=0;
        }

        var disc_type_2 = $(this).find('td:nth-child(13) :selected').data('id');
        var disc_2 = parseFloat($(this).find('td:nth-child(14) input').val());
        if (isNaN(disc_2)){
            disc_2=0;
        }

        var cgst_p = parseFloat($(this).find('td:nth-child(16) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(17)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }
        
        var sgst_p = parseFloat($(this).find('td:nth-child(18) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(19)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }

        var igst_p = parseFloat($(this).find('td:nth-child(20) input').val());
        var igst_v = parseFloat($(this).find('td:nth-child(21)').html());
        if (isNaN(igst_p)){
            igst_p=0;
            igst_v=0;
        }
        
        var taxable_total = $(this).find('td:nth-child(15)').html();
        var line_total = $(this).find('td:nth-child(22)').html();
        
        var item = {
            product_id : product_id,
            quantity: quantity,
            // free: free,
            // free_tax:free_tax,
            unit_id: unit_id,
            sales: sales,
            tsp:tsp,
            mrp: mrp,
            disc_type: disc_type,
            disc: disc,
            disc_type_2: disc_type_2,
            disc_2: disc_2,
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
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{customer:customerid,
                    warehouse:warehouseid,
                    date:date.split("/").reverse().join("-"),
                    grand_discount_type: grand_discount_type,
                    grand_discount_value: grand_discount_value,
                    subtotal: subtotal,
                    taxtotal: taxtotal,
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
                        swal("Hooray", "New sale invoice generated", "success");
                        var url='/sales/invoice/detailview/'+jsondata+'/'
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
        // swal("Oops...", "Please note that vendor and warehouse details must be filled."+
        //     "Also please check the highlightd rows", "error");
    }
}

});