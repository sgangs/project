$(function(){

load_data()

function load_data(){
    $.ajax({
        url : "data/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $('.name').append(jsondata['name']);
            $('.address1').val(jsondata['address_1']);
            $('.address2').val(jsondata['address_2']);
            $('.pin').val(jsondata['pin']);
            
            $('.gst').val(jsondata['gst']);
            $('.pan').val(jsondata['pan']);
            $('.dl1').val(jsondata['dl_1']);
            $('.dl2').val(jsondata['dl_2']);
            
            $.each(jsondata['distributor_sales_policy'], function(){
                count=$('.policy_table tr').length;
                // console.log(this);
                $('.policy_table').append("<tr class='data' align='center'>"+
                '<td class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
                '<td><textarea type="text" class="form-control policy" maxlength="150". '+
                'placeholder="State the excat policy to be printed in distributor sales invoices. Maximum = 150 characters" style="resize: none;">'+
                '</textarea></td></tr>');

                $('.policy_table').find('tr:eq('+count+')').find('.policy').val(this);
            })
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some erros. Please try again after some time.", "error");
        }
    });
}

$('.policy_table').on("mouseenter", ".first", function() {
    console.log("here");
    $( this ).children( ".delete" ).show();
});

$('.policy_table').on("mouseleave", ".first", function() {
    $( this ).children( ".delete" ).hide();
});

$('.policy_table').on("click", ".delete", function() {
    $(this).parent().parent().remove();
});


/*$("#tax").on("click", ".name", function(){
    pk=$(this).closest('tr').find('td:nth-child(1)').html()
    console.log(pk);
    el=this;
    var url="individual/"+pk+"/";
    (function() {
        $.ajax({
            url : url, 
            type: "GET",
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                console.log(jsondata);
            },
            // handle a non-successful response
            error : function() {
                // console.log("here")
                swal("Oops...", "There were some error.", "error");
            }
        });
    }());
});
*/

$('.addmore').click(function(){
    count=$('.details tr').length;
    var data='<tr class="data">'+
    '<td class="first"><button style="display: none;" class="delete btn btn-danger btn-xs">-</button></td>'+
    '<td><textarea type="text" class="form-control policy" maxlength="150". '+
    'placeholder="State the excat policy to be printed in distributor sales invoices. Maximum = 150 characters" style="resize: none;">'+
    '</textarea></td></tr>'
    $('.policy_table').append(data);
})

$('.confirm').click(function(e) {
    $('#policy').modal('hide');
});

$('.update_btn').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Are you sure to update your business details?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#67A3C9",
        confirmButtonText: "Yes, update details!",
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
    var proceed = true;
    var gst = $('.gst').val();
    var pan = $('.pan').val();
    var dl1 = $('.dl1').val();
    var dl2 = $('.dl2').val();
    var distributor_sales_policy = [];

    var policy_count = 0;

    $(".policy_table tr.data").each(function() {
        policy_count+=1;
        var policy = $(this).find('td:nth-child(2) textarea').val();
        policy_len = $.trim(policy).length;
        if (policy_len > 0){
            if (policy_len > 150){
                swal("Hmm...", "Policy can have maximum 150 characters", "error");
                $('#policy').modal('show');
                $(this).closest('tr').addClass("has-error");
                var proceed = false;
            }
            else{
                $(this).closest('tr').removeClass("has-error");
                distributor_sales_policy.push(policy);
            }
        }
    });

    if (policy_count > 5){
        swal("Hmm...", "There can be a maximum of 5 sales policy. Currently there are "+policy_count+" policies", "error");
        $('#policy').modal('show');
        var proceed = false;
    }

    (function() {
        $.ajax({
            url : "data/" , 
            type: "POST",
            data:{gst: gst,
                pan:pan,
                dl1: dl1,
                dl2: dl2,
                distributor_sales_policy : JSON.stringify(distributor_sales_policy),
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            
            success : function(jsondata) {
                var show_success=true
                if (show_success){
                    swal("Hooray", "Company Settings updated.", "success");
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

});