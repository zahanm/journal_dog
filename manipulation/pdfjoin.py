
from __future__ import print_function

import sys
import json
import itertools
import os.path
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE

from xhtml2pdf import pisa

import Image

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from pyPdf import PdfFileReader, PdfFileWriter

from utils import strip_extra_whitespace

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO

JOINED_FNAME = 'output/transcribed.pdf'
JOINED_HTML_FNAME = 'output/transcribed.html'
JOINED_SEARCHABLE = 'output/overlay.pdf'
PARA_PADDING = 25
HTML_HEAD = """
<html>
<head>
<style type="text/css">
.segment p {
  font-size: 16px;
  text-align: center;
  vertical-align: center;
}
.segment img {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style>
</head>
<body>
"""
HTML_FOOT = """
</body>
</html>
"""
HTML_PARA_SNIPPET = """
  <p>{0}</p>
"""
HTML_IMAGE_SNIPPET = """
  <img src="{0}" />
"""

def paint_original_segments(fnames, transcriptions, page):
  pdf_fname = 'tmp/search_{0}.pdf'.format(page)
  pdf = Canvas(pdf_fname, pagesize=A4)
  top = A4[1]
  for fname, transcription in itertools.izip(fnames, transcriptions):
    segment = Image.open(fname)
    width, height = segment.size
    p = Paragraph(transcription, ParagraphStyle('Normal', alignment=TA_CENTER))
    p.wrapOn(pdf, A4[0] - PARA_PADDING * 2, height)
    p.drawOn(pdf, PARA_PADDING, top - height / 2)
    pdf.drawImage(fname, 0, top - height)
    top -= height
  pdf.save()
  return pdf_fname

LATEX_TMP_FNAME = 'builder.{format}'
LATEX_SNIPPET = """
\\documentclass{{article}}
\\usepackage[margin=0in, paperwidth={width}pt, paperheight={height}pt]{{geometry}}
\\usepackage{{amsmath}}
\\begin{{document}}
\\begin{{{font_size}}}
\\begin{{center}}
\\vspace*{{\\fill}}
\\begin{{equation*}}
{raw_latex}
\\end{{equation*}}
\\vspace*{{\\fill}}
\\end{{center}}
\\end{{{font_size}}}
\\end{{document}}
"""

def math_equation_image(fname, raw_latex):
  segment = Image.open(fname)
  width, height = segment.size
  with open(os.path.join('tmp', LATEX_TMP_FNAME.format(format='tex')), 'w') as latex_file:
    latex_file.write(LATEX_SNIPPET.format(height=height, width=width, font_size='large', raw_latex=raw_latex.strip()))
  pdfcreator = ['pdflatex', '-interaction', 'batchmode', '-output-directory', 'tmp', LATEX_TMP_FNAME.format(format='tex')]
  child = Popen(pdfcreator, stdout=PIPE)
  retcode = child.wait()
  if retcode != 0:
    stdoutdata, stderrdata = child.communicate()
    sys.stderr.write(stdoutdata + '\n')
    return 'images/{0}'.format(fname)
    # raise RuntimeError('Error while creating math image with pdflatex')
  png_fname = os.path.join('output', 'images', os.path.basename(fname))
  converter = ['convert', os.path.join('tmp', LATEX_TMP_FNAME.format(format='pdf')), '-quality', '4', png_fname]
  child = Popen(converter, stdout=PIPE, stderr=PIPE)
  retcode = child.wait()
  if retcode != 0:
    stdoutdata, stderrdata = child.communicate()
    sys.stderr.write(stdoutdata + '\n' + stderrdata + '\n')
    return 'images/{0}'.format(fname)
    # raise RuntimeError('Error while converting math image using imagemagick')
  return os.path.join('images', os.path.basename(fname))

def assemble_transcribed_html(fnames, transcriptions, types):
  buf = StringIO()
  for fname, transcription, t_type in itertools.izip(fnames, transcriptions, types):
    buf.write('<div class="segment">')
    if t_type == 'math':
      raw_latex = strip_extra_whitespace(transcription)
      math_image_fname = math_equation_image(fname, raw_latex)
      buf.write(HTML_IMAGE_SNIPPET.format(math_image_fname))
    else:
      # transcription type is 'text'
      for line in transcription.split('\n'):
        buf.write(HTML_PARA_SNIPPET.format(line.strip()))
    buf.write('</div>\n')
  return buf.getvalue()

def join_pages(composites):
  # pisa.showLogging() # DEBUG
  joined_buf = StringIO()
  joined_buf.write(HTML_HEAD)
  pdf_fnames = []
  for page_num, collection in enumerate(collect_pages(composites)):
    fnames, transcriptions, types = [], [], []
    for r in collection:
      fnames.append(r['location'])
      transcriptions.append(r['transcription'])
      types.append(r['type'])
    page_html = assemble_transcribed_html(fnames, transcriptions, types)
    pdf_fnames.append(paint_original_segments(fnames, transcriptions, page_num))
    joined_buf.write(page_html)
    joined_buf.write("<div> <pdf:nextpage /> </div>\n")
  joined_buf.write(HTML_FOOT)
  # HTML and transcribed pdf
  with open(JOINED_HTML_FNAME, 'w') as html_file:
    html_file.write(joined_buf.getvalue())
  # with open(JOINED_FNAME, 'wb') as pdf_file:
  #   pdf = pisa.CreatePDF(joined_buf, pdf_file)
  # ---
  # searchable pdf
  pdf_writer = PdfFileWriter()
  pdf_pages = []
  for pdf_fname in pdf_fnames:
    pdf_pages.append(open(pdf_fname, 'rb'))
    pdf_reader = PdfFileReader(pdf_pages[-1])
    pdf_writer.addPage(pdf_reader.getPage(0))
  with open(JOINED_SEARCHABLE, 'wb') as pdf_searchable:
    pdf_writer.write(pdf_searchable)
  map(lambda f: f.close(), pdf_pages)
  return json.dumps({
    'transcribed_html': JOINED_HTML_FNAME,
    'transcribed_pdf': JOINED_FNAME,
    'searchable_pdf': JOINED_SEARCHABLE
  })


def collect_pages(composites):
  # first sort by page number
  composites.sort(key=lambda composite: composite['page'])
  for page, collection in itertools.groupby(composites, key=lambda composite: composite['page']):
    yield collection

def decode_dog_output(output_fname):
  output = None
  with open(output_fname) as dog_output:
    try:
      output = json.load(dog_output)
    except TypeError:
      pass
  if not output:
    print("{}")
    return None
  return output

if __name__ == '__main__':
  if len(sys.argv) == 2:
    composites = decode_dog_output(sys.argv[1])
    if composites:
      print(join_pages(composites))
  else:
    print('usage: python', __file__, '<output_from_dog>')
