from flask import Flask, render_template, make_response
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, TextAreaField

import io
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register local fonts to report lab
# rl_config.TTFSearchPath.append('/home/ouaf/Projects/bkwrm_page_generator/fonts')
pdfmetrics.registerFont(TTFont('EnglishLing', 'EnglishLing-Regular.ttf'))
# pdfmetrics.registerFont(TTFont('Jarman', 'Jarman.ttf'))
pdfmetrics.registerFont(TTFont('Xumin', 'Xumin.ttf'))

# TODO: 
#   limit char/line in textarea https://codepen.io/chisenires/pen/eRWMZo (js)
#

SECRET_KEY = 'waf'

app = Flask(__name__)
app.config.from_object(__name__)

### WTForm ###
class MyForm(FlaskForm):
    title = StringField('title')
    lines = RadioField('lines', choices=[('6','6 （大）'),('8','8 （中）'),('10','10 （小）'),('12','12 （特小）')])
    text = TextAreaField('text')

### Create pdf function ###
def create_pdf(my_canvas, title, lines_per_page, text):
    lines = text.splitlines()
    number_of_pages = math.ceil(len(text.splitlines())/int(lines_per_page))
    if number_of_pages == 0:
        number_of_pages = 1
    line_spacing  = (A4[1]*0.95) / (int(lines_per_page) +1) / 5
    fontsize = 300 / int(lines_per_page)

    for p in range(1, number_of_pages+1):
        ### Write title and page number
        # my_canvas.setFont('Times-Italic', fontsize)
        my_canvas.setFont('Times-Roman', fontsize)
        page_tag = f"({p}/{number_of_pages})"
        txt = f"{title} {page_tag}"
        my_canvas.drawString(40, A4[1]-50, txt)

        ### Write logo
        my_canvas.drawImage('bookworm.jpg', 500, 700, width=90,
                 preserveAspectRatio=True, mask='auto')


        ### Write lines
        # initialize x and y
        x1 = 40
        x2 = 555
        y = A4[1] - (line_spacing * 6)

        for l in range(int(lines_per_page)):
            my_canvas.setLineWidth(.4)
            my_canvas.line(x1, y, x1, (y - line_spacing * 3))
            my_canvas.line(x2, y, x2, (y - line_spacing * 3))
            my_canvas.line(x1, y, x2, y)
            my_canvas.line(x1, (y - line_spacing*2), x2, (y - line_spacing*2))
            my_canvas.setDash(2, 3)
            my_canvas.line(x1, (y - line_spacing), x2, (y - line_spacing))
            my_canvas.line(x1, (y - line_spacing*3), x2, (y - line_spacing*3))
            my_canvas.setDash(array=[], phase=0)
            y -= (line_spacing * 5)

        ### Write text for that page
        # initialize x and y
        # y = A4[1] - (line_spacing * 8)
        y = A4[1] - (line_spacing * 9) + 1  # for EnglishLing

        # fetch lines index
        first_line_idx = (p-1)*(int(lines_per_page))
        last_line_idx = (p-1)*(int(lines_per_page))+int(lines_per_page)
        # fontsize2 = 350 / int(lines_per_page)
        fontsize2 = 460 / int(lines_per_page)     # For EnglishLing

        for l in lines[first_line_idx:last_line_idx]:
            # my_canvas.setFont('Xumin', fontsize2)
            my_canvas.setFont('EnglishLing', fontsize2)
            # my_canvas.setFillColor(HexColor(0xdddddd))
            my_canvas.drawString(44, y, l)
            y -= (line_spacing * 5)

        ### Go to next page
        if p < number_of_pages:
            my_canvas.showPage()


### Flask routes ###
@app.route('/',methods=['post','get'])
def hello_world():
    form = MyForm()
    if form.validate_on_submit():
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)

        create_pdf(p, form.title.data, form.lines.data, form.text.data)

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        resp = make_response(pdf)
        resp.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        resp.headers["Content-type"] = "application/pdf"
        return resp
    else:
        print(form.errors)
    return render_template('index.html',form=form)

if __name__ == '__main__':
    app.run(debug=True)