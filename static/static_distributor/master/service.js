$(function(){

var has_attribute=false, attr_name, service_name, sku, reorder, unit, brand, group, has_batch,tax_array={}, group_array={},
    has_instance;



// var tax_array={};

load_services()

function load_services(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                // var url='/inventory/barcode/'+this.id+'/'
                // console.log(url)
                if ($.trim(this.rates).length>0){
                    $('#product_table').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.name+"</td>"+
                    "<td>"+$.trim(this.hsn_code)+"</td>"+
                    "<td>"+this.sku+"</td>"+
                    "<td>"+$.trim(this.default_unit)+"</td>"+
                    // "<td>"+$.trim(this.brand)+"</td>"+
                    "<td>"+$.trim(this.group)+"</td>"+
                    // "<td>"+$.trim(this.remarks)+"</td>"+
                    "<td class='rate'>"+$.trim(this.rates[0].tentative_sales_rate)+"</td>"+
                    "<td hidden>"+$.trim(this.rates[0].id)+"</td>"+
                    "<td hidden>"+$.trim(this.rates[0].is_tax_included)+"</td>"+
                    "<td class='add_price'>Click to add sales rate</td>"+
                    // "<td class='barcode'><a href="+url+">Click to download barcode</a></td>"+
                    "</tr>");
                }
                else{
                    $('#product_table').append("<tr class='data' align='center'>"+
                    "<td hidden='true'>"+this.id+"</td>"+
                    "<td class='link' style='text-decoration: underline; cursor: pointer'>"+this.name+"</td>"+
                    "<td>"+$.trim(this.hsn_code)+"</td>"+
                    "<td>"+this.sku+"</td>"+
                    "<td>"+$.trim(this.default_unit)+"</td>"+
                    // "<td>"+$.trim(this.brand)+"</td>"+
                    "<td>"+$.trim(this.group)+"</td>"+
                    // "<td>"+$.trim(this.remarks)+"</td>"+
                    "<td class='rate'></td>"+
                    "<td hidden></td>"+
                    "<td hidden></td>"+
                    "<td class='add_price'>Click to add sales rate</td>"+
                    // "<td class='barcode'><a href="+url+">Click to download barcode</a></td>"+
                    "</tr>");   
                }
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No product is recorded yet.", "error");
        }
    });
}

load_unit()

function load_unit(){
    $.ajax({
        url : "/master/dimensionunit/unitdata/onlybase", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                    $('#unit').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.name
                        }));
                    $('#unit').selectpicker('refresh')
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No unit data exist.", "error");
        }
    });
}

load_tax()

function load_tax(){
    $.ajax({
        url : "/master/tax/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                tax_array[this.name]=this.id;
                $('#tax_cgst').append($('<option/>',{
                    'data-id': this.id,
                    'text': this.name
                }));
                $('#tax_sgst').append($('<option/>',{
                    'data-id': this.id,
                    'text': this.name
                }));
                $('#tax_igst').append($('<option/>',{
                    'data-id': this.id,
                    'text': this.name
                }));
                $('#cgst_data_prod').append($('<option/>',{
                    'value': this.id,
                    'text': this.name
                }));
                $('#sgst_data_prod').append($('<option/>',{
                    'value': this.id,
                    'text': this.name
                }));
                $('#igst_data_prod').append($('<option/>',{
                    'value': this.id,
                    'text': this.name
                }));
            })
            $('#tax_cgst').selectpicker('refresh');
            $('#tax_sgst').selectpicker('refresh');
            $('#tax_igst').selectpicker('refresh');
            // $('#cgst_data_prod').selectpicker('refresh');
            // $('#sgst_data_prod').selectpicker('refresh');
            // $('#igst_data_prod').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No tax data exist.", "error");
        }
    });
}

load_group()

