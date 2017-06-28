
$(function(){

var pk;

discount_types=['Nil','%','Val' ]


$('.get_invoice').click(function(){
    invoice_id=$('.sales_inv_no').val()
    console.log("here")
    $.ajax({
        url : "data/", 
        type: "GET",
        data:{invoice_id: invoice_id,
            calltype: "Sales Return"},
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata)
            load_data(jsondata)
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
})


function load_data(pk){
    $.ajax({
        url : "/sales/invoice/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.invoice_meta').attr('hidden', false);
            $('.details .data').remove()
            igst_total=0;
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            $('.invoiceid').append(jsondata['invoice_id']);
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append(date);
            // $('.customer').append(jsondata['customer_name']+
            //         ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']);
            $('.customer').append(jsondata['customer_name']);
            $('.warehouse').append(jsondata['warehouse_address']+',<br>'+jsondata['warehouse_city']);
            $('.subtotal_receipt').html(jsondata['subtotal']);
            $('.taxtotal_receipt').html(taxtotal.toFixed(2));
            $('.total_receipt').html(jsondata['total']);
            $.each(jsondata['line_items'], function(){
                igst_total+=this.igst_value;
                var d1_val=0.00, d2_val=0.00;
                // free_total=parseFloat(this.free_with_tax)+parseFloat(this.free_without_tax)
                pur_rate=parseFloat(this.quantity)*parseFloat(this.purchase_price)
                d1_type=this.discount_type
                d2_type=this.discount2_type
                if (d1_type == 1){
                    d1_val=(this.discount_value*pur_rate/100);
                    pur_rate-=d1_val
                }
                else if(d1_type == 2){
                    d1_val=this.discount_value;
                    pur_rate-=d1_val
                }
                if (d2_type == 1){
                    d2_val=(this.discount2_value*pur_rate/100);
                }
                else if(d2_type == 2){
                    d2_val=this.discount2_value;
                }
                
                $('.details').append("<tr class='data text-center'>"+
                    "<td>"+this.product_name+"</td>"+
                    "<td><input class='form-control qty' value="+this.quantity+"></td>"+
                    // "<td id='not_print'>"+this.free_without_tax+"</td>"+
                    // "<td id='not_print'>"+this.free_with_tax+"</td>"+
                    "<td id='not_pos_print'>"+this.unit+"</td>"+
                    // "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td id='not_pos_print'><input class='form-control sp' value="+this.sales_price+"></td>"+
                    // "<td id='not_pos_print'><input class='form-control dt1' value="+discount_types[this.discount_type]+"></td>"+
                    '<td colspan="1"><select class="form-control select dt">'+
                        '<option data-id=0 title="-">No Discount</option>'+
                        '<option data-id=1 title=%>Percent(%)</option>'+
                        '<option data-id=2 title="V">Value(V)</option>'+
                        '</select></td>'+
                    "<td id='not_pos_print'><input class='form-control dv' value="+this.discount_value+"></td>"+
                    // "<td id='not_pos_print'><input class='form-control dt2' value="+discount_types[this.discount2_type]+"></td>"+
                    '<td colspan="1"><select class="form-control selectpicker dt2">'+
                        '<option data-id=0 title="-">No Discount</option>'+
                        '<option data-id=1 title=%>Percent(%)</option>'+
                        '<option data-id=2 title="V">Value(V)</option>'+
                        '</select></td>'+
                    "<td id='not_pos_print'><input class='form-control dv2' value="+this.discount2_value+"></td>"+
                    "<td id='not_pos_print'>"+this.line_tax+"</td>"+
                    // "<td id='not_pos_print'>"+this.tax_percent+"</td>"+
                    "<td><input class='form-control dv2' value="+this.cgst_percent+"></td>"+
                    "<td>"+this.cgst_value+"</td>"+
                    "<td><input class='form-control dv2' value="+this.sgst_percent+"></td>"+
                    "<td>"+this.sgst_value+"</td>"+
                    "<td class='is_igst'><input class='form-control dv2' value="+this.igst_percent+"></td>"+
                    "<td class='is_igst'>"+this.igst_value+"</td>"+
                    "<td>"+this.line_total+"</td>"+
                    "</tr>");
                $('.dt').selectpicker('refresh');
                $('.dt2').selectpicker('refresh');
                // $('dt').val(this.discount_type);
                // $('dt2').val(this.discount2_type);
                // $('.dt').selectpicker('refresh');
                // $('.dt2').selectpicker('refresh');
            });

        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some issues in fetching the data.", "error");
        }
    });
}



});