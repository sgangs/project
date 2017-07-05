$(function(){
vat_type=["No VAT", "On MRP", "On actual"];
vat_type_reverse={"No VAT":0, "On MRP":1, "On actual":2};
var vat_input, vat_percent, unit_data, unit_multi={}, unit_names={};

$(document).on('keydown.autocomplete', '.name', function() {
    var el=this;
    $(this).autocomplete({
        source : "api/getproduct", 
        minLength: 3,
        timeout: 200,
        select: function( event, ui ) {
            // console.log(ui['item']);
            $(el).closest('tr').addClass("updating");
            $(el).closest('tr').find('td:nth-child(1) input').val(ui['item']['id']);
            $(el).closest('tr').find('td:nth-child(6) input').val(ui['item']['unit']);
            $(el).closest('tr').find('td:nth-child(7)').html(ui['item']['unit_id']);
            $(el).closest('tr').find('td:nth-child(12) input').val(ui['item']['cgst']);
            $(el).closest('tr').find('td:nth-child(14) input').val(ui['item']['sgst']);
            get_product_rate(el, ui['item']['id'])
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
            // console.log(jsondata['rate']);
            // console.log(jsondata['rate'][0]['tentative_sales_rate']);
            
            $(updating_row).find('td:nth-child(5)').html(jsondata['quantity']);
            $(updating_row).find('td:nth-child(8) input').val(jsondata['rate'][0]['tentative_sales_rate']);
            $(updating_row).find('td:nth-child(11)').html(jsondata['rate'][0]['is_tax_included']);
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

// load_units()
// load_customers()

// function load_customers(){
//     $.ajax({
//         url : "/master/customer/getdata/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             $.each(jsondata, function(){
//                 $('#customer').append($('<option>',{
//                     'data-id': this.id,
//                     'text': this.name + ": "+ this.key
//                 }));
//             });
//             $('#customer').selectpicker('refresh')
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Oops...", "No customer data exist.", "error");
//         }
//     });
// }

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



function get_qty_avl(el){
    // var unit_id = $(el).closest('tr').find('td:nth-child(6) .unit :selected').data('id');
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
    // var unit_multi_selected = parseFloat($(el).closest('tr').find('td:nth-child(7)').html());
    // quantity_avl=quantity_avl/unit_multi_selected;
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>quantity_avl ){
            var unit_symbol=$(el).closest('tr').find('td:nth-child(6) input').val();
            swal({
                title: "Oops",
                text: "Total Invoiced Quantity cannot be greater than available quantity. <br>"+
                        " Total available quantity: "+quantity_avl+" "+unit_symbol+".",
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
        
        var sales_rate=$(cells[4]).val()
        
        // discount_type=$(a[i]).find('td:nth-child(11) :selected').data('id');
        // discount_val=$(cells[4]).val();
        discount_amt=$(cells[5]).val();
        
        cgst_percent=parseFloat($(cells[6]).val());
        sgst_percent=parseFloat($(cells[7]).val());

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
            tax_total=this_total-this_total/total_tax_divider
            cgst_total=tax_total/2;
            sgst_total=tax_total/2;
            this_final_total=this_total
            total+=this_final_total
            subtotal+=this_final_total-tax_total
            this_total = this_total - tax_total
        }
        else{
            cgst_total=(this_total*cgst_percent)/100;
            sgst_total=(this_total*sgst_percent)/100;
            tax_total = cgst_total+sgst_total
            this_final_total=this_total+cgst_total+sgst_total
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
    '<td colspan="1"><input class="form-control unit_symbol"></td>'+
    '<td colspan="1" class="unit_id" hidden></td>'+
    '<td colspan="1"><input class="form-control sr"></td>'+
    '<td colspan="1"><input class="form-control da"></td>'+
    '<td colspan="1" class="total" hidden>0.00</td>'+
    '<td colspan="1" hidden class="is_tax"></td>'+
    '<td colspan="1" hidden><input class="form-control cgstp"></td>'+
    '<td colspan="1" hidden class="cgstv" ></td>'+
    '<td colspan="1" hidden><input class="form-control sgstp"></td>'+
    '<td colspan="1" hidden class="sgstv"></td>'+
    '<td colspan="1" class="tv">0.00</td></tr>'
    $('.details').append(data);

    // $('.dt').selectpicker('refresh');
    // $('.dt2').selectpicker('refresh');
    
    
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
        var quantity_avl = parseFloat($(this).find('td:nth-child(5)').html());
        if (isNaN(quantity)){
            proceed=false;
            swal("Oops...", "Please enter a quantity ", "error");
            $(this).closest('tr').addClass("has-error");
        }

        
        var qty_proceed= get_qty_avl(this);
        if (!qty_proceed){
            swal("Oops...", "You don't have enough quantity available. ", "error");
            proceed=false;
        }

        var unit_id = $(this).find('td:nth-child(7)').html();

        
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

        var taxable_total = line_total - cgst_v - sgst_v
        
        var item = {
            product_id : product_id,
            quantity: quantity,
            unit_id: unit_id,
            sales: sales,
            discount_amount: disc_amt,
            cgst_p: cgst_p,
            cgst_v:cgst_v,
            sgst_p: sgst_p,
            sgst_v: sgst_v,
            taxable_total: taxable_total,
            line_total: line_total,
        };
        items.push(item);
    });
    // console.log(items)
    // console.log(customer_name)
    console.log(cgst_total_sum)
    console.log(sgst_total_sum)
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
                    // taxtotal: taxtotal,
                    total: total,
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
                        // var url='/sales/invoice/detailview/'+jsondata+'/'
                        // location.href = url;
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
        // swal("Oops...", "Please note that vendor and warehouse details must be filled."+
        //     "Also please check the highlightd rows", "error");
    }
}

});