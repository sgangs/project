
$(function(){

discount_types=['No Discount','Percent(%)','Value(V)' ]


function round_off(value){
    value=parseInt(value*1000)/1000
    value=parseFloat(value.toFixed(2))
    return value
}

load_data()

function load_data(){
    $.ajax({
        url : "/purchase/order/detail/", 
        type: "GET",
        data:{order_pk: pk,
            calltype: "Order Detail"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            // load_data(jsondata)
            maintain_inventory = jsondata['maintain_inventory']
            $('.details .data').remove()
            
            $('.order_pk').html(jsondata['id']);

            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.vendor').html("<strong>Vendor: </strong>"+jsondata['vendor_name']);

            $('.warehouse').html("<strong>Delivery To: </strong>"+jsondata['warehouse_address']+',<br>'
                                    +jsondata['warehouse_city']);

            $('.order_id').html("<strong>Order No: </strong>"+jsondata['order_id']);
            
            $('.subtotal_receipt').html(jsondata['subtotal']);
            $('.cgsttotal_receipt').html(jsondata['cgsttotal']);
            $('.sgsttotal_receipt').html(jsondata['sgsttotal']);
            $('.total_receipt').html(jsondata['total']);
            $('.round').val(jsondata['roundoff']);
            
            $.each(jsondata['line_items'], function(){
                if (isNaN(this.quantity_delivered)){
                    this.quantity_delivered = 0
                }
                
                $('.details').append("<tr class='data ongoing text-center'>"+

                    '<td hidden><input class="id" value='+this.product_id+' disabled></td>'+
                    '<th colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></th>'+
                    '<td colspan="3"><input class="form-control name" value="'+
                                    this.product_name+'" disabled title="'+this.product_name+'"></td>'+
                    '<td colspan="1"><input class="form-control qty" value='+(parseFloat(this.quantity) - parseFloat(this.quantity_delivered))+'></td>'+
                    // '<td colspan="1"><input class="form-control free"></td>'+
                    '<td colspan="1" hidden><input class="form-control freet"></td>'+
                    '<td colspan="1" hidden><input class="unitid">'+this.unit_id+'</td>'+
                    '<td colspan="1">'+this.unit+'</td>'+
                    '<td colspan="1"><input class="form-control pr" value ='+this.purchase_price+'></td>'+
                    '<td colspan="1"><input class="form-control tsr"></td>'+
                    '<td colspan="1"><input class="form-control mrp"></td>'+
                    '<td colspan="1">'+
                        '<select class="form-control selectpicker dt">'+
                            '<option data-id=0 title="-">No Disc.</option>'+
                            '<option data-id=1 title="%">Percent(%)</option>'+
                            '<option data-id=2 title="V">Value</option>'+
                    '</select></td>'+
                    '<td colspan="1"><input class="form-control dv" value='+(this.discount_value)+'></td>'+
                    '<td colspan="1">'+
                        '<select class="form-control selectpicker dt2">'+
                            '<option data-id=0 title="-">No Disc.</option>'+
                            '<option data-id=1 title="%">Percent(%)</option>'+
                            '<option data-id=2 title="V">Value</option>'+
                    '</select></td>'+
                    '<td colspan="1"><input class="form-control dv2" value='+(this.discount2_value)+'></td>'+
                    '<td colspan="1" class="total">'+this.line_tax+'</td>'+
                    // '<td colspan="1" class="vt"></td>'+
                    // '<td colspan="1" class="vp"></td>'+
                    '<td colspan="1"><input class="form-control cgstp" value='+this.cgst_percent+'></td>'+
                    '<td colspan="1" class="cgstv">'+this.cgst_value+'</td>'+
                    '<td colspan="1"><input class="form-control sgstp" value='+this.sgst_percent+'></td>'+
                    '<td colspan="1" class="sgstv">'+this.sgst_value+'</td>'+
                    '<td colspan="1" hidden><input class="form-control igstp" value='+this.igst_percent+'></td>'+
                    '<td colspan="1" hidden class="igstv">'+this.igst_value+'</td>'+
                    '<td colspan="1" class="tv">'+this.line_total+'</td>'+
                    '<td colspan="1" hidden>'+(parseFloat(this.quantity) - parseFloat(this.quantity_delivered))+'</td>'+
                    '<td colspan="1" hidden>'+this.id+'</td>');


                    // '<td colspan="1" class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
                    // "<td hidden>"+this.id+"</td>"+
                    // "<td hidden>"+this.product_id+"</td>"+
                    // "<td>"+this.product_name+"</td>"+
                    // "<td hidden><input class='form-control qty_avl' value="+(this.qty_avl)+" disabled></td>"+
                    // "<td><input class='form-control qty' value="+(this.quantity - this.quantity_returned)+"></td>"+
                    // "<td id='not_pos_print'>"+this.unit+"</td>"+
                    // "<td hidden>"+this.unit_multi+"</td>"+
                    // "<td id='not_pos_print' hidden>"+sales_rate.toFixed(2)+"</td>"+
                    // "<td id='not_pos_print'><input class='form-control sr' value="+sales_rate+"></td>"+
                    // // '<th class="text-center">'+this.discount_type+'</th>'+ //Disc. Type-1
                    // '<td colspan="1"><select class="form-control selectpicker dt">'+
                    //     '<option data-id=0 title="-">No Discount</option>'+
                    //     '<option data-id=1 title=%>Percent(%)</option>'+
                    //     '<option data-id=2 title="V">Value(V)</option>'+
                    //     '</select></td>'+
                    // "<td class='text-center'><input class='form-control dv' value="+(this.discount_value)+"></td>"+ //Disc. Value-1
                    // // '<th class="text-center">'+this.discount2_type+'</th>'+ //Disc. Type-2
                    // '<td colspan="1"><select class="form-control selectpicker dt2">'+
                    //     '<option data-id=0 title="-">No Discount</option>'+
                    //     '<option data-id=1 title=%>Percent(%)</option>'+
                    //     '<option data-id=2 title="V">Value(V)</option>'+
                    //     '</select></td>'+
                    // "<td class='text-center'><input class='form-control dv2' value="+(this.discount2_value)+"></td>"+ //Disc. Value-2
                    // "<td hidden>"+this.tentative_sales_price+"</td>"+
                    // "<td hidden>"+this.mrp+"</td>"+
                    // "<td id='not_pos_print'>"+this.line_tax+"</td>"+                    
                    // "<td><input class='form-control cgstp' value="+this.cgst_percent+"></td>"+
                    // "<td>"+this.cgst_value+"</td>"+
                    // "<td><input class='form-control sgstp' value="+this.sgst_percent+"></td>"+
                    // "<td>"+this.sgst_value+"</td>"+
                    // "<td class='is_igst'><input class='form-control igstp' value="+this.igst_percent+"></td>"+
                    // "<td class='is_igst'>"+this.igst_value+"</td>"+
                    // "<td>"+this.line_total+"</td>"+
                    // "</tr>");
                $('.dt').selectpicker('refresh');
                $('.dt2').selectpicker('refresh');

                updating_row=$('.details').find('.ongoing');
                $(updating_row).find('td:nth-child(11) .dt').val(discount_types[this.discount_type]);
                $(updating_row).find('td:nth-child(13) .dt2').val(discount_types[this.discount2_type]);
                $(updating_row).removeClass('ongoing');
                $('.dt').selectpicker('refresh')
                $('.dt2').selectpicker('refresh')
            });

        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No open order exist.", "error");
        }
    });
};


$(".details").on("keyup", ".qty", function(){
    var el = this;
    get_qty_avl(el);
});

function get_qty_avl(el){
    var quantity =  parseFloat($(el).closest('tr').find('td:nth-child(4) input').val());
    var quantity_avl = parseFloat($(el).closest('tr').find('td:nth-child(23)').html());
    var unit = $(el).closest('tr').find('td:nth-child(7)').html();
    
    if (!$(el).closest('tr').hasClass("has-error")){
        if ((quantity)>(quantity_avl) ){
            swal({
                title: "Oops",
                text: "Total received quantity cannot be greater than order quantity. <br>"+
                        " Order quantity: "+(quantity_avl)+" "+unit+".",
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


});