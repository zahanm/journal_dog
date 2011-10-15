
from __future__ import print_function

import sys
import os
import json
from subprocess import call, PIPE
from glob import glob

import Image

from pyPdf import PdfFileWriter, PdfFileReader

DOG_INPUT_FNAME = 'split.json'
SEGMENTS_PER_PAGE = 6

def split_pages(pdf_fname):
  out_fnames = []
  with open(pdf_fname, 'rb') as inp_file:
    inp = PdfFileReader(inp_file)
    for page in xrange(inp.getNumPages()):
      out = PdfFileWriter()
      out.addPage(inp.getPage(page))
      out_fnames.append('tmp/page_{0}.pdf'.format(page))
      with open(out_fnames[page], 'wb') as out_file:
        out.write(out_file)
  return out_fnames

def convert_pages(pdf_fnames):
  for page, pdf_fname in enumerate(pdf_fnames):
    png_fname = 'tmp/page_{0}.png'.format(page)
    args = ['convert', pdf_fname, '-quality', '4', png_fname]
    retcode = call(args)
    if retcode != 0:
      raise RuntimeError('Error while converting pdf to png')
    yield png_fname

def divide_page(page_num, png_fname):
  page = Image.open(png_fname)
  page_width, page_height = page.size
  segment_height = page_height / SEGMENTS_PER_PAGE
  left, upper, right, lower = 0, 0, page_width, segment_height
  for segment_num in xrange(SEGMENTS_PER_PAGE):
    segment_fname = 'data/segment_{0}_{1}.png'.format(page_num, segment_num)
    segment = page.copy()
    segment = segment.crop((left, upper, right, lower))
    segment.save(segment_fname)
    yield segment_fname
    upper += segment_height
    lower += segment_height

def split_pdf(pdf_fname):
  output = []
  pdf_fnames = split_pages(pdf_fname)
  for page, png_fname in enumerate(convert_pages(pdf_fnames)):
    for segment_fname in divide_page(page, png_fname):
      output.append({ 'location': segment_fname, 'page': page })
  with open(DOG_INPUT_FNAME, 'w') as dog_input:
    json.dump(output, dog_input)
  return json.dumps(output)

def cleanup_last_run():
  old_files = []
  old_files.extend(glob('data/*.png'))
  old_files.extend(glob('tmp/*.png'))
  old_files.extend(glob('tmp/*.pdf'))
  old_files.extend(glob('tmp/*.tex'))
  old_files.extend(glob('tmp/*.aux'))
  old_files.extend(glob('tmp/*.log'))
  old_files.extend(glob('tmp/*.pdf'))
  for old_file in old_files:
    os.remove(old_file)

if __name__ == '__main__':
  if(len(sys.argv) == 2):
    cleanup_last_run()
    print(split_pdf(sys.argv[1]))
  else:
    print('usage: python', __file__, '<input_pdf>')
