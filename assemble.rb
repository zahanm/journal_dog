#!/usr/bin/env ruby

module ManReduce
  
  class Assemble < Reducer
    
    attr_accessor :path
    
    def reduce(key, values)
      segments = File.join(File.dirname($0), "segments.json")
      
      file = File.open(segments, 'w')
      file.write(values.to_json)
      
      #if !File.exists?(segments) then
      #end
      `python2.7 manipulation/pdfjoin.py #{segments}`
      
    end
    
  end

end
