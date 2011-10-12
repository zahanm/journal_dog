#
# Copyright 2011 by Zahan Malkani (zahanm@gmail.com).
# All rights reserved.
#
# Permission is granted for use, copying, modification, distribution,
# and distribution of modified versions of this work as long as the
# above copyright notice is included.
#

class TranscribeJournal < ManReduce::HumanMapper

  def initialize
    super
    self.template = "transcribe_journal.template"
    self.parameters["mode"] = "text"
  end
  
end
