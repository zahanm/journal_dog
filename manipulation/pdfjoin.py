
from __future__ import print_function

import sys
import json
import itertools
from xhtml2pdf import pisa

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO

JOINED_FNAME = 'output/images.pdf'

def assemble_page(fnames, transcriptions):
  buf = StringIO()
  for fname in fnames:
    buf.write("<div class=\"segment\"><img src=\"{0}\"></div>\n".format(fname))
  return buf.getvalue()

def join_pages(composites):
  HTML_HEAD = """
  <html>
  <body>
  """
  HTML_FOOT = """
  </body>
  </html>
  """
  joined_buf = StringIO()
  joined_buf.write(HTML_HEAD)
  for collection in collect_pages(composites):
    fnames = map(lambda composite: composite['location'], collection)
    transcriptions = map(lambda composite: composite['transcription'], collection)
    page_html = assemble_page(fnames, transcriptions)
    joined_buf.write(page_html)
    joined_buf.write("<div> <pdf:nextpage /> </div>\n")
  joined_buf.write(HTML_FOOT)
  with open(JOINED_FNAME, 'wb') as pdf_file:
    pdf = pisa.CreatePDF(joined_buf, pdf_file)

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
      join_pages(composites)
  else:
    print('usage: python', __file__, '<output_from_dog>')
