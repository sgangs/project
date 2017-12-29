
$(function(){

function number2text(value) {
    var fraction = Math.round(frac(value)*100);
    var f_text  = "";

    if(fraction > 0) {
        f_text = "AND "+convert_number(fraction)+" PAISE";
    }

    return convert_number(value)+" RUPEE "+f_text+" ONLY";
}

function frac(f) {
    return f % 1;
}

function convert_number(number)
{
    if ((number < 0) || (number > 999999999)) 
    { 
        return "NUMBER OUT OF RANGE!";
    }
    var Gn = Math.floor(number / 10000000);  /* Crore */ 
    number -= Gn * 10000000; 
    var kn = Math.floor(number / 100000);     /* lakhs */ 
    number -= kn * 100000; 
    var Hn = Math.floor(number / 1000);      /* thousand */ 
    number -= Hn * 1000; 
    var Dn = Math.floor(number / 100);       /* Tens (deca) */ 
    number = number % 100;               /* Ones */ 
    var tn= Math.floor(number / 10); 
    var one=Math.floor(number % 10); 
    var res = ""; 

    if (Gn>0) 
    { 
        res += (convert_number(Gn) + " CRORE"); 
    } 
    if (kn>0) 
    { 
            res += (((res=="") ? "" : " ") + 
            convert_number(kn) + " LAKH"); 
    } 
    if (Hn>0) 
    { 
        res += (((res=="") ? "" : " ") +
            convert_number(Hn) + " THOUSAND"); 
    } 

    if (Dn) 
    { 
        res += (((res=="") ? "" : " ") + 
            convert_number(Dn) + " HUNDRED"); 
    } 


    var ones = Array("", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX","SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE", "THIRTEEN","FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN","NINETEEN"); 
    var tens = Array("", "", "TWENTY", "THIRTY", "FOURTY", "FIFTY", "SIXTY","SEVENTY", "EIGHTY", "NINETY"); 

    if (tn>0 || one>0) 
    { 
        if (!(res=="")) 
        { 
            res += " AND "; 
        } 
        if (tn < 2) 
        { 
            res += ones[tn * 10 + one]; 
        } 
        else 
        { 

            res += tens[tn];
            if (one>0) 
            { 
                res += ("-" + ones[one]); 
            } 
        } 
    }

    if (res=="")
    { 
        res = "zero"; 
    } 
    return res;
}

function title_case(str) {
  return str.replace(/\b\S/g, function(t) { return t.toUpperCase() });
}


discount_types=['Nil','%','Val' ]

load_data()

function load_data(){
    $.ajax({
        url : "/sales/invoice/detail/"+pk+"/", 
        type: "GET",
        dataType: 'json',
        // handle a successful response
        success : function(jsondata) {
            document.title = "Sales Invoice:"+jsondata['invoice_id'];
            igst_total=0;
            taxtotal = parseFloat(jsondata['cgsttotal']) + parseFloat(jsondata['sgsttotal']) + parseFloat(jsondata['igsttotal'])
            
            // Fill Template 1

            $('.invoiceid').append('<font size="3">'+jsondata['invoice_id']+'</font>');
            date=jsondata['date']
            date=date.split("-").reverse().join("-")
            $('.date').append('<font size="3">'+date+'</font');
            
            $('.date_template2').append(date);
            $('.invoiceid_template2').append(jsondata['invoice_id']);
            
            if ((jsondata['dl_1']!=''&& jsondata['dl_1'] !=null) || (jsondata['dl_2']!=''&& jsondata['dl_2']!=null) ){
                $('.customer').append('<font size="2">'+jsondata['customer_name']+
                    ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']
                    +'<br>DL No:'+jsondata['dl_1']+'/'+jsondata['dl_2']+'<font size="2">');

                
                $('.customer_template2').append(jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']
                    +'<br>PAN:'+$.trim(jsondata['customer_pan'])+'<br>DL No:'+jsondata['dl_1']+'/'+jsondata['dl_2']);
            }
            else{
                $('.customer').append('<font size="2">'+jsondata['customer_name']+
                    ',<br>'+jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']+'<font size="2">');


                $('.customer_template2').append(jsondata['customer_address']+',<br>'+jsondata['customer_city']+'<br>GST:'+jsondata['customer_gst']
                    +'<br>PAN:'+$.trim(jsondata['customer_pan']));
            }
            
            if ((jsondata['tenant_dl1']!=''&& jsondata['tenant_dl1'] !=null) || (jsondata['tenant_dl2']!=''&& jsondata['tenant_dl2']!=null) ){
                $('.warehouse').append('<font size="2">'+jsondata['tenant_name']+'<br>'+jsondata['warehouse_address']+
                    ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<br>DL No:'+jsondata['tenant_dl1']+'/'
                    +jsondata['tenant_dl2']+'<font size="2">');

                $(".tenant_name").html(jsondata['tenant_name'].toUpperCase());

                $('.warehouse_template2').append(jsondata['warehouse_address']+
                    ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<br>PAN:'+jsondata['tenant_pan']+
                    '<br>DL No:'+jsondata['tenant_dl1']+'/'+jsondata['tenant_dl2']);

            }
            else{
                $('.warehouse').append('<font size="2">'+jsondata['tenant_name']+'<br>'+jsondata['warehouse_address']+
                    ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<font size="2">');

                $(".tenant_name").html(jsondata['tenant_name'].toUpperCase());
                // 

                $('.warehouse_template2').append(jsondata['warehouse_address']+
                    ',<br>'+jsondata['warehouse_city']+'<br>GST:'+jsondata['tenant_gst']+'<br>PAN:'+jsondata['tenant_pan']);
            }
            
            // tenant_name_upper = jsondata['tenant_name'].toUpperCase();
            tenant_name_lower = jsondata['tenant_name'].toLowerCase();
            tenant_name_title = title_case(tenant_name_lower);

            $(".from_template2").append(tenant_name_title);
            $(".behalf_template2").append(tenant_name_title);
            $(".phone").append(jsondata['tenant_phone']);
            $(".email").append(jsondata['tenant_email']);

            customer_name_lower = jsondata['customer_name'].toLowerCase();
            customer_name_title = title_case(customer_name_lower);

            $(".to_template2").append(customer_name_title);

            var payable_total = parseFloat(jsondata['total']);

            $('.subtotal_receipt').append('<font size="2">'+jsondata['subtotal']+'<font size="2">');

            $('.subtotal_template2').append(jsondata['subtotal']);


            // $('.taxtotal_receipt').append(taxtotal.toFixed(2));
            cgst_fixed=parseFloat(jsondata['cgsttotal']).toFixed(2);
            sgst_fixed=parseFloat(jsondata['sgsttotal']).toFixed(2)
            $('.cgsttotal_receipt').append('<font size="2">'+cgst_fixed+'<font size="2">');
            $('.sgsttotal_receipt').append('<font size="2">'+sgst_fixed+'<font size="2">');
            $('.total_receipt').append('<font size="2">'+(parseFloat(jsondata['total'])-parseFloat(jsondata['roundoff'])).toFixed(2)+'<font size="2">');
            $('.roundoff_receipt').append('<font size="2">'+jsondata['roundoff']+'<font size="2">');
            $('.payable_receipt').append('<font size="2">'+jsondata['total']+'<font size="2">');

            $('.cgsttotal_template2').append(cgst_fixed);
            $('.sgsttotal_template2').append(sgst_fixed);
            $('.total_template2').append((parseFloat(jsondata['total'])-parseFloat(jsondata['roundoff'])).toFixed(2));
            $('.round_template2').append(jsondata['roundoff']);
            $('.payable_template2').append(jsondata['total']);

            // var num_to_str_upper = number2text(payable_total);
            var num_to_str_lower = number2text(payable_total).toLowerCase();
            var num_to_str = title_case(num_to_str_lower);
           $('.total_words_template2').append(num_to_str);

           $.each(jsondata['tenant_tnc'], function(){
                
                $('.sales_tnc_body').append("<p style='margin: 0''>"+this+"</p>");
            })

           // var len_items = jsondata['line_items'].length;
           // var len_policy = jsondata['tenant_tnc'].length;
           // var total_len = len_items + len_policy;
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
                    "<td colspan='2'><font size='1'>"+this.product_name+"</font></td>"+
                    "<td><font size='1'>"+$.trim(this.product_hsn)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.quantity)+"</font></td>"+
                    // "<td id='not_print'>"+this.free_without_tax+"</td>"+
                    // "<td id='not_print'>"+this.free_with_tax+"</td>"+
                    "<td id='not_pos_print' class='hidden-print'><font size='1'>"+this.unit+"</font></td>"+
                    // "<td class='visible-print-block'>"+free_total+"</td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.sales_price+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.mrp+"</font></td>"+
                    "<td id='not_pos_print' class='hidden-print'><font size='1'>"+discount_types[this.discount_type]+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.discount_value+"</font></td>"+
                    "<td id='not_pos_print' class='hidden-print'><font size='1'>"+discount_types[this.discount2_type]+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.discount2_value+"</font></td>"+
                    "<td id='not_pos_print'><font size='1'>"+this.line_tax+"</font></td>"+
                    // "<td id='not_pos_print'>"+this.tax_percent+"</td>"+
                    "<td><font size='1'>"+parseFloat(this.cgst_percent)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.cgst_value)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.sgst_percent)+"</font></td>"+
                    "<td><font size='1'>"+parseFloat(this.sgst_value)+"</font></td>"+
                    "<td class='is_igst'><font size='1'>"+parseFloat(this.igst_percent)+"</font></td>"+
                    "<td class='is_igst'><font size='1'>"+parseFloat(this.igst_value)+"</font></td>"+
                    "<td><font size='1'>"+this.line_total+"</font></td>"+
                    "</tr>");
            });

            // if (total_len < 12){
            //     for (i = 0; i < (12 - total_len); i++) {
            //         $('.table_bnw').append("<tr class='data text-center blank_rows'>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td></td>"+
            //         "<td class='is_igst'></td>"+
            //         "<td class='is_igst'></td>"+
            //         "</tr>");
            //     }
            // }
        },
        // handle a non-successful response
        error : function() {
            swal("Oops...", "There were some issues in fetching the data.", "error");
        }
    });
}

