$(function(){

var cur=0,age=0;

load_current_inventory()

$('.cur').click(function(){
    load_current_inventory();
});

function load_current_inventory(){
    $('.ageing').attr('hidden', true);
    $('.cur').hide();
    $('.age').show();
    $('.current').attr('hidden', false);
    if (cur == 0){
        $.ajax({
            url : "/inventory/getcurrentdata",
            type: "GET",
            data:{calltype: 'current'},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                cur+=1;
                $.each(jsondata, function(){
                    if ($.trim(this.expiry_date).length>3){
                        var expiry_date = moment(new Date(this.expiry_date)).format('DD/MM/YYYY');
                    }
                    $('#current_inventory').append("<tr class='data' align='center'>"+
                    "<td hidden='true'></td>"+
                    "<td>"+this.product__name+"</td>"+
                    "<td>"+this.product__sku+"</td>"+
                    "<td>"+$.trim(expiry_date)+"</td>"+
                    "<td>"+$.trim(this.warehouse__address_1)+","+$.trim(this.warehouse__address_2)+","+
                            $.trim(this.warehouse__city)+"</td>"+
                    "<td>Rs. "+this.purchase_price+"</td>"+
                    "<td>"+this.available+"</td>"+
                    "<td>Rs "+Math.round(this.available*this.purchase_price)+"</td>"+
                    "</tr>");
                })
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "No product inventory exist.", "error");
            }
        });
    }
}

// load_current_inventory()

$('.age').click(function(){
    load_ageing_inventory();
});

function load_ageing_inventory(){
    $('.current').attr('hidden', true);
    $('.cur').show();
    $('.age').hide();
    $('.ageing').attr('hidden', false);
    if (age == 0){
        $.ajax({
            url : "/inventory/getcurrentdata",
            type: "GET",
            data:{calltype: 'stockwise'},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                age+=1;
                $.each(jsondata, function(){
                    var purchase_date = moment(new Date(this.purchase_date)).format('DD/MM/YYYY');
                    if ($.trim(this.expiry_date).length>3){
                        var expiry_date = moment(new Date(this.expiry_date)).format('DD/MM/YYYY');
                    }
                    $('#ageing_inventory').append("<tr class='data' align='center'>"+
                    "<td hidden='true'></td>"+
                    "<td>"+this.product__name+"</td>"+
                    "<td>"+this.product__sku+"</td>"+
                    "<td>"+$.trim(purchase_date)+"</td>"+
                    "<td>"+$.trim(expiry_date)+"</td>"+
                    "<td>"+$.trim(this.warehouse__address_1)+","+$.trim(this.warehouse__address_2)+","+
                            $.trim(this.warehouse__city)+"</td>"+
                    "<td>Rs. "+this.purchase_price+"</td>"+
                    "<td>"+this.available+"</td>"+
                    "<td>Rs "+Math.round(this.available*this.purchase_price)+"</td>"+
                    "</tr>");
                })
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "No product inventory exist.", "error");
            }
        });
    }
}



});