function load_group(){
    $.ajax({
        url : "/master/servicegroup/data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                group_array[this.name]=this.id;
                $('#group').append($('<option/>',{
                    'data-id': this.id,
                    'text': this.name
                }));

                $('#group_edit').append($('<option/>',{
                    'value': this.id,
                    'text': this.name
                }));

            })
            $('#group').selectpicker('refresh');
            // $('#group_edit').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No service group data exist.", "error");
        }
    });
}

// load_attribute()

// function load_attribute(){
//     $.ajax({
//         url : "attributedata/", 
//         type: "GET",
//         dataType: 'json',
//         // handle a successful response
//         success : function(jsondata) {
//             attr_values=jsondata;
//             $.each(attr_values, function(){
//                     $('#selattr0').append($('<option/>',{
//                         'data-id': this.id,
//                         'text': this.name
//                         }));                    
//             })
//         },
//         // handle a non-successful response
//         error : function() {
//             swal("Hmm...", "No attribute data exist.", "error");
//         }
//     });
// }


// $("#product_table").on("click", ".barcode", function(){
//     var newurl=$(this).closest('tr').find('td:nth-child(13) a').attr('href');
//     $('a.barcodetag').attr('href', newurl);
//     productid=$(this).closest('tr').find('td:nth-child(1)').html();
//     productname=$(this).closest('tr').find('td:nth-child(2)').html();
//     $('.id_barcode').val(productid)
//     $('.name_barcode').val(productname)
//     $('#modal_barcode').modal('show');
//     // console.log(newurl);
// });

$("#product_table").on("click", ".rate", function(){
    var prod_id=$(this).closest('tr').find('td:nth-child(1)').html();
    var name=$(this).closest('tr').find('td:nth-child(2)').html();
    var rate=$(this).closest('tr').find('td:nth-child(7)').html();
    var rate_id=$(this).closest('tr').find('td:nth-child(8)').html();
    var rate_is_tax=$(this).closest('tr').find('td:nth-child(9)').html();
    $('.product_name_update').html(name);
    $('.retail_rate_update').val(rate);
    $('.product_id_rate_update').html(prod_id);
    $('.retail_rate_id').html(rate_id);

    $('.is_tax_update').prop('checked', rate_is_tax);

    $('#retailRate').modal('show');
});

$('.update_rate').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to update the service rate?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update service rate!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){update_rate()},600)
            // console.log("rate update called")            
        }
    })
});


function update_rate(){
    var proceed=true;
    new_rate=parseFloat($('.retail_rate_update').val());
    if (isNaN(new_rate) || new_rate<0){
        proceed = false;
        swal("Oops...", "Retail Sales Rate must be a number greater than zero.", "error");
    }
    rate_id = $('.retail_rate_id').html();
    serviceid = $('.product_id_rate_update').html();
    is_tax = $('.is_tax_update').is(":checked");
    // var is_present = $(this).find('td:nth-child(6) input').is(":checked");
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{new_rate: new_rate,
                    rate_id: rate_id,
                    is_tax: is_tax,
                    serviceid: serviceid,
                    calltype: "updaterate",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Product retail sales rate updated", "success");
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
}


// $( ".has_attribute" ).change(function() {
//     has_attribute = $( ".has_attribute" ).is(":checked");
//     if (has_attribute){
//         $('#attribute_details').prop('hidden',false);
//     }
//     else{
//         $('#attribute_details').prop('hidden',true);        
//     }
// });



// var next = 0;
//     $("#add-more").click(function(e){
//         e.preventDefault();
//         var addto = "#attr" + next;
//         var addRemove = "#attr" + next;
//         next = next + 1;
//         var newIn = ' <div id="attr'+ next +'" class="attr"><br>'+
//             '<div class="form-group"><label class="control-label">Select Attribute</label>'+
//             '<select class="form-control select attribute" id="selattr'+next+'"">'+
//             '<option disabled selected hidden style="display: none" value>Select Attribute</option></select></div>'+
//             '<div class="form-group"><label class="control-label">Attribute Value</label>'+
//             '<input type="text" class="form-control value" placeholder="If arribute is colour, value can be: Blue, White, etc.">'+
//             '</div></div>';
//         var newInput = $(newIn);
//         var removeBtn = '<button id="remove'+(next - 1)+'"class="btn btn-danger btn-xs remove-me">Remove Attribute</button>';
//         var removeButton = $(removeBtn);
//         $(addto).after(newInput);
//         $(addRemove).after(removeButton);
//         $("#attr" + next).attr('data-source',$(addto).attr('data-source'));
//         $("#count").val(next);
//         $.each(attr_values, function(){
//             $('#selattr'+next).append($('<option/>',{
//             'data-id': this.id,
//             'text': this.name
//             }));                    
//         })
        
//         $('.remove-me').click(function(e){
//             e.preventDefault();
//             var attrNum = this.id.charAt(this.id.length-1);
//             var attrID = "#attr" + attrNum;
//             $(this).remove();
//             $(attrID).remove();
//         });
//     });


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new service?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new service!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_service()},600)            
        }
    })
});

