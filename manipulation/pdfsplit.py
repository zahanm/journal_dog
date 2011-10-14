
from __future__ import print_function

import sys
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

def divide_page(png_fname):
  out_fnames = []
  # TODO

if __name__ == '__main__':
  if(len(sys.argv) == 2):
    split_pages(sys.argv[1])
  else:
    print('usage: python', __file__, '<input_pdf>')
