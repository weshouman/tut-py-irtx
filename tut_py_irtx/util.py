def in_sorted(elems, query):
  """Check if query is located in the sorted elems"""
  for elem in elems:
    if query == elem:
      return True
    elif query > elem:
      return False

  return False

def slice_list_of_dict(indict, end, start=0):
  """Get a slice of the the input dictionary of size n"""
  outlist = []
  for i, (k, v) in enumerate(indict.items()):
    if i < start: break
    if end > 0 and i >= end: break
    outlist.append(v)

  return outlist

def normalize(text):
  return text.lower().strip(",.#@:\"")

