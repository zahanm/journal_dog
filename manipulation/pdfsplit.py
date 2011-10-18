
from __future__ import print_function

import sys
import os
import json
from subprocess import call
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

# --- UIST HACK START

SPLIT_HEIGHTS = [
  [138, 180, 214, 292, 323, 355, 374, 450, 500, 560, 630, 683, 731],
  [180, 244, 275, 343, 361, 400, 424, 460, 481, 565, 598, 734],
  [133, 153, 170, 227, 257, 286, 313, 405, 425, 493, 603, 621, 726],
  [105, 168, 244, 295, 368, 720],
  [122, 155, 241, 277, 308, 480, 510, 540, 592, 616, 723],
  [190, 224, 450, 479, 717]
]

def divide_page_manual(page_num, png_fname):
  page = Image.open(png_fname)
  page_width, page_height = page.size
  left, upper, right = 0, 0, page_width
  for segment_num, lower in enumerate(SPLIT_HEIGHTS[page_num]):
    segment_fname = 'data/segment_{0}_{1}.png'.format(page_num, segment_num)
    segment = page.copy()
    segment = segment.crop((left, upper, right, lower))
    segment.save(segment_fname)
    yield segment_fname
    upper = lower

# --- UIST HACK END

def split_pdf(pdf_fname):
  output = []
  pdf_fnames = split_pages(pdf_fname)
  for page, png_fname in enumerate(convert_pages(pdf_fnames)):
    for segment_fname in divide_page_manual(page, png_fname): # divide_page(page, png_fname)
      output.append({ 'location': segment_fname, 'page': page })
  with open(DOG_INPUT_FNAME, 'w') as dog_input:
    json.dump(output, dog_input)
  return json.dumps(output)

def cleanup_last_run():
  file_globs = ['data/*.png', 'tmp/*.pdf', 'tmp/*.png', 'tmp/*.tex',
    'tmp/*.aux', 'tmp/*.log', 'output/*.pdf']
  old_files = []
  map(lambda fg: old_files.extend(glob(fg)), file_globs)
  map(lambda old_file: os.remove(old_file), old_files)

if __name__ == '__main__':
  if(len(sys.argv) == 2):
    cleanup_last_run()
    print(split_pdf(sys.argv[1]))
  else:
    print('usage: python', __file__, '<input_pdf>')
