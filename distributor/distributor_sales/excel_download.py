import datetime as dt
from datetime import datetime
from io import BytesIO
import xlsxwriter

from django.utils.translation import ugettext


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

def header_date_format(workbook):
    header_date = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'num_format': 'dd-mm-yyyy'
    })    
    return header_date

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

def sales_invoice_excel(line_items, invoice, tenant):
    discount_options=['Nil','%','Value']
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("Purchase Invoice")
    title=title_format(workbook)
    header=header_format(workbook)
    header_date=header_date_format(workbook)
    cell=cell_format(workbook)
    cell_center=cell_center_format(workbook)
       
    title_text = u"{0}".format(ugettext("Sales Tax Invoice"))
    # merge cells
    worksheet_s.merge_range('A2:S2', title_text, title)

    # write invoice metadata-1
    worksheet_s.merge_range("A5:C5", ugettext("Sold To"), header)
    worksheet_s.merge_range("F5:H5", ugettext("Sales Invoice No"), header)
    worksheet_s.merge_range("K5:M5", ugettext("Sold By"), header)
    worksheet_s.merge_range("P5:R5", ugettext("Date"), header)

    worksheet_s.merge_range("A6:C6", invoice.customer_name, header)
    worksheet_s.merge_range("A7:C7", invoice.customer_address, header)
    worksheet_s.merge_range("A8:C8", invoice.customer_gst, header)
    
    worksheet_s.merge_range("F6:H6", invoice.invoice_id, header)
    
    worksheet_s.merge_range("K6:M6", tenant.name, header)
    worksheet_s.merge_range("K7:M7", tenant.address_1+", "+tenant.address_2, header)
    worksheet_s.merge_range("K8:M8", tenant.gst, header)
    
    format4 = workbook.add_format({'num_format': 'dd-mm-yyyy'})
    worksheet_s.merge_range("P6:R6", invoice.date, header_date)

    # header=14

    # write header
    worksheet_s.write(12, 0, ugettext("Item"), header)
    worksheet_s.write(12, 1, ugettext("HSN Code"), header)
    worksheet_s.write(12, 2, ugettext("Qty"), header)
    worksheet_s.write(12, 3, ugettext("Unit"), header)
    worksheet_s.write(12, 4, ugettext("Sales Price"), header)
    worksheet_s.write(12, 5, ugettext("MRP"), header)
    worksheet_s.write(12, 6, ugettext("Discount Type -1"), header)
    worksheet_s.write(12, 7, ugettext("Discount Value -1"), header)
    worksheet_s.write(12, 8, ugettext("Discount Type -2"), header)
    worksheet_s.write(12, 9, ugettext("Discount Value -2"), header)
    worksheet_s.write(12, 10, ugettext("Taxable Total"), header)
    worksheet_s.write(12, 11, ugettext("CGST %"), header)
    worksheet_s.write(12, 12, ugettext("CGST Amt"), header)
    worksheet_s.write(12, 13, ugettext("SGST %"), header)
    worksheet_s.write(12, 14, ugettext("SGST Amt"), header)
    worksheet_s.write(12, 15, ugettext("IGST %"), header)
    worksheet_s.write(12, 16, ugettext("IGST Amt"), header)
    worksheet_s.write(12, 17, ugettext("Total"), header)
    
    # column widths definition
    base_col_width = 16
    
    #add data to table
    row=14
    for data in line_items:
        worksheet_s.write(row, 0, data['product_name'], cell_center)
        worksheet_s.write(row, 1, data['product_hsn'], cell_center)
        worksheet_s.write(row, 2, data['quantity'], cell_center)
        worksheet_s.write(row, 3, data['unit'], cell_center)
        worksheet_s.write(row, 4, (data['sales_price']), cell_center)
        worksheet_s.write(row, 5, (data['mrp']), cell_center)
        worksheet_s.write(row, 6, discount_options[data['discount_type']], cell_center)
        worksheet_s.write(row, 7, (data['discount_value']), cell_center)
        worksheet_s.write(row, 8, discount_options[data['discount2_type']], cell_center)
        worksheet_s.write(row, 9, (data['discount2_value']), cell_center)
        worksheet_s.write(row, 10, (data['line_tax']), cell_center)
        worksheet_s.write(row, 11, (data['cgst_percent']), cell_center)
        worksheet_s.write(row, 12, (data['cgst_value']), cell_center)        
        worksheet_s.write(row, 13, (data['sgst_percent']), cell_center)
        worksheet_s.write(row, 14, (data['sgst_value']), cell_center)
        worksheet_s.write(row, 15, (data['igst_percent']), cell_center)
        worksheet_s.write(row, 16, (data['igst_value']), cell_center)        
        worksheet_s.write(row, 17, (data['line_total']), cell_center)
        row+=1


    worksheet_s.write(row+2, 16, ugettext("Subtotal"), header)
    worksheet_s.write(row+3, 16, ugettext("Total Tax"), header)
    worksheet_s.write(row+4, 16, ugettext("TOtal"), header)

    worksheet_s.write(row+2, 17, invoice.subtotal, header)
    worksheet_s.write(row+3, 17, (invoice.total - invoice.subtotal), header)
    worksheet_s.write(row+4, 17, invoice.total, header)

    wide_col_width = 25
    base_col_width = 10

    worksheet_s.set_column('A:A', wide_col_width)
    worksheet_s.set_column('B:B', base_col_width)
    worksheet_s.set_column('C:C', base_col_width)
    worksheet_s.set_column('D:D', base_col_width)
    worksheet_s.set_column('E:E', base_col_width)
    worksheet_s.set_column('F:F', base_col_width)
    worksheet_s.set_column('G:G', base_col_width)
    worksheet_s.set_column('H:H', base_col_width)
    worksheet_s.set_column('I:I', base_col_width)
    worksheet_s.set_column('J:J', base_col_width)
    worksheet_s.set_column('K:K', base_col_width)
    worksheet_s.set_column('L:L', base_col_width)
    worksheet_s.set_column('M:M', base_col_width)
    worksheet_s.set_column('N:N', base_col_width)
    worksheet_s.set_column('O:O', base_col_width)
    worksheet_s.set_column('P:P', base_col_width)
    worksheet_s.set_column('Q:Q', base_col_width)
    worksheet_s.set_column('R:R', base_col_width)
    worksheet_s.set_column('S:S', base_col_width)
    
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data

    