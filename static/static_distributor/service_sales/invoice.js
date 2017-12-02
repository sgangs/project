$(function(){
var salespersons, salespersons_id = {}, unit_data, unit_multi={}, maintain_inventory, unit_names={}, count=0;

function round_off(value){
    value=parseInt(value*1000)/1000
    value=parseFloat(value.toFixed(2))
    return value
}


$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "api/getproduct", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            // console.log(ui['item']);
            maintain_inventory=ui['item']['inventory']
            $(el).closest('tr').addClass("updating");
            $(el).closest('tr').find('td:nth-child(1) input').val(ui['item']['id']);
            // $(el).closest('tr').find('td:nth-child(6) input').val(ui['item']['unit']);
            // $(el).closest('tr').find('td:nth-child(7)').html(ui['item']['unit_id']);
            $(el).closest('tr').find('td:nth-child(6) .unit').val(ui['item']['unit_id']);
            $(el).closest('tr').find('td:nth-child(7)').html(unit_multi[ui['item']['unit_id']]);
            // $(el).closest('tr').find('td:nth-child(12) input').val(ui['item']['cgst']);
            // $(el).closest('tr').find('td:nth-child(14) input').val(ui['item']['sgst']);
            get_product_rate(el, ui['item']['id']);
            $('.unit').selectpicker('refresh');
        }
    });
});

function get_product_rate(el, product_id){
    warehouse_id=$('.warehouse').find(':selected').data('id');
    $.ajax({
        url : "api/getproductrate", 
        type: "GET",
        data:{product_id: product_id,
            warehouse_id: warehouse_id},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            updating_row=$('.details').find('.updating')
            // console.log(jsondata['rate'][0]['tentative_sales_rate']);
            if (jsondata['rate'][0]){
                console.log('here')
                // $(updating_row).find('td:nth-child(5)').html(jsondata['quantity']);
                $(updating_row).find('td:nth-child(8) input').val(jsondata['rate'][0]['tentative_sales_rate']);
                $(updating_row).find('td:nth-child(11)').html(jsondata['rate'][0]['is_tax_included']);
                $(updating_row).find('td:nth-child(12) input').val(jsondata['cgst']);
                $(updating_row).find('td:nth-child(14) input').val(jsondata['sgst']);
            }
            else{
                console.log('here')
                $(updating_row).find('td:nth-child(5)').html(jsondata['quantity']);
                // $(updating_row).find('td:nth-child(8) input').val(jsondata['rate'][0]['tentative_sales_rate']);
                $(updating_row).find('td:nth-child(11)').html(false);
                $(updating_row).find('td:nth-child(12) input').val(jsondata['cgst']);
                $(updating_row).find('td:nth-child(14) input').val(jsondata['sgst']);
            }
            $(updating_row).removeClass('updating');
            
            // May have to consider multiple sales rate

            // $(".prod_data .prod_indi_data").remove();
            // $.each(jsondata, function(){
            //     $('.prod_data').append("<tr class='prod_indi_data'>"+
            //     "<td class='prod_tsp'>"+this.tentative_sales_price +"</td>"+
            //     "<td class='prod_mrp'>"+this.mrp+"</td>"+
            //     "<td class='prod_qa'>"+this.available+"</td>"+
            //     "<td class='prod_qa'>"+default_unit+"</td>"+
            //     "</tr>");
            // })
            // $('#productdetails').modal('show');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product inventory exist.", "error");
        }
    });
}

// $('.prod_data').on('click','.prod_indi_data', function(){
//     // console.log('clicked');
//     updating_row=$('.details').find('.updating')
//     mrp=$(this).closest('tr').find('td:nth-child(2)').html()
//     tsp=$(this).closest('tr').find('td:nth-child(1)').html()
//     qty_avl=$(this).closest('tr').find('td:nth-child(3)').html()
//     $(updating_row).find('td:nth-child(5)').html(qty_avl);
//     $(updating_row).find('td:nth-child(8)').html(tsp);
//     $(updating_row).find('td:nth-child(9)').html(mrp);
//     $(updating_row).find('td:nth-child(10) input').val(tsp);
//     $(updating_row).removeClass('updating');
//     $('#productdetails').modal('hide');
//     // console.log(mrp)
// });



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

