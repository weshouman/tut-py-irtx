import logging

from tut_py_irtx.util import *
from tut_py_irtx.Doc import *
import tut_py_irtx.Term
from tut_py_irtx.InvertedIndexer import *
from tut_py_irtx.DocIndexer import *
from tut_py_irtx.KGramIndexer import *

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

class IndexController():

  def __init__(self, docs=None):

    self.indexers = []
    self.add_indexer(InvertedIndexer())
    self.add_indexer(DocIndexer())
    self.add_indexer(KGramIndexer(k=2))

    if docs:
      self.set_docs(docs)
    else:
      self.doc_list = []

    self.doc_index = {}
    self.is_doc_index_built = False

  def add_indexer(self, indexer):
    self.indexers.append(indexer)

  def set_docs(self, docs):
    if isinstance(docs, Doc):
      self.doc_list = [docs]
    elif isinstance(docs, list):
      if len(docs) > 0 and not isinstance(docs[0], Doc):
        raise TypeError("Unsupported Document type")
      else:
        self.doc_list = sorted(docs)
    else:
      raise TypeError("Unsupported Document type")

    for indexer in self.indexers:
      # TODO: ensure not updating here follows the least astonishment principle
      # indexer.doc_list = self.doc_list
      indexer.invalidate()

  def doc_indexer(self):
    for indexer in self.indexers:
      if isinstance(indexer, DocIndexer):
        return indexer
    raise(IndexNotFoundError(DocIndexer))

  def inv_indexer(self):
    for indexer in self.indexers:
      if isinstance(indexer, InvertedIndexer):
        return indexer
    raise(IndexNotFoundError(InvertedIndexer))

  def kgram_indexer(self):
    for indexer in self.indexers:
      if isinstance(indexer, KGramIndexer):
        return indexer
    raise(IndexNotFoundError(KGramIndexer))

  def get_inv_index(self):
    return self.inv_indexer().index

  def set_inv_index(self, index):
    self.inv_indexer().index = index

  def build(self, force=False):
    for indexer in self.indexers:
      indexer.doc_list = self.doc_list
      indexer.build(force)

  def get_doc_index_slice(self, n = 10):
    """Unpack and return n doc indexers"""
    return self.doc_indexer().get_slice(n)

  def get_inv_index_slice(self, n = 10):
    """Unpack and return n inverted indexers"""
    return self.inv_indexer().get_slice(n)

  def get_kgram_index_slice(self, n = 10):
    """Unpack and return n kgram indexers"""
    return self.kgram_indexer().get_slice(n)

  def _regex_docs(self, regex):
    """This function is used for debugging purposes"""
    import re
    matched = []
    comp = re.compile(regex, re.IGNORECASE)
    for doc in self.doc_list:
      if comp.search(doc.text):
        matched.append(doc)
    return matched

  def query_intersection_wildcards(self, text):
    """Query the intersection of documents in the indexers
       that the given text appeared at, with wildcard support"""
    if isinstance(text, str):
      text_list = [text]
    elif isinstance(text, list):
      text_list = text
    else:
      raise TypeError("Unexpected query type")

    if len(text_list) < 1:
      return []
    else:
      self.build()
      intersection = []
      term_list = []

      # through intersecting kgrams, expand the wildcard text into text to be searched for
      text_list_exp = []
      kgram_index = self.kgram_indexer().index
      for text in text_list:
        if ("*" in text):
          terms = KGramIndexer.wildcard_to_terms(text, kgram_index)
          text_list_exp.extend(terms)
        else:
          text_list_exp.append(text)

      # search for documents that have the expanded text
      for text in text_list_exp:
        text_normal = util.normalize(text)
        inv_index = self.inv_indexer().index
        if text_normal in inv_index.keys():
          term_list.append(inv_index[text_normal])

      if len(term_list) > 0:
        intersection = term_list[0].occurances

        for curr_term in term_list[1:]:
          curr_o = curr_term.occurances
          intersection = get_intersection(curr_o, intersection)

      doc_index = self.doc_indexer().index
      return [doc_index[elem] for elem in intersection]

  def query_intersection(self, text):
    """Query the intersection of documents in the invereted index
       that the given text appeared at"""
    if isinstance(text, str):
      text_list = [text]
    elif isinstance(text, list):
      text_list = text
    else:
      raise TypeError("Unexpected query type")

    if len(text_list) < 1:
      return []
    else:
      # better be sure that the indices are built
      self.build()

      # lists to be filled
      intersection = []
      term_list = []

      for text in text_list:
        text_normal = Term.normalize(text)
        inv_index = self.inv_indexer().index
        if text_normal in inv_index.keys():
          term_list.append(inv_index[text_normal])

      if len(term_list) > 0:
        intersection = term_list[0].occurances

        for curr_term in term_list[1:]:
          curr_o = curr_term.occurances
          intersection = get_intersection(curr_o, intersection)

      doc_index = self.doc_indexer().index
      return [doc_index[elem] for elem in intersection]

