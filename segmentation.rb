#!/usr/bin/env ruby

module ManReduce
  
  class Segmentation < Mapper
    
    attr_accessor :file_type
    attr_accessor :split_on_white_space
    
    def map(key, value)
      path = File.join(File.dirname($0), value)
      cache = File.join(File.dirname(path), "notes_segments.json")
      if File.exists?(cache) then
        string = File.read(cache)
        output = JSON.parse(string)
        for i in output do
          emit i["location"], i
        end
        
      else
        output = `python2.7 manipulation/pdfsplit.py #{path}`
        emit key, output
      end
    end
    
  end

end
