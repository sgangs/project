import datetime as dt
from datetime import datetime
from io import BytesIO
import xlrd
import xlsxwriter

from django.db import transaction
#from django.db.models import Avg, Sum, Max, Min
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext
# from school.id_definition import make_id
# from school_genadmin.models import Batch
from .models import Customer, Unit, Product, tax_structure, Zone, product_sales_rate, Manufacturer, Group
from distributor.variable_list import state_list


def customer_validate(row, this_tenant):
    state_dict= dict((y,x) for x,y in state_list)
    # key=str(make_id())
    # item=None
    # row[12]=batch
    state_selected=row[4]
    row[4]=state_dict[state_selected]
    row.append(this_tenant)
    if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "") :
        transaction.rollback()
        return HttpResponse("There is error in uploaded excel")
    return row


def customer_register(excel_data, this_tenant):
    row_no=[]
    customer_key={}
    objects_customer = []
    state_dict= dict((y,x) for x,y in state_list)
    tmp = xlrd.open_workbook(file_contents=excel_data.read())
    sheet = tmp.sheet_by_index(0)
    num_rows = sheet.nrows
    for i in range(2, num_rows):
        row = sheet.row_values(i)
        
        if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "") :
            row_no.append(i+1)
        elif (row[1] in customer_key):
            row_no.append(i+1)
        else:
            zone=None
            customer_key[row[1]]=i
            if (row[12] != None or row[12] != ""):
                try:
                    zone=Zone.objects.for_tenant(this_tenant).get(key=row[12])
                except:
                    pass
            try:
                Customer.objects.for_tenant(this_tenant).get(key=row[1])
                row_no.append(i+1)
            except:
                row[4]=state_dict[row[4]]
                objects_customer.append(Customer(name=row[0], key=row[1],address_1=row[2], address_2=row[3], state=row[4],\
                    city=row[5],pin=row[6],phone_no=row[7], cst=row[8], tin=row[9], gst=row[10], details=row[11],zone=zone, tenant=this_tenant))

    with transaction.atomic():
        try:
            Customer.objects.bulk_create(objects_customer)
        except:
            transaction.rollback()
        # print(row)
    return row_no




def product_register(excel_data, this_tenant):
    taxes=tax_structure.objects.for_tenant(this_tenant).all()
    row_no=[]
    product_id={}
    objects_product = []
    tmp = xlrd.open_workbook(file_contents=excel_data.read())
    sheet = tmp.sheet_by_index(0)
    num_rows = sheet.nrows
    if (num_rows > 500):
        row_no.append("Maximum of 500 products can be uploaded at a time.")
    else:
        unit=Unit.objects.for_tenant(this_tenant).get(name='Number')
        manufacturers=Manufacturer.objects.for_tenant(this_tenant).all()
        groups=Group.objects.for_tenant(this_tenant).all()
        for i in range(1, num_rows):
            manufac = None
            group_selected = None

            has_rate=False
            row = sheet.row_values(i)
            if (row[0] == None or row[0] == "" or row[2] == None or row[2] == "") :
                row_no.append(i+1)
            elif (row[2] in product_id):
                row_no.append(i+1)
            else:
                product_id[row[2]]=i
                try:
                    old_product=Product.objects.for_tenant(this_tenant).get(sku=row[2])
                    row_no.append(i+1)
                except:
                    cgst = None
                    sgst = None
                    igst = None
                    hsn = None
                    if row[3]:
                        try:
                            Product.objects.for_tenant(this_tenant).get(barcode=str(row[3]).rstrip('0').rstrip('.'))
                            row_no.append(i+1)
                        except:
                            if row[1]:
                                try:
                                    hsn=str(int(row[1]))
                                except:
                                    pass
                            
                            if row[4]:
                                try:
                                    cgst=taxes.get(name=row[4])
                                except:
                                    pass
                            
                            if row[5]:
                                try:
                                    sgst=taxes.get(name=row[5])
                                except:
                                    pass
                            
                            if row[6]:
                                try:
                                    igst=taxes.get(name=row[6])
                                except:
                                    pass
                            
                            if row[7]:
                                retail_sales_rate=row[7]
                                has_rate = True
                            
                            if row[8]:
                                is_tax=row[8]
                                if is_tax == 'Y' or is_tax == 'y':
                                    is_tax = True
                                else:
                                    is_tax = False
                            else:
                                is_tax = False

                            if row[9]:
                                manufacturer_name = row[9]
                                try:
                                    manufac = manufacturers.get(name = manufacturer_name)
                                except:
                                    manufac = None

                            if row[10]:
                                group_name = row[10]
                                try:
                                    group_selected = groups.get(name = group_name)
                                except:
                                    group_selected = None
                                                            
                            new_product=Product.objects.create(name=row[0],hsn_code=hsn, sku=row[2],barcode=str(str(row[3]).rstrip('0').rstrip('.')),\
                                default_unit=unit,cgst=cgst, sgst=sgst, igst=igst, manufacturer = manufac, group=group_selected, tenant=this_tenant)

                            if has_rate:
                                new_rate=product_sales_rate.objects.create(product=new_product, tentative_sales_rate=retail_sales_rate,\
                                    is_tax_included=is_tax, tenant=this_tenant)
                    else:
                        if row[1]:
                                try:
                                    hsn=str(int(row[1]))
                                except:
                                    pass
                        if row[4]:
                            try:
                                cgst=taxes.get(name=row[4])
                            except:
                                pass
                        
                        if row[5]:
                            try:
                                sgst=taxes.get(name=row[5])
                            except:
                                pass
                        
                        if row[6]:
                            try:
                                igst=taxes.get(name=row[6])
                            except:
                                pass
                        
                        if row[7]:
                            retail_sales_rate=row[7]
                            has_rate = True
                        
                        if row[8]:
                            is_tax=row[8]
                            if is_tax == 'Y' or is_tax == 'y':
                                is_tax = True
                            else:
                                is_tax = False
                        else:
                            is_tax = False

                        if row[9]:
                            manufacturer_name = row[9]
                            try:
                                manufac = manufacturers.get(name = manufacturer_name)
                            except:
                                manufac = None

                        if row[10]:
                            group_name = row[10]
                            try:
                                group_selected = groups.get(name = group_name)
                            except:
                                group_selected = None

                        new_product=Product.objects.create(name=row[0],hsn_code=hsn, sku=row[2],barcode=str(row[3]).rstrip('0').rstrip('.'),\
                            default_unit=unit,cgst=cgst, sgst=sgst, igst=igst, manufacturer = manufac, group=group_selected, tenant=this_tenant)
                        
                        if has_rate:
                            new_rate=product_sales_rate.objects.create(product=new_product, tentative_sales_rate=retail_sales_rate,\
                                is_tax_included=is_tax, tenant=this_tenant)

    return row_no


