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
from .models import Customer, Unit, Product
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
            customer_key[row[1]]=i
            try:
                Customer.objects.for_tenant(this_tenant).get(key=row[1])
                row_no.append(i+1)
            except:
                row[4]=state_dict[row[4]]
                objects_customer.append(Customer(name=row[0], key=row[1],address_1=row[2], address_2=row[3], state=row[4],\
                    city=row[5],pin=row[6],phone_no=row[7], cst=row[8], tin=row[9], gst=row[10], details=row[11], tenant=this_tenant))

    with transaction.atomic():
        try:
            Customer.objects.bulk_create(objects_customer)
        except:
            transaction.rollback()
        # print(row)
    return row_no


def product_register(excel_data, this_tenant):
    row_no=[]
    product_id={}
    objects_product = []
    tmp = xlrd.open_workbook(file_contents=excel_data.read())
    sheet = tmp.sheet_by_index(0)
    num_rows = sheet.nrows
    unit=Unit.objects.for_tenant(this_tenant).get(name='Number')
    for i in range(2, num_rows):
        row = sheet.row_values(i)
        if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "") :
            row_no.append(i+1)
        elif (row[1] in product_id):
            row_no.append(i+1)
        else:
            product_id[row[1]]=i
            try:
                Product.objects.for_tenant(this_tenant).get(sku=row[1])
                row_no.append(i+1)
            except:
                if row[2]:
                    try:
                        Product.objects.for_tenant(this_tenant).get(barcode=row[2])
                        row_no.append(i+1)
                    except:
                        objects_product.append(Product(name=row[0], sku=row[1],barcode=row[2], default_unit=unit, tenant=this_tenant))
                else:
                    objects_product.append(Product(name=row[0], sku=row[1], default_unit=unit, tenant=this_tenant))
            
    with transaction.atomic():
        try:
            Product.objects.bulk_create(objects_product)
        except:
            transaction.rollback()
        # print(row)
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
    worksheet_s.write(1, 1, ugettext("Short Name/Code (Must be filled and must be unique) Max_length:40"), header)
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
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    
    worksheet_s.write(1, 0, ugettext("Product Name (Must be filled)"), header)
    worksheet_s.write(1, 1, ugettext("Product SKU (Must be filled and must be unique) Max_length:20"), header)
    worksheet_s.write(1, 2, ugettext("Product Barcode (Must be unique) Max_length:10"), header)
    
    # column widths definition
    base_col_width = 25
    # description_col_width = 10
    wide_col_width = 45

    # column widths
    worksheet_s.set_column('A:A', base_col_width)
    worksheet_s.set_column('B:B', wide_col_width)
    worksheet_s.set_column('C:C', wide_col_width    )
    
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data