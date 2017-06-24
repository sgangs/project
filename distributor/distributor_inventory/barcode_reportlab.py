from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
#I"ll be generating code39 barcodes, others are available
from reportlab.graphics.barcode import code39
from reportlab.graphics.barcode import code128


# generate a canvas (A4 in this case, size doesn"t really matter)
c=canvas.Canvas("barcode_example.pdf",pagesize=A4)

# barcode=code39.Extended39("123456789",barWidth=0.5*mm,barHeight=20*mm, humanReadable=True)

barcode = code128.Code128("123456789",barHeight=20*mm,barWidth = 0.3*mm)

# drawOn puts the barcode on the canvas at the specified coordinates
barcode.drawOn(c,5*mm,5*mm)   #Left bottom
barcode.drawOn(c,120*mm,5*mm)   #Right bottom
barcode.drawOn(c,5*mm,275*mm)   #Left top
barcode.drawOn(c,120*mm,275*mm)   #Right top

#start from left top, go to right top......and then print it out.

# now create the actual PDF
c.showPage()
c.save()