
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
HTML_HEAD = """
<html>
<head>
<style type="text/css">
.segment img {
  z-index: 10;
}
.segment span {
  z-index: 1;
  position: relative;
  left: -50%;
  text-align: center;
  vertical-align: center;
}
</style>
</head>
<body>
"""
HTML_FOOT = """
</body>
</html>
"""
SEARCHABLE_SNIPPET = """
<div class=\"segment\">
  <img src=\"{0}\">
  <span>{1}</span>
</div>
"""


def assemble_page(fnames, transcriptions):
  buf = StringIO()
  for fname, transcription in itertools.izip(fnames, transcriptions):
    buf.write(SEARCHABLE_SNIPPET.format(fname, transcription))
  return buf.getvalue()

def join_pages(composites):
  joined_buf = StringIO()
  joined_buf.write(HTML_HEAD)
  for collection in collect_pages(composites):
    fnames, transcriptions = [], []
    for r in collection:
      fnames.append(r['location'])
      transcriptions.append(r['transcription'])
    page_html = assemble_page(fnames, transcriptions)
    joined_buf.write(page_html)
    joined_buf.write("<div> <pdf:nextpage /> </div>\n")
  joined_buf.write(HTML_FOOT)
  print(joined_buf.getvalue())
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
