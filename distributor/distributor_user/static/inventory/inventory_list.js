$(function(){

var cur=0,age=0, manufac=0;

load_current_inventory()

$('.cur').click(function(){
    load_current_inventory();
});

function load_current_inventory(){
    $('.ageing').attr('hidden', true);
    $('.cur').hide();
    $('.age').show();
    $('.manufac').show();
    $('.current').attr('hidden', false);
    $('.manufacturer').attr('hidden', true);
    if (cur == 0){
        $.ajax({
            url : "/inventory/getcurrentdata",
            type: "GET",
            data:{calltype: 'current'},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                $("#current_inventory .data").remove();
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
    $('.manufac').show();
    $('.ageing').attr('hidden', false);
    $('.manufacturer').attr('hidden', true);
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


$('.manufac').click(function(){
    load_manufacturer_inventory();
});


function load_manufacturer_inventory(){
    $('.manufacturer').attr('hidden', false);
    $('.current').attr('hidden', true);
    $('.ageing').attr('hidden', true);
    $('.cur').show();
    $('.age').show();
    $('.manufac').hide();
    if (manufac == 0){
        $.ajax({
            url : "/inventory/getcurrentdata",
            type: "GET",
            data:{calltype: 'manufacturer group'},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                manufac+=1;
                $.each(jsondata, function(){
                    $('#manufacturer_inventory').append("<tr class='data' align='center'>"+
                    "<td hidden>"+this.product__manufacturer__id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.product__manufacturer__name+"</td>"+
                    "<td>Rs "+parseFloat(this.total_value)+"</td>"+
                    "</tr>");
                })
            },
            // handle a non-successful response
            error : function() {
                swal("Oops...", "No manufacturer inventory data exist.", "error");
            }
        });
    }
};

$("#manufacturer_inventory").on("click", ".link", function(){
    // console.log('here');
    $("#current_inventory .data").remove();
    $('.manufacturer').attr('hidden', true);
    $('.current').attr('hidden', false);
    $('.ageing').attr('hidden', true);
    $('.cur').show();
    $('.age').show();
    $('.manufac').show();
    manufac_id=$(this).closest('tr').find('td:nth-child(1)').html();
    $.ajax({
        url : "/inventory/getcurrentdata",
        type: "GET",
        data:{calltype: 'manufacturer products',
            manufac_id: manufac_id,},
        dataType: 'json',
            // handle a successful response
        success : function(jsondata) {
            cur=0;
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
});


});