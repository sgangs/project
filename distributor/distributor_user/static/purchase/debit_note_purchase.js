$(function(){
vat_type=["No VAT", "On MRP", "On actual"];
vat_type_reverse={"No VAT":0, "On MRP":1, "On actual":2};
var vat_input, vat_percent, unit_data, default_unit, unit_multi={}, unit_names={};

$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "/purchase/receipt/api/getproduct", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            $(el).closest('tr').addClass("updating");
            $(el).closest('tr').find('td:nth-child(1) input').val(ui['item']['id']);
            default_unit=ui['item']['unit']
            $(el).closest('tr').find('td:nth-child(6) .unit').val(ui['item']['unit_id']);
            $(el).closest('tr').find('td:nth-child(7)').html(unit_multi[ui['item']['unit_id']]);
            $(el).closest('tr').find('td:nth-child(13) ').html(vat_type[ui['item']['vat_type']]);
            vat_percent=ui['item']['tax']
            $(el).closest('tr').find('td:nth-child(14) ').html(vat_percent);
            $('.unit').selectpicker('refresh');
            get_product_warehouse(el, ui['item']['id'])
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
                "<td class='prod_tsp'>"+this.purchase_price +"</td>"+
                "<td class='prod_tsp'>"+this.tentative_sales_price +"</td>"+
                "<td class='prod_mrp'>"+this.mrp+"</td>"+
                "<td class='prod_qa'>"+this.available+"</td>"+
                // "<td class='prod_qa'>"+default_unit+"</td>"+
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
    pr=$(this).closest('tr').find('td:nth-child(1)').html()
    tsp=$(this).closest('tr').find('td:nth-child(2)').html()
    mrp=$(this).closest('tr').find('td:nth-child(3)').html()
    qty_avl=$(this).closest('tr').find('td:nth-child(4)').html()
    $(updating_row).find('td:nth-child(5)').html(qty_avl);
    $(updating_row).find('td:nth-child(8)').html(pr);
    $(updating_row).find('td:nth-child(9)').html(tsp);
    $(updating_row).find('td:nth-child(10)').html(mrp);
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
    get_total();
    get_qty_avl(this);
});
$(".details").on("keydown", ".qty", function(){
    get_total();
    get_qty_avl(this);
});

$(".details").on("change", ".is_tax", function(){
    get_total();
});

$(".details").on("change", ".unit", function(){
    var unit_id = $(this).find(':selected').data('id');
    unit_multi_selected=unit_multi[unit_id]
    old_multi=parseFloat($(this).closest('tr').find('td:nth-child(7)').html())
    // console.log(old_multi);

    $(this).closest('tr').find('td:nth-child(7)').html(unit_multi_selected);
    var pur_rate=parseFloat($(this).closest('tr').find('td:nth-child(8)').html());
    var tsp=parseFloat($(this).closest('tr').find('td:nth-child(9)').html());
    // console.log(tsp)
    var mrp=parseFloat($(this).closest('tr').find('td:nth-child(10)').html());
    
    new_pr=pur_rate*unit_multi_selected/old_multi;
    new_tsp=tsp*unit_multi_selected/old_multi;
    new_mrp=mrp*unit_multi_selected/old_multi;
    // console.log(new_pr);
    // console.log(new_tsp);
    // console.log(new_mrp);

    $(this).closest('tr').find('td:nth-child(8)').html(new_pr)
    $(this).closest('tr').find('td:nth-child(9)').html(new_tsp)
    $(this).closest('tr').find('td:nth-child(10)').html(new_mrp)

    get_qty_avl(this);
});

function get_qty_avl(el){
    var unit_id = $(el).closest('tr').find('td:nth-child(6) .unit :selected').data('id');
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(5)').html());
    if (isNaN(quantity_avl)){
        quantity_avl=0;
    }
    var unit_multi_selected = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());
    quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than available quantity. <br>"+
                        " Total available quantity: "+quantity_avl.toFixed(2)+" "+unit_names[unit_id]+".",
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
        // console.log(cells);
        var quantity=parseFloat($(cells[2]).val());
        var pur_rate=parseFloat($(a[i]).find('td:nth-child(8)').html());
        var mrp=parseFloat($(a[i]).find('td:nth-child(10)').html());
        var vat_total=0
        is_tax=$(a[i]).find('td:nth-child(12) input').is(":checked")
        vat_input=parseInt(vat_type_reverse[$(a[i]).find('td:nth-child(13)').html()]);
        vat_percent=parseFloat($(a[i]).find('td:nth-child(14)').html());
        if(isNaN(pur_rate)){
            pur_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        if(isNaN(mrp)){
            mrp=0;
        }
        
        var this_total=quantity*pur_rate
        if (is_tax){
            if (vat_input == 1){
                vat_total=(mrp*(quantity))-(mrp*(quantity))/(100+vat_percent)*100;
            }
            else if (vat_input == 2){
                vat_total=((pur_rate*(quantity))*vat_percent)/100;
            }
        }
        $(a[i]).find('td:nth-child(11) ').html(this_total.toFixed(2))
        this_final_total=this_total+vat_total
        $(a[i]).find('td:nth-child(15) ').html(this_final_total.toFixed(2))
        subtotal=subtotal+this_total
        tax_total=tax_total+vat_total
    }
    total=subtotal+tax_total
    $('.subtotal_receipt').html(subtotal.toFixed(2))
    $('.taxtotal_receipt').html(tax_total.toFixed(2))
    $('.total_receipt').html(total.toFixed(2))
};

