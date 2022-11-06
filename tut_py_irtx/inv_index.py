import logging

class Doc():
  """A document is a representation of the structured form
     that the code retrieves info from"""
  def __init__(self, index="0", author_id="", text="", timestamp=""):
    self.index = index
    self.author_id = author_id
    self.text = text
    self.timestamp = timestamp

  def __lt__(self, other):
    return self.index < other.index

  def __str__(self):
    out = self.index

    if self.author_id:
      out += " \tauthored by {self.author_id}"

    if self.timestamp:
      out += " \tat {self.timestamp}"

    return out

class Term():
  """A term contains a text, the occurances list and the occurances count"""
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
    return text.lower().strip(",.#@")

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

def in_sorted(elems, query):
  """Check if query is located in the sorted elems"""
  for elem in elems:
    if query == elem:
      return True
    elif query > elem:
      return False

  return False

def slice_list_of_dict(indict, n):
  """Get a slice of the the input dictionary of size n"""
  outlist = []
  for i, (k, v) in enumerate(indict.items()):
    if i == n: break
    outlist.append(v)

  return outlist

def get_joint(list1, list2):
  """Return the join of 2 lists"""
  list1.extend(list2)
  return list(set(list1))

def get_joint_multi(lists):
  if len(lists) < 1:
    return []
  else:
    joint = []
    curr_list = lists[0]
    for curr_l in lists[1:]:
      joint = get_joint(curr_l, joint)

  return joint

def get_intersection(list1, list2):
  """Return the intersection of 2 lists"""
  # surprisingly, that doesn't save time
  # if list1[0] > list2[-1] or list2[0] > list1[-1]:
  #   return []

  iter1 = iter(list1)
  iter2 = iter(list2)

  intersection = []
  try:
    i = next(iter1)
    j = next(iter2)
    while True:
      if i == j:
        intersection.append(i)
        i = next(iter1)
        j = next(iter2)
      if i < j:
        i = next(iter1)
      if i > j:
        j = next(iter2)
  except StopIteration as ex:
    pass

  return intersection

class InvertedIndex():

  def __init__(self):
    self.doc_list = []
    self.doc_dict = {}
    self.is_doc_dict_built = False

  def build_doc_dict(self, force=False):
    if (force or self.is_doc_dict_built == False):
      for doc in self.doc_list:
        self.doc_dict.setdefault(doc.index, doc)
    self.is_doc_dict_built = True

  def build_indices(self, docs):
    """Build the inverted indices of the given doc(s) and return it"""
    if isinstance(docs, Doc):
      self.doc_list = [docs]
    elif isinstance(docs, list):
      if len(docs) > 0 and not isinstance(docs[0], Doc):
        raise("Unsupported Document type")
      else:
        self.doc_list = sorted(docs)
    else:
      raise("Unsupported Document type")

    indices = {}
    for doc in self.doc_list:
      indices = self.merge_terms(indices, self.get_terms(doc))
    return indices

  def get_terms(self, doc):
    """Get a list of terms given a doc"""
    if not isinstance(doc, Doc):
      raise("Unsupported Document type")

    text = doc.text

    tokens = text.split()
    terms = [Term(elem, [doc.index]) for elem in set(tokens)]
    return terms

  def merge_terms(self, indices, term_list):
    """Merge the term_list with the given indices and return the indices"""
    for term in term_list:
      if term.text in indices:
        # Doing this check increases the time for a large dataset
        #   ~20 times from 4 to 63 seconds
        #if term.occurances[0] in indices[term.text].occurances:
        if in_sorted(indices[term.text].occurances, term.occurances[0]):
          pass
        else:
          indices[term.text].occurances.extend(term.occurances)
      else:
        indices.setdefault(term.text, term)
      indices[term.text].update_count()

    # DO NOT DO THAT: it takes forever for large data
    #for key in indices:
    #  indices[key].update_count()

    return indices

  def slice_n_indices(self, indices, n = 10):
    """avoid packing all the indices at once, as usually n is very small"""
    return slice_list_of_dict(indices, n)

  def _regex_docs(self, regex):
    """This function is used for debugging purposes"""
    import re
    matched = []
    comp = re.compile(regex, re.IGNORECASE)
    for doc in self.doc_list:
      if comp.search(doc.text):
        matched.append(doc)
    return matched

  def query_docs(self, indices, text):
    """Query the intersection of documents in the indices
       that the given text appeared at"""
    if isinstance(text, str):
      text_list = [text]
    elif isinstance(text, list):
      text_list = text
    else:
      raise("Unexpected query type")

    if len(text_list) < 1:
      return []
    else:
      self.build_doc_dict()
      intersection = []
      term_list = []

      for text in text_list:
        text_normal = Term.normalize(text)
        if text_normal in indices.keys():
          term_list.append(indices[text_normal])

      if len(term_list) > 0:
        intersection = term_list[0].occurances

        for curr_term in term_list[1:]:
          curr_o = curr_term.occurances
          intersection = get_intersection(curr_o, intersection)

      return [self.doc_dict[elem] for elem in intersection]

