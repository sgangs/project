import datetime as dt
from datetime import datetime
from io import BytesIO
import xlsxwriter

# from django.db import transaction
from django.utils.translation import ugettext
# from .models import Student


def title_format(workbook):
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })    
    return title

def header_format(workbook):
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })    
    return header

def cell_format(workbook):
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })    
    return cell

def cell_center_format(workbook):
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1
    })    
    return cell_center

def cell_left_format(workbook):
    cell_left = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'border': 1
    })    
    return cell_left

def bold_format(workbook):
    title = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })    
    return title

def account_excel(items, data_type):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("Summary")
    title=title_format(workbook)
    header=header_format(workbook)
    cell=cell_format(workbook)
    cell_center=cell_center_format(workbook)
       
    title_text = u"{0}".format(ugettext(data_type))
    # merge cells
    worksheet_s.merge_range('A2:H2', title_text, title)

    # write header
    worksheet_s.write(4, 0, ugettext("No"), header)
    worksheet_s.write(4, 1, ugettext("Ledger Group Name"), header)
    worksheet_s.write(4, 2, ugettext("Account Name"), header)
    worksheet_s.write(4, 3, ugettext("Account Type"), header)
    worksheet_s.write(4, 4, ugettext("Account Key"), header)
    worksheet_s.write(4, 5, ugettext("Remarks"), header)
    worksheet_s.write(4, 6, ugettext("Current Debit"), header)
    worksheet_s.write(4, 7, ugettext("Current Credit"), header)
    
    # column widths definition
    base_col_width = 16
    
    #add data to table
    for idx, data in enumerate(items):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write(row, 1, data.ledger_group.name, cell_center)
        worksheet_s.write(row, 2, data.name, cell_center)
        worksheet_s.write(row, 3, data.account_type, cell_center)
        worksheet_s.write(row, 4, data.key, cell_center)
        worksheet_s.write(row, 5, data.remarks, cell_center)
        worksheet_s.write(row, 6, data.current_debit, cell_center)
        worksheet_s.write(row, 7, data.current_credit, cell_center)        
    
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data


def trail_balance_excel(items, data_type):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    worksheet_s = workbook.add_worksheet("Trial Balance")
    title=title_format(workbook)
    header=header_format(workbook)
    cell=cell_format(workbook)
    cell_center=cell_center_format(workbook)
       
    title_text = u"{0}".format(ugettext(data_type))
    # merge cells
    worksheet_s.merge_range('A2:D2', title_text, title)

    # write header
    worksheet_s.write(4, 0, ugettext("Account Type"), header)
    worksheet_s.write(4, 1, ugettext("Account Name"), header)
    worksheet_s.write(4, 2, ugettext("Debit Value"), header)
    worksheet_s.write(4, 3, ugettext("Credit Value"), header)
    
    # column widths definition
    base_col_width = 16
    
    #add data to table
    for idx, data in enumerate(items):
        row = 5 + idx
        if (data['data_type'] == 'journal'):
            worksheet_s.write(row, 0, data['account_type'], cell_center)
            worksheet_s.write(row, 1, data['account'], cell_center)
            worksheet_s.write(row, 2, data['debit'], cell_center)
            worksheet_s.write(row, 3, data['credit'], cell_center)
        elif (data['data_type'] == 'value'):
            worksheet_s.write(row, 0, "Total", cell_center)
            worksheet_s.write(row, 1, "", cell_center)
            worksheet_s.write(row, 2, data['debit'], cell_center)
            worksheet_s.write(row, 3, data['credit'], cell_center)        
    
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data

def profit_loss_excel(items, data_type):
    final_row=5
    row=0
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'constant_memory': True})
    worksheet_s = workbook.add_worksheet("Income And Expenditure")
    title=title_format(workbook)
    header=header_format(workbook)
    cell=cell_format(workbook)
    cell_center=cell_center_format(workbook)
    cell_left=cell_left_format(workbook)
    cell_bold=bold_format(workbook)
       
    title_text = u"{0}".format(ugettext(data_type))
    # merge cells
    worksheet_s.merge_range('A2:B2', title_text, title)

    # write header
    worksheet_s.write(4, 0, ugettext(" "), header)
    worksheet_s.write(4, 1, ugettext("Total"), header)    
    
    # column widths definition
    base_col_width = 40
    
    #add Income data to table
    worksheet_s.write(final_row, 0, 'Income', cell_left)
    final_row+=1
    i=0
    for idx, data in enumerate(items):
        if (data['data_type'] == 'income'):            
            row = final_row + i
            worksheet_s.write(row, 0, data['account'], cell_center)
            worksheet_s.write(row, 1, data['total'], cell_center)
            i+=1
    final_row=row+1

    #add Expense data to table
    worksheet_s.write(final_row, 0, 'Expense', cell_left)
    final_row+=1
    i=0
    for idx, data in enumerate(items):
        if (data['data_type'] == 'expense'):
            row = final_row + i
            worksheet_s.write(row, 0, data['account'], cell_center)
            worksheet_s.write(row, 1, data['total'], cell_center)
            i+=1
    final_row=row+2
    #add Gross Income data to table
    for idx, data in enumerate(items):
        if (data['data_type'] == 'gross'):
            if(float(data['income']) >=0):
                worksheet_s.write(final_row, 0, "Gross Income Over Expenditure", cell_bold)
                worksheet_s.write(final_row, 1, float(data['income']), cell_bold)
            else:
                worksheet_s.write(final_row, 0, "Gross Expenditure Over Income", cell_bold)
                worksheet_s.write(final_row, 1, float(data['income'])*(-1), cell_bold)
    final_row+=1
    #add Other Income data to table
    worksheet_s.write(final_row, 0, 'Other Income', cell_left)
    final_row+=1
    i=0
    for idx, data in enumerate(items):
        if (data['data_type'] == 'other_income'):
            row = final_row + i
            worksheet_s.write(row, 0, data['account'], cell_center)
            worksheet_s.write(row, 1, data['total'], cell_center)
            i+=1
    
    if (i==0):
        worksheet_s.write(final_row, 0, "", cell_center)
        worksheet_s.write(final_row, 1, " ", cell_center)
        final_row+=1
    else:
        final_row=row+1

    #add Other Expense data to table
    worksheet_s.write(final_row, 0, 'Other Expense', cell_left)
    final_row+=1
    i=0
    for idx, data in enumerate(items):
        if (data['data_type'] == 'other_expense'):
            row = final_row + i
            worksheet_s.write(row, 0, data['account'], cell_center)
            worksheet_s.write(row, 1, data['total'], cell_center)
            i+=1
    final_row=row+1

    #add Net Income data to table
    for idx, data in enumerate(items):
        if (data['data_type'] == 'net'):
            if(float(data['income']) >=0):
                worksheet_s.write(final_row, 0, "Net Income Over Expenditure", cell_bold)
                worksheet_s.write(final_row, 1, float(data['income']), cell_bold)
            else:
                worksheet_s.write(final_row, 0, "Net Expenditure Over Income", cell_bold)
                worksheet_s.write(final_row, 1, float(data['income'])*(-1), cell_bold)
    

    # column widths
    worksheet_s.set_column('A:A', base_col_width)
    worksheet_s.set_column('B:B', base_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data

# def profit_loss_entry(items, worksheet_s, call_type, final_row):
    