$('.addmore').click(function(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<td hidden=""><input class="id" disabled></td>'+
    '<th colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></th>'+
    '<td colspan="3"><input class="form-control name"></td>'+
    '<td colspan="1"><input class="form-control qty"></td>'+
    '<td colspan="1" hidden></td>'+
    '<td colspan="1"><select class="form-control selectpicker unit" id="unit"></select></td>'+
    '<td colspan="1" hidden></td>'+
    '<td colspan="1"><input class="form-control pr" disabled></td>'+
    '<td colspan="1"><input class="form-control tsr" disabled hidden></td>'+
    '<td colspan="1"><input class="form-control mrp" disabled hidden></td>'+
    '<td colspan="1" class="total">0.00</td>'+
    '<td colspan="1" class="total text-center"><input type="checkbox" class="is_tax"></td>'+
    '<td colspan="1" class="vt"></td>'+
    '<td colspan="1" class="vp"></td>'+
    '<td colspan="1" class="tv">0.00</td>';
    $('.details').append(data);

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
    grand_discount_type=$('.gdt').find(':selected').data('id');
    grand_discount_value=$('.gd').val();
    subtotal=parseFloat($('.subtotal_receipt').html());
    taxtotal=parseFloat($('.taxtotal_receipt').html());
    total=parseFloat($('.total_receipt').html());
    
    if (vendorid == '' || typeof(vendorid) =='undefined' || warehouseid == '' || typeof(warehouseid) == 'undefined' ||
        $.trim(invoice_no) == '' || typeof(invoice_no) =='undefined' || $.trim(date) == '' || typeof(date) =='undefined'){
        proceed = false;
    }
    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(1) input').val();
        if (product_id == '' || product_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a product ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var quantity = $(this).find('td:nth-child(4) input').val();
        if (quantity == '' || quantity =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var free = parseInt($(this).find('td:nth-child(5) input').val());

        if (isNaN(free)){
            free=0;
        }
        
        var free_tax = parseInt($(this).find('td:nth-child(6) input').val());
        if (isNaN(free_tax)){
            free_tax=0;
        }
        
        var unit_id = $(this).find('td:nth-child(8) :selected').data('id');
        if (unit_id == '' || unit_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter the purchase unit ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var purchase = $(this).find('td:nth-child(9) input').val();
        if (purchase == '' || purchase =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter the actual purchase rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var sales = $(this).find('td:nth-child(10) input').val();
        if (sales == '' || sales =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a tentative sales rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        var mrp = $(this).find('td:nth-child(11) input').val();
        
        var disc_type = $(this).find('td:nth-child(12) :selected').data('id');
        var disc = parseFloat($(this).find('td:nth-child(13) input').val());
        if (isNaN(disc)){
            disc=0;
        }
        var disc_type_2 = $(this).find('td:nth-child(14) :selected').data('id');
        var disc_2 = parseFloat($(this).find('td:nth-child(15) input').val());
        console.log(disc_2);
        if (isNaN(disc_2)){
            disc_2=0;
        }
        
        var taxable_total = $(this).find('td:nth-child(16)').html();
        var line_total = $(this).find('td:nth-child(19)').html();
        
        var item = {
            product_id : product_id,
            quantity: quantity,
            free: free,
            free_tax:free_tax,
            unit_id: unit_id,
            purchase: purchase,
            sales: sales,
            mrp: mrp,
            disc_type: disc_type,
            disc: disc,
            disc_type_2: disc_type_2,
            disc_2:disc_2,
            taxable_total:taxable_total,
            line_total: line_total,
        };
        items.push(item);
        console.log(items);
    });
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{supplier_invoice: invoice_no,
                    vendor:vendorid,
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
                        swal("Hooray", "New purchase receipt added", "success");
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
    else{
        swal("Oops...", "Please note that vendor and warehouse details must be filled."+
            "Also please check the highlightd rows", "error");
    }
}

});