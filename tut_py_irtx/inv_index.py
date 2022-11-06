import logging

class Doc():
  def __init__(self, index="0", author_id="", text="", timestamp=""):
    self.index = index
    self.author_id = author_id
    self.text = text
    self.timestamp = timestamp

class Term():
  def __init__(self, text, occurances=None):
    self.text = Term.normalize(text)

    if occurances == None:
      self.occurances = []
    else:
      self.occurances = occurances

  @classmethod
  def normalize(cls, text):
    return text.lower()

  def update_count(self):
    self.count = len(self.occurances)

  def __lt__(self, other):
    return self.text < other.text

  def __str__(self):
    return f"{self.text} \tfound in {self.count} doc(s)"

def get_terms(doc):
  if not isinstance(doc, Doc):
    raise("Unsupported Document type")

  text = doc.text

  tokens = text.split()
  terms = [Term(elem, [doc.index]) for elem in set(tokens)]
  return terms

def get_term_dict(docs):
  if isinstance(docs, Doc):
    doc_list = [docs]
  elif isinstance(docs, list):
    if len(docs) > 0 and not isinstance(docs[0], Doc):
      raise("Unsupported Document type")
    else:
      doc_list = docs
  else:
    raise("Unsupported Document type")

  term_dict = {}
  for doc in doc_list:
    term_dict = merge_terms(term_dict, get_terms(doc))
  return term_dict

def merge_terms(term_dict, term_list):
  for term in term_list:
    if term.text in term_dict:
      # doing this check increases the time for a large dataset 20 times from 3 to 63 seconds
      # if term.occurances[0] in term_dict[term.text].occurances:
      #   pass
      # else:
      #   term_dict[term.text].occurances.extend(term.occurances)
      term_dict[term.text].occurances.extend(term.occurances)
    else:
      term_dict.setdefault(term.text, term)
    term_dict[term.text].update_count()

  # DO NOT DO THAT: it takes forever for large data
  #for key in term_dict:
  #  term_dict[key].update_count()

  return term_dict

def get_n_indices(indices, n = 10):
  """avoid packing all the indices at once, as usually n is very small"""
  indices_slice = []
  for i, (k, v) in enumerate(indices.items()):
    if i == n: break
    indices_slice.append(v)

  return indices_slice


