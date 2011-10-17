
from __future__ import print_function

import sys
import json
import itertools
import os.path
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE
from shutil import move

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

OVERLAY_PDF_FNAME = 'output/overlay.pdf'
PARA_PADDING = 25

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

LATEX_WRAP = """
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\begin{{document}}
\\begin{{{font_size}}}
\\begin{{center}}
{raw_latex}
\\end{{center}}
\\end{{{font_size}}}
\\end{{document}}
"""

LATEX_EQN_SNIPPET = """
\\begin{{equation*}}
{0}
\\end{{equation*}}
"""

LATEX_NEWPAGE_SNIPPET = """
\\newpage
"""

LATEX_FONT_SIZE = 'large'

LATEX_TMP_FNAME = 'builder.{format}'
LATEX_PDF_FNAME = 'output/transcribed.pdf'

def latex_to_pdf(raw_latex):
  with open(os.path.join('tmp', LATEX_TMP_FNAME.format(format='tex')), 'w') as latex_file:
    latex_file.write(raw_latex)
  pdfcreator = ['pdflatex', '-interaction', 'nonstopmode', '-output-directory', 'tmp', LATEX_TMP_FNAME.format(format='tex')]
  child = Popen(pdfcreator, stdout=PIPE)
  retcode = child.wait()
  if retcode != 0:
    stdoutdata, stderrdata = child.communicate()
    sys.stderr.write(raw_latex + '\n')
    sys.stderr.write(stdoutdata + '\n')
    return LATEX_TMP_FNAME.format('tex')
    # raise RuntimeError('Error while creating math image with pdflatex')
  move(os.path.join('tmp', LATEX_TMP_FNAME.format(format='pdf')), LATEX_PDF_FNAME)
  return LATEX_PDF_FNAME

def assemble_latex(fnames, transcriptions, types):
  buf = StringIO()
  for transcription, t_type in itertools.izip(transcriptions, types):
    stripped = strip_extra_whitespace(transcription)
    if t_type == 'math':
      buf.write(LATEX_EQN_SNIPPET.format(stripped))
    else:
      # t_type= 'text'
      buf.write(stripped.replace('_', '\_').replace('^', '\^'))
  return buf.getvalue()

def join_pages(composites):
  latex_buf = StringIO()
  pdf_fnames = []
  for page_num, collection in enumerate(collect_pages(composites)):
    fnames, transcriptions, types = [], [], []
    for r in collection:
      fnames.append(r['location'])
      transcriptions.append(r['transcription'])
      types.append(r['type'])
    pdf_fnames.append(paint_original_segments(fnames, transcriptions, page_num))
    latex_buf.write(assemble_latex(fnames, transcriptions, types))
    latex_buf.write(LATEX_NEWPAGE_SNIPPET)
  raw_latex = LATEX_WRAP.format(raw_latex=latex_buf.getvalue(), font_size=LATEX_FONT_SIZE)
  # transcribed pdf
  latex_to_pdf(raw_latex)
  # ---
  # searchable pdf
  pdf_writer = PdfFileWriter()
  pdf_pages = []
  for pdf_fname in pdf_fnames:
    pdf_pages.append(open(pdf_fname, 'rb'))
    pdf_reader = PdfFileReader(pdf_pages[-1])
    pdf_writer.addPage(pdf_reader.getPage(0))
  with open(OVERLAY_PDF_FNAME, 'wb') as pdf_searchable:
    pdf_writer.write(pdf_searchable)
  map(lambda f: f.close(), pdf_pages)
  return json.dumps({
    'transcribed_pdf': LATEX_PDF_FNAME,
    'searchable_pdf': OVERLAY_PDF_FNAME
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
