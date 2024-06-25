import segno
import io
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

qrcode = segno.make('JP5AC1DC18930505', micro=False)
buff = io.BytesIO()

# qrcode.save('./teste1.svg', kind='svg')
qrcode.save(buff, kind='svg', scale=10)

buff.seek(0)
print(buff.getvalue())
# drawing = svg2rlg('./teste1.svg')
drawing = svg2rlg(buff)
renderPDF.drawToFile(drawing, "./pdf/segno_test_10.pdf")
