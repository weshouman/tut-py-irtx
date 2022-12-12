def in_sorted(elems, query):
  """Check if query is located in the sorted elems
  Returns
  -------
  -2 if interrupted
  -1 if search is complete without a result
  0 or positive number, the index of the matching element
  """
  for index, elem in enumerate(elems):
    # print(f"[query:{query}] [elem:{elem}]")
    if query == elem:
      return index
    elif query < elem:
      return -2

  return -1

def slice_list_of_dict(indict, end, start=0):
  """Get a slice of the input dictionary of size n"""
  outlist = []
  for i, (k, v) in enumerate(indict.items()):
    if i < start: break
    if end > 0 and i >= end: break
    outlist.append(v)

  return outlist

def normalize(text):
  return text.lower().strip(",.#@:\"")

