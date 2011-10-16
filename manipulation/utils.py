
def strip_extra_whitespace(s):
  o = []
  for line in s.split('\n'):
    if line.strip():
      o.append(line.strip())
  return '\n'.join(o)
