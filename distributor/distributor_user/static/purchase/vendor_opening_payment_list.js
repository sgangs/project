$(function(){

var total_payment=0, page_no=0, filter_applied = false;

var end = moment();
var start = moment(end).subtract(60, 'days');
var startdate=start.format('DD-MM-YYYY'), enddate=end.format('DD-MM-YYYY');
var dateChanged=false;
// date_update();


// function apply_navbutton(jsondata, page_no){
//     $('.navbtn').remove()
//     for (i =jsondata['start']+1; i<=jsondata['end']; i++){
//         if (i==page_no){
//                     // $('.add_nav').append("<a href='#' class='btn nav_btn btn-sm btn-default' data=1 style='margin-right:0.2%'>"+i+"</a>")
//             $('.add_nav').append("<button title='Your Current Page' class='btn btn-sm navbtn btn-info' "+
//                 "value="+i+" style='margin-right:0.2%'>"+i+"</button>")
//         }
//         else{
//             $('.add_nav').append("<button title='Go to page no: "+i+"' class='btn btn-sm navbtn btn-default'"+
//                 " value="+i+" style='margin-right:0.2%'>"+i+"</button>")
//         }
//     }
// }

// $('.apply_reset').click(function(){
//     filter_applied=false;
//     $('select').val([]).selectpicker('refresh');
//     $('.vendor').val('');
//     $('.receipt_no').val('');
//     $('.cheque_rtgs').val('');
//     date_update();
//     dateChanged=false;
//     load_receipts(1);
//     $('#filter').modal('hide');
// });


function load_payments(){
    
    // if (!dateChanged){
    //     startdate = startdate.split("-").reverse().join("-")
    //     enddate = enddate.split("-").reverse().join("-")
    //     dateChanged= true;
    // }

    vendorid=$('.vendor').find(':selected').data('id')

    $.ajax({
        url : "/purchase/vendor/opening-balance/",
        type: "GET",
        data:{ calltype:"vendor_opening_list",
            vendorid: vendorid,
            // start: startdate,
            // end: enddate
            },
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $("#payment_table .data").remove();

            $.each(jsondata['payment_list'], function(){
                // console.log(this.purchase_receipt.id);
                var date=this.paid_on
                date=date.split("-").reverse().join("-")

                $('#payment_table').append("<tr class='data' align='center'>"+
                "<td hidden='true'>"+this.id+"</td>"+
                "<td>"+date+"</td>"+
                "<td>"+this.payment_mode_name+"</td>"+
                "<td>"+this.amount_paid+"</td>"+
                "<td>"+$.trim(this.cheque_rtgs_number)+"</td>"+
                "<td><input type='checkbox'></td>"+
                "</tr>");
            })
            // apply_navbutton(jsondata, page_no)
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not fetch payment data. Kindly rety after some time.", "error");
        }
    });
}


load_vendors()

function load_vendors(){
    $.ajax({
        url : "/master/vendor/getdata/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            $.each(jsondata, function(){
                $('#vendor').append($('<option>',{
                    'data-id': this.id,
                    'text': this.name + ": "+ this.key
                }));
            });
            $('#vendor').selectpicker('refresh');
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "Could not load vendor data. Kindly try aain later.", "error");
        }
    });
}


$('.vendor').on('change', function() {
    $('#vendor').toggle();
    load_payments();
})


$('.deletebtn').click(function(e) {
    swal({
        title: "Are You Sure To Delete?",
        text: "Are you sure you want to delete the payment?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete payment record!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: true
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){delete_payment()},600)            
        }
    })
});


function delete_payment(){
    var items=[];
    
    $("#payment_table tr.data").each(function() {
        var is_selected = $(this).find('td:nth-child(6) input').is(":checked");
        if (is_selected){
            var payment_id = $(this).find('td:nth-child(1)').html();
            var item = {
                payment_id : payment_id,
            };
            items.push(item);
        }
    });
    
    // if (proceed){
        (function() {
            $.ajax({
                url : "/purchase/vendor/opening-balance/",
                type: "POST",
                data:{delete_list: JSON.stringify(items),
                    calltype: "delete_payment",
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',               
                success : function(jsondata) {
                    // if (typeof(jsondata["id"]) == "undefined"){
                    //     swal("Oops...", "Recheck your inputs. "+jsondata, "error");        
                    // }
                    // else{
                        swal("Hooray", "Selected payments deleted.", "success");
                        load_payments();
                        // var url='/sales/invoice/detailview/'+jsondata['invoice_id']+'/'
                        // location.href = url;
                    // }
                    //console.log(jsondata);
                },
                // handle a non-successful response
                error : function() {
                    swal("Oops...", "Recheck your inputs. There were some errors!", "error");
                }
            });
        }());
    // }
}


});

