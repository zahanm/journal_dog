
from __future__ import print_function

import sys
import json
from pyPdf import PdfFileWriter, PdfFileReader

def split_pages(pdf_fname):
  out_fnames = []
  with open(pdf_fname, 'rb') as inp_file:
    inp = PdfFileReader(inp_file)
    for page in xrange(inp.getNumPages()):
      out = PdfFileWriter()
      out.addPage(inp.getPage(page))
      out_fnames.append('out_{0}.pdf'.format(page))
      with open(out_fnames[page], 'wb') as out_file:
        out.write(out_file)
  return out_fnames

def convert_pages(pdf_fnames):
  # TODO
  yield png_name

def divide_page(png_fname):
  # TODO
  yield segment_fname

def split_pdf(pdf_fname):
  output = []
  pdf_fnames = split_pages(pdf_fnames)
  for page, png_fname in enumerate(convert_pages(pdf_fnames)):
    for segment_fname in divide_page(png_fname)
      output.append({ 'segment': segment_fname, 'page': page })
  with open(dog_input_fname, 'w') as dog_input:
    json.dump(output, dog_input)

if __name__ == '__main__':
  if(len(sys.argv) == 2):
    split_pdf(sys.argv[1])
  else:
    print('usage: python', __file__, '<input_pdf>')
