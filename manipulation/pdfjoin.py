
from __future__ import print_function

import sys
import json
from pyPdf import PdfFileWriter

def assemble_page(fnames, transcriptions):
  # TODO

def join_pages(composites):
  joined_fname = 'output.pdf'
  joined_writer = PdfFileWriter()
  for collection in collect_pages(composites):
    fnames = filter(lambda composite: return composite['fname'], composites)
    transcriptions = filter(lambda composite: return composite['transcription'], composites)
    page_fname = assemble_page(fnames, transcriptions):
    with open(page_fname, 'rb') as page:
      page_reader = PDFFileReader(page)
      joined_writer.addPage(page_reader.getPage(0))
  with open(joined_fname, 'wb') as joined_file:
    joined_writer.write(joined_file)

def collect_pages(composites):
  # first sort by page number
  composites.sort(key=lambda composite: return composite['page'])
  collection = []
  current_page = 1
  for segment in composites:
    if segment['page'] != current_page:
      yield collection
      collection = []
      current_page = segment['page']
    collection.append(segment)

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
  return output['data']

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('usage: python', __file__, 'output.json')
    return
  composites = decode_dog_output(sys.argv[1])
  if composites:
    join_pages(composites)
