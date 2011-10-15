#
# Copyright 2011 by Zahan Malkani (zahanm@gmail.com).
# All rights reserved.
#
# Permission is granted for use, copying, modification, distribution,
# and distribution of modified versions of this work as long as the
# above copyright notice is included.
#

def split_pdf(pdf_fname)
  dog_input = `python2.7 manipulation/pdfsplit.py #{pdf_fname}`
  emit dog_input
end

=begin
dog output format:
[
  {
    "location": "data/segment_0_1.png",
    "transcription": "Hellow out there",
    "page": 0
  },
  ...
]
=end

def join_images(json_output_fname)
  dog_output = `python2.7 manipulation/pdfjoin.py #{json_output_fname}`
  emit dog_output
end