load_salesperson()

function load_salesperson(){
    $.ajax({
        url : "/servicesales/getsalesusers/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            salespersons=jsondata
            $.each(jsondata, function(){
                salespersons_id [this.id] = this.first_name + " "+ this.last_name
            });
            // $.each(jsondata, function(){
            //     $('#warehouse').append($('<option>',{
            //         'data-id': this.id,
            //         'text': this.address_1 + " "+ this.address_2
            //     }));
            // });
            // $('#warehouse').selectpicker('refresh')
        },
        // handle a non-successful response
        error : function() {
            // swal("Oops...", "No warehouse data exist.", "error");
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
    if (maintain_inventory){
        get_qty_avl(el);
    }
});
$(".details").on("keydown", ".qty", function(){
    var el=this;
    get_total();
    if (maintain_inventory){
        get_qty_avl(el);
    }
});


$(".details").on("keyup", ".sr", function(){
    get_total();
});
$(".details").on("keydown", ".sr", function(){
    get_total();
});

$(".details").on("keyup", ".dv", function(){
    get_total();
});

$(".details").on("keydown", ".dv", function(){
    get_total();
});

$(".details").on("click", ".add_user", function(){
    var el = $(this);
    count = parseInt($(el).closest('tr').find('td:nth-child(18)').html());
    if (count <3){
        $('#selectsales').empty();
        $('#selectsales').selectpicker('refresh')

        $(el).closest('tr').addClass("adding_user");
        $.each(salespersons, function(){
            $('#selectsales').append($('<option>',{
                'data-id': this.id,
                'text': this.first_name + " "+ this.last_name
            }));
        });
        $(".saleslineinput .datainput").remove();
        $('#selectsales').selectpicker('refresh')
        if (count ==1){
            salesman1_id = $(el).closest('tr').find('td:nth-child(19)').html();
            salesman1_contrib = $(adding_user_row).find('td:nth-child(20)').html();
            $('.saleslineinput').append("<tr class='datainput'>"+
                "<td>"+salespersons_id[salesman1_id] +"</td>"+
                "<td>"+salesman1_contrib+"</td>"+
            "</tr>");

        }
        else if (count ==2){
            salesman1_id = $(el).closest('tr').find('td:nth-child(19)').html();
            salesman1_contrib = $(adding_user_row).find('td:nth-child(20)').html();
            
            salesman2_id = $(el).closest('tr').find('td:nth-child(21)').html();
            salesman2_contrib = $(adding_user_row).find('td:nth-child(22)').html();
            
            $('.saleslineinput').append("<tr class='datainput'>"+
                "<td>"+salespersons_id[salesman1_id] +"</td>"+
                "<td>"+salesman1_contrib+"</td>"+
            "</tr>");
            $('.saleslineinput').append("<tr class='datainput'>"+
                "<td>"+salespersons_id[salesman2_id] +"</td>"+
                "<td>"+salesman2_contrib+"</td>"+
            "</tr>");

        }
        $('#salesperson').modal('show');
    }
    else{
        swal("Ugggh...", "Only 3 salesperson per service can be added. ", "warning");
    }
});

$('.submituser').click(function(){
    var salesman = $('.selectsales').find(':selected').data('id');
    var salesValue =  $('.sales_value').val();
    adding_user_row=$('.details').find('.adding_user')
    if (count == 0){
        $(adding_user_row).find('td:nth-child(18)').html(1);
        $(adding_user_row).find('td:nth-child(19)').html(salesman);
        $(adding_user_row).find('td:nth-child(20)').html(salesValue);
        count = 1
    }
    else if (count == 1){
        $(adding_user_row).find('td:nth-child(18)').html(2);
        $(adding_user_row).find('td:nth-child(21)').html(salesman);
        $(adding_user_row).find('td:nth-child(22)').html(salesValue);
        count = 2
    }
    else if (count == 2){
        $(adding_user_row).find('td:nth-child(18)').html(3);
        $(adding_user_row).find('td:nth-child(23)').html(salesman);
        $(adding_user_row).find('td:nth-child(24)').html(salesValue);
        count = 3
    }
    else{
        swal("Oops...", "There were some errors. ", "error");
    }
    $(adding_user_row).removeClass('adding_user');
    $('#salesperson').modal('hide');
});



$(".details").on("change", ".unit", function(){
    var unit_id = $(this).find(':selected').data('id');
    unit_multi_selected=unit_multi[unit_id]
    $(this).closest('tr').find('td:nth-child(7)').html(unit_multi_selected);
    // get_total();
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
        // free=0;
    // }
    // var free_tax = parseInt($(el).closest('tr').find('td:nth-child(7) input').val());
    // if (isNaN(free_tax)){
        // free_tax=0;
    // }
    var unit_multi_selected = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());
    quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            // var unit_symbol=$(el).closest('tr').find('td:nth-child(6) input').val();
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
    var i =0;
    for (var a = document.querySelectorAll('table.details tbody tr'), i = 0; a[i]; ++i) {
        // get all cells with input field
        cells = a[i].querySelectorAll('input:last-child');

        var quantity=parseFloat($(cells[2]).val());
        var qty_avl=parseFloat($(a[i]).find('td:nth-child(5)').html());
        
        var sales_rate=$(cells[3]).val()
        
        // discount_type=$(a[i]).find('td:nth-child(11) :selected').data('id');
        // discount_val=$(cells[4]).val();
        discount_amt=$(cells[4]).val();
        
        cgst_percent=parseFloat($(cells[5]).val());
        sgst_percent=parseFloat($(cells[6]).val());

        if(isNaN(cgst_percent)){
            cgst_percent=0;
        }
        if(isNaN(sgst_percent)){
            sgst_percent=0;
        }
        
        if(isNaN(sales_rate)){
            sales_rate=0;
        }
        if(isNaN(quantity)){
            quantity=0;
        }
        
        var this_total=quantity*sales_rate
        
        // sales_disc_rate=sales_rate
        
        // if(discount_type == 2){
        //     sales_disc_rate=sales_disc_rate - discount_val/quantity;
        //     this_total=(this_total - discount_val);
        // }
        is_tax=$(a[i]).find('td:nth-child(11)').html()

        discount_amt=$(a[i]).find('td:nth-child(9) input').val()
        
        // sales_disc_rate=sales_disc_rate - discount_val/quantity;
        this_total=(this_total - discount_amt);

        // console.log(i+": "+is_tax)
        
        if (is_tax) {
            total_tax_per=cgst_percent+sgst_percent
            total_tax_divider=(100+total_tax_per)/100
            tax_total=round_off(this_total-this_total/total_tax_divider)
            cgst_total=round_off(tax_total/2);
            sgst_total=round_off(tax_total/2);
            this_final_total=round_off(this_total);
            total+=this_final_total
            subtotal+=this_final_total-(cgst_total+ sgst_total)
            this_total = this_total - (cgst_total+ sgst_total)
        }
        else{
            cgst_total=round_off((this_total*cgst_percent)/100);
            sgst_total=round_off((this_total*sgst_percent)/100);
            tax_total = cgst_total+sgst_total;
            this_final_total=this_total+cgst_total+sgst_total;
            total+=this_final_total
            subtotal+=this_final_total-tax_total
        }
        // console.log(i+": "+tax_total)
        // console.log(i+": "+total)
        
        $(a[i]).find('td:nth-child(13) ').html(cgst_total.toFixed(2))
        $(a[i]).find('td:nth-child(15) ').html(sgst_total.toFixed(2))
        
        $(a[i]).find('td:nth-child(10) ').html(this_total.toFixed(2))
        
        $(a[i]).find('td:nth-child(16) ').html(this_final_total.toFixed(2))
        
    }
    // console.log(total)
    // console.log(subtotal)
    subtotal = round_off(subtotal)
    total = round_off(total)
    
    $('.subtotal_receipt').html(subtotal.toFixed(2))
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
    '<td colspan="1"><select class="form-control selectpicker unit" id="unit"></select></td>'+
    '<td colspan="1" class="unit_id" hidden></td>'+
    '<td colspan="1"><input class="form-control sr"></td>'+
    '<td colspan="1"><input class="form-control da"></td>'+
    '<td colspan="1" class="total" hidden>0.00</td>'+
    '<td colspan="1" hidden class="is_tax"></td>'+
    '<td colspan="1" class="cgstp" hidden><input class="form-control dv2"></td>'+
    '<td colspan="1" class="cgstv" hidden></td>'+
    '<td colspan="1" class="sgstp" hidden><input class="form-control dv2"></td>'+
    '<td colspan="1" class="sgstv" hidden></td>'+
    '<td colspan="1" class="tv">0.00</td>'+
    '<td colspan="1" class="add_user">Click To Add User</td>'+
    '<td colspan="1" class="count" hidden>0</td>'+
    '<td colspan="1" class="per1" hidden></td>'+
    '<td colspan="1" class="per1_val" hidden></td>'+
    '<td colspan="1" class="per2" hidden></td>'+
    '<td colspan="1" class="per2_val" hidden></td>'+
    '<td colspan="1" class="per3" hidden></td>'+
    '<td colspan="1" class="per3_val" hidden></td>'+
    '</tr>'
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
    var cgst_total_sum=0
    var sgst_total_sum=0
    var items=[];
    var proceed=true;
    customer_phone=$('.cust_phone').val();
    customer_name=$('.cust_name').val();
    customer_address=$('.cust_address').val();
    customer_email=$('.cust_email').val();
    customer_gender=$('.cust_gender').find(':selected').data('id');
    customer_dob=$('.cust_dom').val();

    warehouseid=$('.warehouse').find(':selected').data('id');
    date=$('.date').val()
    subtotal=parseFloat($('.subtotal_receipt').html());
    // taxtotal=parseFloat($('.taxtotal_receipt').html());
    total=parseFloat($('.total_receipt').html());
    if (warehouseid == '' || typeof(warehouseid) =='undefined'){
        proceed = false;
        swal("Oops...", "Please select a warehouse. ", "error");
    }
    $(".details tr.data").each(function() {
        var product_id = $(this).find('td:nth-child(1) input').val();
        if (product_id == '' || product_id =='undefined'){
            proceed=false;
            swal("Oops...", "Please enter a product ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        var quantity = parseFloat($(this).find('td:nth-child(4) input').val());
        // var quantity_avl = parseFloat($(this).find('td:nth-child(5)').html());
        // if (isNaN(quantity)){
        //     proceed=false;
        //     swal("Oops...", "Please enter a quantity ", "error");
        //     $(this).closest('tr').addClass("has-error");
        // }

        
        // if (maintain_inventory){
        //     var qty_proceed= get_qty_avl(this);
        //     if (!qty_proceed){
        //         swal("Oops...", "You don't have enough quantity available. ", "error");
        //         proceed=false;
        //     }
        // }

        var unit_id = $(this).find('td:nth-child(6) :selected').data('id');
        
        var sales = parseFloat($(this).find('td:nth-child(8) input').val());
        if (isNaN(sales)){
            proceed=false;
            swal("Oops...", "Please enter a sales rate ", "error");
            $(this).closest('tr').addClass("has-error");
        }
        
        // var disc_type = $(this).find('td:nth-child(11) :selected').data('id');
        // var disc = parseFloat($(this).find('td:nth-child(12) input').val());
        // if (isNaN(disc)){
        //     disc=0;
        // }

        var disc_amt = parseFloat($(this).find('td:nth-child(9) input').val());

        if (isNaN(disc_amt)){
            disc_amt=0
        }


        var is_tax = $(this).find('td:nth-child(11)').html();

        var cgst_p = parseFloat($(this).find('td:nth-child(12) input').val());
        var cgst_v = parseFloat($(this).find('td:nth-child(13)').html());
        if (isNaN(cgst_p)){
            cgst_p=0;
            cgst_v=0;
        }
        cgst_total_sum+=cgst_v
        var sgst_p = parseFloat($(this).find('td:nth-child(14) input').val());
        var sgst_v = parseFloat($(this).find('td:nth-child(15)').html());
        if (isNaN(sgst_p)){
            sgst_p=0;
            sgst_v=0;
        }
        sgst_total_sum+=sgst_v
        
        var line_total = $(this).find('td:nth-child(16)').html();

        var taxable_total = line_total - cgst_v - sgst_v;
        var sales_before_tax = round_off(taxable_total/quantity); 

        var count = $(this).find('td:nth-child(18)').html();

        salesman1_id = $(this).find('td:nth-child(19)').html();
        salesman1_contrib = $(this).find('td:nth-child(20)').html();
            
        salesman2_id = $(this).find('td:nth-child(21)').html();
        salesman2_contrib = $(this).find('td:nth-child(22)').html();

        salesman3_id = $(this).find('td:nth-child(23)').html();
        salesman3_contrib = $(this).find('td:nth-child(24)').html();
        
        var sales_list=[];
        
        if (count == 1) {

            sales_list.push({"id" : salesman1_id,  "cont" : salesman1_contrib});    
        }

        else if (count == 2) {

            sales_list.push({"id" : salesman1_id, "cont" : salesman1_contrib})
            sales_list.push({"id" : salesman2_id, "cont" : salesman2_contrib})    
        }

        else if (count == 3) {

            sales_list.push({"id" : salesman1_id, "cont" : salesman1_contrib})
            sales_list.push({"id" : salesman2_id, "cont" : salesman2_contrib})
            sales_list.push({"id" : salesman3_id, "cont" : salesman3_contrib})
        }

        
        var item = {
            product_id : product_id,
            quantity: quantity,
            unit_id: unit_id,
            sales_before_tax: sales_before_tax,
            discount_amount: disc_amt,
            cgst_p: cgst_p,
            cgst_v:cgst_v,
            sgst_p: sgst_p,
            sgst_v: sgst_v,
            taxable_total: taxable_total,
            line_total: line_total,
            is_tax: is_tax,
            salespersons: sales_list,
        };
        items.push(item);
    });

    cgst_total_sum = round_off(cgst_total_sum);
    sgst_total_sum = round_off(sgst_total_sum);
    
    console.log(items);
    
    if (proceed){
        (function() {
            $.ajax({
                url : "save/" , 
                type: "POST",
                data:{customer_phone:customer_phone,
                    customer_name:customer_name,
                    customer_address:customer_address,
                    customer_gender:customer_gender,
                    customer_dob,customer_dob,
                    customer_email,customer_email,
                    warehouse:warehouseid,
                    subtotal: subtotal,
                    cgsttotal: cgst_total_sum,
                    sgsttotal: sgst_total_sum,
                    // is_tax: is_tax,
                    total: total,
                    bill_details: JSON.stringify(items),
                    calltype: "save",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                
                success : function(jsondata) {
                    var show_success=true
                    if (jsondata['id']){
                        swal("Hooray", "New sale invoice generated", "success");
                        var url='/servicesales/invoice/productdetailview/'+jsondata['pk']+'/'
                        location.href = url;
                        // setTimeout(location.reload(true),1000);
                    }
                    else{
                        swal("Oops...", jsondata, "error");
                    }
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