function new_service(){
    var proceed=true, attributes=[];
    service_name=$('.name').val()
    sku=$('.sku').val()
    // barcode=$('.barcode_new').val()
    hsn=$('.hsn').val()
    // vat_type=$(".vattype").find(':selected').data('id');
    // tax=$(".tax").find(':selected').data('id');
    cgst=$(".cgst").find(':selected').data('id');
    sgst=$(".sgst").find(':selected').data('id');
    igst=$(".igst").find(':selected').data('id');
    unit=$(".unit").find(':selected').data('id');
    // brand=$(".brand").find(':selected').data('id');
    group=$(".group").find(':selected').data('id');
    // has_batch = $( ".has_batch" ).is(":checked");
    // has_instance = $( ".has_instance" ).is(":checked");
    
    if (service_name == '' || service_name =='undefined' || sku == '' || sku =='undefined' || unit == '' || typeof(unit) =='undefined'){
        proceed = false;
        swal("Oops...", "Service must have a name, sku/product code and default unit.", "error");
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{name: service_name,
                    sku: sku,
                    hsn: hsn,
                    // barcode: barcode,
                    // tax:tax,
                    cgst:cgst,
                    sgst:sgst,
                    igst:igst,
                    // reorder:reorder,
                    unit:unit,
                    // brand:brand,
                    group: group,
                    // has_batch: has_batch,
                    // has_instance: has_instance,
                    // attributes:JSON.stringify(attributes),
                    calltype: "newservice",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New service added", "success");
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
        swal("Oops...", "Please note that service name, sku, tax type (if applicable) must be filled. Check the inputs.", "error");
    }
}




$('.submitattribute').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new attribute?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new attribute!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_attribute()},600)            
        }
    })
});

    
function new_attribute(){
    var proceed=true;
    attr_name=$('.attributename').val()
    if (attr_name == '' || attr_name =='undefined'){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: attr_name,
                    calltype: "newattribute",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New attribute added", "success");
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
        swal("Oops...", "Please note that an unique attribute name must be filled.", "error");
    }
}


$("#product_table").on("click", ".add_price", function(){
    serviceid=$(this).closest('tr').find('td:nth-child(1)').html();
    servicename=$(this).closest('tr').find('td:nth-child(2)').html();
    servicesku=$(this).closest('tr').find('td:nth-child(4)').html();
    existingrate=$(this).closest('tr').find('td:nth-child(7)').html();
    // console.log(existingrate.length);
    // console.log(isNaN(existingrate));
    if (existingrate.length == 0){
        $('#modal_product_rate').modal('show');
        $('.id_rate_prod').val(serviceid)
        $('.name_rate_prod').val(servicename)
        $('.sku_rate_prod').val(servicesku)
        $('.sales_rate_prod').val('')
    }
    else{
        swal("Hmmm...", "Existing sales rate is already present. Kindly update the existing rate", "info");
    }
});

