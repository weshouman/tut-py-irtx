import logging

class Doc():
  def __init__(self, index="0", author_id="", text="", timestamp=""):
    self.index = index
    self.author_id = author_id
    self.text = text
    self.timestamp = timestamp

  def __lt__(self, other):
    return self.index < other.index

  def __str__(self):
    return f"{self.index} \tauthored by {self.author_id} \tat {self.timestamp}"

class Term():
  def __init__(self, text, occurances=None):
    self.text = Term.normalize(text)

    if occurances == None:
      self.occurances = []
    else:
      self.occurances = occurances

  verbose = False
  DEFAULT_VERBOSE_OCCURANCE_COUNT = 3

  @classmethod
  def normalize(cls, text):
    return text.lower().strip(",.")

  def update_count(self):
    self.count = len(self.occurances)

  def get_first_n_occurances(self, n=DEFAULT_VERBOSE_OCCURANCE_COUNT):
    return self.occurances[:n]

  def __lt__(self, other):
    return self.text < other.text

  @classmethod
  def get_header(cls):
    text  = "[Term text]"
    count = "[Count in docs]"
    occur = f"[first {cls.DEFAULT_VERBOSE_OCCURANCE_COUNT} occurances]"
    if Term.verbose:
      out =  f"\n{text:20} \t{count:>15} \t{occur}"
      out += f"\n{len(out)*'-'}--------"
    else:
      out =  f"\n{text:20} \t{count:15}"
      out += f"\n{len(out)*'-'}-"

    return out

  def __str__(self):
    if Term.verbose:
      out = f"{self.text:20} \t{self.count:15} \t{self.get_first_n_occurances()}"
    else:
      out = f"{self.text:20} \t{self.count:15}"
    return out

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
      doc_list = sorted(docs)
  else:
    raise("Unsupported Document type")

  term_dict = {}
  for doc in doc_list:
    term_dict = merge_terms(term_dict, get_terms(doc))
  return term_dict

def is_occurance_contained(occurances, query):
  for occurance in occurances:
    if query == occurance:
      return True
    elif query > occurance:
      return False

  return False

def merge_terms(term_dict, term_list):
  for term in term_list:
    if term.text in term_dict:
      # doing this check increases the time for a large dataset ~20 times from 4 to 63 seconds
      #if term.occurances[0] in term_dict[term.text].occurances:
      if is_occurance_contained(term_dict[term.text].occurances, term.occurances[0]):
        pass
      else:
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


