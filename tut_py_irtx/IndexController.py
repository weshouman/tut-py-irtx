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

def get_intersection_of_sorted(list1, list2):
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

  def query_intersection_core(self, text_list, support_wildcards_kgram=True):
    """Core query function

    Parameters
    ----------
    text_list : list of str
      Text to query
    support_wildcards_kgram : bool
      Whether to support wildcard expansion using kgrams or not

    Returns
    -------
    list
      Docs corresponding to the given query text_list
    """
    ii = self.inv_indexer()

    out_docs = []
    for i, text in enumerate(text_list):
      text_docs = []

      if (support_wildcards_kgram and "*" in text):
        # kgram index is used only if support_wildcard_kgrams is used
        kgram_index = self.kgram_indexer().index
        wc_exp_list = KGramIndexer.expand_wildcard_to_list(text, kgram_index)
        for wc_exp in wc_exp_list:
          term = ii.get_corresponding_term(util.normalize(wc_exp))
          if term is not None:
            text_docs = get_joint(text_docs, term.occurances)

      else:
        term = ii.get_corresponding_term(util.normalize(text))
        if term is not None:
          text_docs = term.occurances

      # enable for extensive debugging only
      # logging.debug(f"[{text}] found in the docs: {text_docs}")

      if i == 0:
        out_docs = text_docs
      else:
        out_docs = get_intersection_of_sorted(sorted(out_docs), sorted(text_docs))

      logging.debug(f"[DOC-INTERSECTION]: {out_docs}")

    return out_docs

  def query_intersection_wildcards(self, text):
    return self.query_intersection(text, True)

  def query_intersection(self, text, wildcard=False):
    """Query the intersection of documents in the indexers
       that the given text appeared at, with wildcard support"""
    if isinstance(text, str):
      text_list = [text]
    elif isinstance(text, list):
      text_list = text
    else:
      raise TypeError("Unexpected query type")

    self.build()

    docs = self.query_intersection_core(text_list, support_wildcards_kgram=wildcard)

    doc_index = self.doc_indexer().index
    return [doc_index[doc] for doc in docs]