$('.submitrate').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a sales rate?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new rate!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_rate()},600)            
        }
    })
});

    
function new_rate(){
    var proceed=true;
    serviceid=$('.id_rate_prod').val()
    rate=parseFloat($('.sales_rate_prod').val());
    is_tax = $( ".tax_rate_prod" ).is(":checked");
    if (isNaN(rate) || rate<0){
        proceed = false;
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{serviceid: serviceid,
                    rate: rate,
                    is_tax: is_tax,
                    calltype: "newrate",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New sales rate added", "success");
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
        swal("Oops...", "Please note that sales rate must be greater than zero.", "error");
    }
}

$("#product_table").on("click", ".link", function(){
    serviceid = $(this).closest('tr').find('td:nth-child(1)').html();
    $('.update').hide();
    $('.edit').show();
    $.ajax({
        url : "data/",
        type: "GET",
        data: { calltype:"one_service",
            serviceid:serviceid},
        dataType: 'json',
            // handle a successful response
        success : function(jsondata) {
            $('#modal_product_details').modal('show');
            $('.id_data_prod').val(jsondata['id'])
            $('.name_data_prod').val(jsondata['name'])
            $('.sku_data_prod').val(jsondata['sku'])
            // $('.barcode_data_prod').val(jsondata['barcode'])
            $('.hsn_data_prod').val(jsondata['hsn_code'])            
            $('#cgst_data_prod').val(tax_array[jsondata['cgst']])
            $('#sgst_data_prod').val(tax_array[jsondata['sgst']])
            $('#igst_data_prod').val(tax_array[jsondata['igst']])
            $('#group_edit').val(group_array[jsondata['group']])
            // $('#manufac_data_prod').val(tax_array[jsondata['manufacturer']])
            $('.editable').attr('disabled', true);
            // $('#cgst_data_prod').selectpicker('refresh');
            // $('#sgst_data_prod').selectpicker('refresh');
            // $('#igst_data_prod').selectpicker('refresh');
        },
            // handle a non-successful response
        error : function() {
            swal("Oops...", "There was error in processing service data. Please try again later", "error");
        }
    });
});

$('.edit').click(function(e) {
    $('.editable').attr('disabled', false);
    $('.edit').hide();
    $('.update').show();
});

$('.update').click(function(e) {
    
    swal({
        title: "Are you sure?",
        text: "Are you sure to update product data?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, update data!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){update_data()},600)            
        }
    })
});

function update_data(){
    var proceed_update=true;
    pk=$('.id_data_prod').val()
    name_update=$('.name_data_prod').val()
    sku_update=$('.sku_data_prod').val()
    barcode_update=$('.barcode_data_prod').val()
    hsn_update=$('.hsn_data_prod').val()
    cgst_update=$('#cgst_data_prod').val()
    sgst_update=$('#sgst_data_prod').val()
    igst_update=$('#igst_data_prod').val()
    group_update=$('#group_edit').val()
    // group_update=$(".group_update").find(':selected').data('id');
    
    if (name_update == '' || typeof(name_update) =='undefined' || sku_update == '' || typeof(sku_update) =='undefined' ){
        proceed_update = false;
    }
    if (proceed_update){
        (function() {
            $.ajax({
                url : "data/" , 
                type: "POST",
                data:{pk: pk,
                    name: name_update,
                    sku:sku_update,
                    barcode: barcode_update,
                    hsn: hsn_update,
                    cgst:cgst_update,
                    sgst:sgst_update,
                    igst:igst_update,
                    group: group_update,
                    calltype: "updateservice",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "Product data updated.", "success");
                        setTimeout(location.reload(true),1000);
                    }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. Remember, SKU must be unique. There were some errors!", "error");
                }
            });
        }());
    }
    else{
        swal("Oops...", "Please note that name & sku must be filled and SKU must be unique.", "error");
    }
}

});