def customer_format():
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    worksheet_s = workbook.add_worksheet("Summary")

    # excel styles
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    
    worksheet_s.write(1, 0, ugettext("Customer Name (Must be filled) Max_length:200"), header)
    worksheet_s.write(1, 1, ugettext("Short Name/Code (Must be filled and must be unique) Max_length:30"), header)
    worksheet_s.write(1, 2, ugettext("Address Line 1"), header)
    worksheet_s.write(1, 3, ugettext("Address Line 2"), header)
    worksheet_s.write(1, 4, ugettext("State (Please Contact Us For State List)"), header)
    worksheet_s.write(1, 5, ugettext("City/Town"), header)
    worksheet_s.write(1, 6, ugettext("Pincode"), header)
    worksheet_s.write(1, 7, ugettext("Phone No (Format:+91-XXXXXXXXXX"), header)
    worksheet_s.write(1, 8, ugettext("CST No"), header)
    worksheet_s.write(1, 9, ugettext("TIN"), header)
    worksheet_s.write(1, 10, ugettext("GST No"), header)
    worksheet_s.write(1, 11, ugettext("Remarks"), header)
    
    # column widths definition
    base_col_width = 15
    # description_col_width = 10
    # observations_col_width = 25

    # column widths
    worksheet_s.set_column('A:A', base_col_width)
    worksheet_s.set_column('B:B', base_col_width)
    worksheet_s.set_column('C:C', base_col_width)
    worksheet_s.set_column('D:D', base_col_width)
    worksheet_s.set_column('E:E', 30)
    worksheet_s.set_column('F:F', base_col_width)
    worksheet_s.set_column('G:G', base_col_width)
    worksheet_s.set_column('H:H', base_col_width)
    worksheet_s.set_column('I:I', base_col_width)
    worksheet_s.set_column('J:J', base_col_width)
    worksheet_s.set_column('K:K', base_col_width)
    worksheet_s.set_column('L:L', base_col_width)

    
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data



def product_format():
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    worksheet_s = workbook.add_worksheet("Summary")

    # excel styles
    note_header = workbook.add_format({
        'bg_color': '#FFFFFF',
        'color': '##00208E',
        'valign': 'top',
        'border': 1
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })

    bold_header = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })    
    
    worksheet_s.write(0, 0, ugettext\
        ("Note: Items in bold must be filled. Product SKU and Product Barcodes must be unique.Is Tax Included must be filled with either 'Y' or 'N'")\
        , note_header)


    worksheet_s.write(1, 0, ugettext("Product Name"), bold_header)
    worksheet_s.write(1, 1, ugettext("Product HSN Code"), header)
    worksheet_s.write(1, 2, ugettext("Product SKU (Max_length:15)"), bold_header)
    worksheet_s.write(1, 3, ugettext("Product Barcode (Max_length:15)"), header)
    worksheet_s.write(1, 4, ugettext("CGST Structure Name"), header)
    worksheet_s.write(1, 5, ugettext("SGST Structure Name"), header)
    worksheet_s.write(1, 6, ugettext("IGST Structure Name"), header)
    worksheet_s.write(1, 7, ugettext("Retail Rate"), header)
    worksheet_s.write(1, 8, ugettext("Is Tax Included (Y/N)"), header)
    worksheet_s.write(1, 9, ugettext("Manufacturer"), header)
    worksheet_s.write(1, 10, ugettext("Prouct Category"), header)
    
    # column widths definition
    base_col_width = 25
    wide_col_width = 45
    narrow_col_width = 20

    # column widths
    worksheet_s.set_column('A:A', base_col_width)
    worksheet_s.set_column('B:B', base_col_width)
    worksheet_s.set_column('C:C', wide_col_width)
    worksheet_s.set_column('D:D', wide_col_width)
    worksheet_s.set_column('E:E', narrow_col_width)
    worksheet_s.set_column('F:F', narrow_col_width)
    worksheet_s.set_column('G:G', narrow_col_width)
    worksheet_s.set_column('H:H', narrow_col_width)
    worksheet_s.set_column('I:I', base_col_width)
    worksheet_s.set_column('J:J', narrow_col_width)
    worksheet_s.set_column('K:K', narrow_col_width)
    
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data