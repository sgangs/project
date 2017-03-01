import datetime as dt
from datetime import datetime
from io import BytesIO
import xlsxwriter

from django.db import transaction
#from django.db.models import Avg, Sum, Max, Min
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext
from .models import Student


#This function is used to provide students' data for attendance/exam score entry
def student_validate(row, this_tenant, counter):
    data="st"
    tenant=this_tenant
    today=dt.date.today()
    today_string=today.strftime('%y%m%d')
    next_student_number='{0:03d}'.format(counter)
    last_student=Student.objects.filter(tenant=this_tenant).\
            filter(key__contains=today_string).order_by('key').last()
    if last_student:
        last_student_number=int(last_student.key[8:])
        next_student_number='{0:03d}'.format(last_student_number + counter)
    key=data+str(today_string)+str(next_student_number)
    toslug=str(tenant)+" " +str(key)
    slug=slugify(toslug)
    item=None
    row.append(key)
    row.append(slug)
    row.append(this_tenant)
    row.append(item)
    row.append(item)
    print (type(row [2]))

    if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "") :
        transaction.rollback()
        return HttpResponse("There is error in uploaded excel")
    if (row[3] != "M" and row[3] != "F" and row[3] != "O"):
        transaction.rollback()
        return HttpResponse("There is error in uploaded excel")
    if (row [2] != None and row [2] != ""):
        if (type(row [2]) != dt.date):
            transaction.rollback()
            return HttpResponse("There is error in uploaded excel")
    return row

def WriteToExcel(student):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    worksheet_s = workbook.add_worksheet("Summary")

    # excel styles
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1
    })

    # # write title
    # if town:
    #     town_text = town.name
    # else:
    #     town_text = ugettext("all recorded towns")
    title_text = u"{0}".format(ugettext("Student Details"))
    # merge cells
    worksheet_s.merge_range('A2:O2', title_text, title)

    # write header
    worksheet_s.write(4, 0, ugettext("No"), header)
    worksheet_s.write(4, 1, ugettext("System Key"), header)
    worksheet_s.write(4, 2, ugettext("School Internal Key"), header)
    worksheet_s.write(4, 3, ugettext("First Name"), header)
    worksheet_s.write(4, 4, ugettext("Last Name"), header)
    worksheet_s.write(4, 5, ugettext("Date Of Birth"), header)
    worksheet_s.write(4, 6, ugettext("Gender"), header)
    worksheet_s.write(4, 7, ugettext("Blood Group"), header)
    worksheet_s.write(4, 8, ugettext("Contact"), header)
    worksheet_s.write(4, 9, ugettext("Email ID"), header)
    worksheet_s.write(4, 10, ugettext("Address Line 1"), header)
    worksheet_s.write(4, 11, ugettext("Address Line 2"), header)
    worksheet_s.write(4, 12, ugettext("State"), header)
    worksheet_s.write(4, 13, ugettext("Pincode"), header)
    worksheet_s.write(4, 14, ugettext("Batch"), header)

    # column widths definition
    base_col_width = 20
    # description_col_width = 10
    # observations_col_width = 25

    #add data to table
    for idx, data in enumerate(student):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write(row, 1, data.key, cell_center)
        worksheet_s.write(row, 2, data.local_id, cell_center)
        worksheet_s.write(row, 3, data.first_name, cell_center)
        worksheet_s.write(row, 4, data.last_name, cell_center)
        worksheet_s.write(row, 5, data.dob.strftime('%d/%m/%Y'), cell_center)
        worksheet_s.write(row, 6, data.gender, cell_center)
        worksheet_s.write(row, 7, data.blood_group, cell_center)
        worksheet_s.write(row, 8, data.contact, cell_center)
        worksheet_s.write(row, 9, data.email_id, cell_center)
        worksheet_s.write(row, 10, data.address_line_1, cell_center)
        worksheet_s.write(row, 11, data.address_line_2, cell_center)
        worksheet_s.write(row, 12, data.state, cell_center)
        worksheet_s.write(row, 13, data.pincode, cell_center)
        worksheet_s.write(row, 14, data.batch.name, cell_center)

    # column widths
    worksheet_s.set_column('B:B', base_col_width)
    worksheet_s.set_column('C:C', base_col_width)
    worksheet_s.set_column('D:D', base_col_width)
    worksheet_s.set_column('E:E', base_col_width)
    worksheet_s.set_column('F:F', base_col_width) 
    worksheet_s.set_column('I:I', base_col_width)
    worksheet_s.set_column('J:J', base_col_width)
    worksheet_s.set_column('K:K', 50)
    worksheet_s.set_column('L:L', 50)
    worksheet_s.set_column('M:M', base_col_width)
    worksheet_s.set_column('N:N', base_col_width)
    worksheet_s.set_column('O:O', base_col_width)


    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data
        