$('.printout').click(function(){
     // window.print();
     if (igst_total == 0 || isNaN(igst_total)){
        $('.is_igst').addClass('hidden-print');

    }

    // $(".base_template").attr('hidden', false);

    // $(".template2").attr('hidden', true);



     $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: landscape; margin: 0mm;}");
        text("@media print {#print{display: block;}#not_print{display: none;}"+
            ".details { border: solid #000 !important; border-width: 0.5px 0 0 0.5px !important; }"+
            ".details th, .details td { border: solid #000 !important; border-width: 0 0.5px 0.5px 0 !important; }} "+
            "@page{size: auto; margin: 0mm;}");

    window.print();

    // $(".base_template").attr('hidden', true);

    // $(".template2").attr('hidden', false);
});


$('.printTemplate2').click(function(){
     // window.print();
    if (igst_total == 0 || isNaN(igst_total)){
        $('.is_igst').addClass('hidden-print');
        // $(".product_name_header").css('width' ,'25%')

    }

    $(".base_template").attr('hidden', true);

    $(".template2bnw").attr('hidden', true);

    $(".template2").attr('hidden', false);

    $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: landscape; margin: 0mm;}");
        text("@page {size: A4; @bottom-right { content: counter(page); } }"+
        
        ".template2{ box-shadow: 0 0 0.5cm rgba(0, 0, 0, 0.5); box-sizing: border-box; }"+

        "@media print { .page-break { display: block; page-break-before: always; } size: A4 portrait; }"+

        // "@media print { .add_shadow { -webkit-filter: drop-shadow(4px 4px 1px #ccc); text-shadow: 4px 4px 1px #ccc; } }"+

        "@media print {"+
        ".details { border: solid #a0e8da !important; border-width: 0.5px 0 0 0.5px !important; }"+
        ".details th, .details td { border: solid #a0e8da !important; border-width: 0 0.5px 0.5px 0 !important; }} "+

        "@media print{ body { margin: 0; padding: 0; }"+

        ".template2 { box-shadow: none; margin: 0; width: auto; height: auto; } .enable-print { display: block; } }"+

        "@media print{ div{ page-break-inside: avoid; } }");

    window.print();

    $(".base_template").attr('hidden', false);

    $(".template2").attr('hidden', true);

    $(".template2bnw").attr('hidden', true);

});

