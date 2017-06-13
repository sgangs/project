$(function(){
var has_attribute=false, attr_name, product_name, sku, vat_type, tax, reorder, unit, brand, group, has_batch, 
    has_instance;

load_products()

function load_products(){
    $.ajax({
        url : "productdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            console.log(jsondata);
            $.each(jsondata, function(){
                $('#product_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+this.name+"</td>"+
                "<td>"+this.sku+"</td>"+
                "<td>"+$.trim(this.default_unit)+"</td>"+
                "<td>"+$.trim(this.brand)+"</td>"+
                "<td>"+$.trim(this.group)+"</td>"+
                "<td>"+$.trim(this.remarks)+"</td>"+
                "</tr>");
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
        url : "/master/dimensionunit/unitdata/", 
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
                    $('#tax').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.name
                        }));
                    $('#tax').selectpicker('refresh')
                })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "No tax data exist.", "error");
        }
    });
}

load_attribute()

function load_attribute(){
    $.ajax({
        url : "attributedata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            attr_values=jsondata;
            $.each(attr_values, function(){
                    $('#selattr0').append($('<option/>',{
                        'data-id': this.id,
                        'text': this.name
                        }));                    
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Hmm...", "No attribute data exist.", "error");
        }
    });
}



$( ".has_attribute" ).change(function() {
    has_attribute = $( ".has_attribute" ).is(":checked");
    if (has_attribute){
        $('#attribute_details').prop('hidden',false);
    }
    else{
        $('#attribute_details').prop('hidden',true);        
    }
});



var next = 0;
    $("#add-more").click(function(e){
        e.preventDefault();
        var addto = "#attr" + next;
        var addRemove = "#attr" + next;
        next = next + 1;
        var newIn = ' <div id="attr'+ next +'" class="attr"><br>'+
            '<div class="form-group"><label class="control-label">Select Attribute</label>'+
            '<select class="form-control select attribute" id="selattr'+next+'"">'+
            '<option disabled selected hidden style="display: none" value>Select Attribute</option></select></div>'+
            '<div class="form-group"><label class="control-label">Attribute Value</label>'+
            '<input type="text" class="form-control value" placeholder="If arribute is colour, value can be: Blue, White, etc.">'+
            '</div></div>';
        var newInput = $(newIn);
        var removeBtn = '<button id="remove'+(next - 1)+'"class="btn btn-danger btn-xs remove-me">Remove Attribute</button>';
        var removeButton = $(removeBtn);
        $(addto).after(newInput);
        $(addRemove).after(removeButton);
        $("#attr" + next).attr('data-source',$(addto).attr('data-source'));
        $("#count").val(next);
        $.each(attr_values, function(){
            $('#selattr'+next).append($('<option/>',{
            'data-id': this.id,
            'text': this.name
            }));                    
        })
        
        $('.remove-me').click(function(e){
            e.preventDefault();
            var attrNum = this.id.charAt(this.id.length-1);
            var attrID = "#attr" + attrNum;
            $(this).remove();
            $(attrID).remove();
        });
    });


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to add a new product?",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add new product!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){new_product()},600)            
        }
    })
});

function new_product(){
    var proceed=true, attributes=[];
    product_name=$('.name').val()
    sku=$('.sku').val()
    vat_type=$(".vattype").find(':selected').data('id');
    tax=$(".tax").find(':selected').data('id');
    reorder=$('.reorder').val()
    unit=$(".unit").find(':selected').data('id');
    brand=$(".brand").find(':selected').data('id');
    group=$(".group").find(':selected').data('id');
    has_batch = $( ".has_batch" ).is(":checked");
    has_instance = $( ".has_instance" ).is(":checked");
    has_attribute = $( ".has_attribute" ).is(":checked");
    if (has_attribute){
        $("#attribute_details").children('div').each(function() {
            var attribute_id = $(this).find('.attribute :selected').data('id');
            var value = $(this).children().last().find('.value').val();
            if (isNaN(attribute_id)){
                $(this).addclass('has-error')
            }
            var item = {
                attribute_id : attribute_id,
                value: value,            
            };
            attributes.push(item);            
        });
        console.log(attributes)
    }
    if (has_attribute){
        if (attributes.length < 1){
            proceed=false;
            swal("Oops...", "Please add atleast one attribute if has_attribute is selected.", "error");
        }
    }

    if (product_name == '' || product_name =='undefined' || sku == '' || sku =='undefined' || vat_type >3 || vat_type<1){
        proceed = false;
        swal("Oops...", "Product must have a name and sku/product code.", "error");
    }
    if (vat_type == 2 || vat_type ==3){
        if (tax == '' || tax =='undefined' || isNaN(tax)){
            proceed=false;
            swal("Oops...", "Please select a tax structure", "error");
        }
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "" , 
                type: "POST",
                data:{name: product_name,
                    sku: sku,
                    vat_type: vat_type,
                    tax:tax,
                    reorder:reorder,
                    unit:unit,
                    brand:brand,
                    group: group,
                    has_batch: has_batch,
                    has_instance: has_instance,
                    has_attribute: has_attribute,
                    attributes:JSON.stringify(attributes),
                    calltype: "newproduct",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                // contentType: "application/json",
                        // handle a successful response
                success : function(jsondata) {
                    var show_success=true
                    if (show_success){
                        swal("Hooray", "New product added", "success");
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
        swal("Oops...", "Please note that product name, sku, tax type (if applicable) must be filled. Check the inputs.", "error");
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

});