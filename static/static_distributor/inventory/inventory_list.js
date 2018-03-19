$(function(){

var cur=0,age=0, manufac=0, manufac_id=-1;

$('.cur').hide();
$('.age').hide();
$('.manufac').hide();

// load_current_inventory()

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
            data:{calltype: 'current',
                manufacturer_id: manufac_id},
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

load_manufacturer()

function load_manufacturer(){

    $.ajax({
        url : "/master/manufacbrand/manufacdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#manufacDownload').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name
                }));
                
            });
            $('#manufacDownload').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch manufacturer data. Try again later.", "error");
        }
    });
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
            data:{calltype: 'stockwise',
                    manufacturer_id : manufac_id},
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

load_manufacturer_inventory();

function load_manufacturer_inventory(){
    $('.manufacturer').attr('hidden', false);
    $('.current').attr('hidden', true);
    $('.ageing').attr('hidden', true);
    $('.cur').hide();
    $('.age').hide();
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
    $('.cur').hide();
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


function encodeQueryData(data) {
   let ret = [];
   for (let d in data)
     ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
   return ret.join('&');
}


$('.download').click(function(e){
    $('#manufac').modal('show');
});

$('.download_manufacwise').click(function(e){
    
    var manufacturer_id=$(".manufacDownload").find(':selected').data('id');
    
    if (manufacturer_id == 'undefined' || manufacturer_id == undefined || manufacturer_id == '' 
            || typeof(manufacturer_id) == undefined || $.trim(manufacturer_id).length == 0){
        swal("Ughh...", "Kindly select a manufacturer to proceed.", "warning");
    }
    else{
        var data = { 'calltype': 'download_current', 'manufacturer_id': manufacturer_id};
        var querystring = encodeQueryData(data);
        var download_url='/inventory/getcurrentdata/?'+querystring
        location.href = download_url;
    }

});


});