$('.printTemplate2BnW').click(function(){
     // window.print();
    if (igst_total == 0 || isNaN(igst_total)){
        $('.is_igst').addClass('hidden-print');
        // $(".product_name_header").css('width' ,'25%')

    }

    $(".base_template").attr('hidden', true);

    $(".template2").attr('hidden', true);

    $(".template2bnw").attr('hidden', false);

    $(".print_style").
        // text("@media print {#print{display: block;}#not_print{display: none;}} @page{size: landscape; margin: 0mm;}");
        text("@page {size: A4; @bottom-right { content: counter(page); } }"+
        
        ".template2{ box-shadow: 0 0 0.5cm rgba(0, 0, 0, 0.5); box-sizing: border-box; }"+

        "@media print { .page-break { display: block; page-break-before: always; } size: A4 portrait; }"+

        // "@media print { .add_shadow { -webkit-filter: drop-shadow(4px 4px 1px #ccc); text-shadow: 4px 4px 1px #ccc; } }"+

        "@media print {"+
        ".details { border: solid #000000 !important; border-width: 0.5px 0 0 0.5px !important; }"+
        ".details th, .details td { border: solid #000000 !important; border-width: 0 0.5px 0.5px 0 !important; }} "+

        "@media print {"+
        ".blank_rows { border: solid #ffffff !important; border-width: 0.5px 0 0 0.5px !important; }"+
        ".blank_rows th, .blank_rows td { border: solid #ffffff !important; border-width: 0 0.5px 0.5px 0 !important; }} "+

        "@media print{ body { margin: 0; padding: 0; }"+

        ".template2 { box-shadow: none; margin: 0; width: auto; height: auto; } .enable-print { display: block; } }"+

        "@media print{ div{ page-break-inside: avoid; } }");

    window.print();

    $(".base_template").attr('hidden', false);

    $(".template2").attr('hidden', true);

    $(".template2bnw").attr('hidden', true);

});


});