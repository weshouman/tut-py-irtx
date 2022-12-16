import logging

from tut_py_irtx.errors import *
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
        self.doc_list = sorted(docs, reverse=True)
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
      # doc_list is saved twice, can we fix that?
      # if so, we need to cleanup
      indexer.set_docs(self.doc_list)
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

  def get_query_frequencies(queries):
    """ fetch the tfs and idfs of the terms in the queries"""
    queryDoc = Doc(text=" ".join(queries))
    terms = Doc.fetch_terms(queryDoc)
    unique_terms = set(terms)

    uterm_counts = []
    qtfs = []
    qidfs = []

    # This loop is only necessary when (len(set(terms)) != len(terms))
    # however, it's not necessary to treat that specially,
    # query terms won't exceed a hundred anyway
    for i, uterm in enumerate(unique_terms):
      uterm_counts.append(0)

      for term in terms:
        term == uterm
        uterm_counts[i] = uterm_counts[i] + 1

      qtfs.append(tfidf.calc_tf(uterm_counts[i]))

    # a query is a single document thus the idf is just 1, normalized to the multiplier
    qidfs.extend([1 *tfidf.IDF_MULTIPLIER] * len(unique_terms))

    return qtfs, qidfs

  def get_doc_frequencies(index, posting, queries):
    """ fetch the tfs and idfs of the terms in the index, that match the given queries

    notes:
    - docs could be extracted from the index + queries, but it's kept separate until
      it's decided how bad is it to refetch the docs
    - keep unique_terms extraction in sync with get_query_frequencies,
      until it's decided whether it's better to separate the logics
      or to combine them
    """
    queryDoc = Doc(text=" ".join(queries))
    terms = Doc.fetch_terms(queryDoc)
    unique_terms = set(terms)

    ranks = []
    dtfs = []
    didfs = []

    for uterm in unique_terms:
      occ = index[uterm.text].occurances.has(Node(posting))
      if i >= 0:
        logging.debug(f"[DOCMATCH][TERM:{uterm.text:8}] mentioned [{occ.data.count:2} times] in [DOC:{posting}]")
        dtfs.append(occ.data.tf)
      else:
        dtfs.append(0)

      didfs.append(index[uterm.text].idf)

    return dtfs, didfs

  def query_intersection_core(self, text_list, support_wildcards_kgram=True, support_ranking=False):
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
            # posting_ids = [posting.doc_id for posting in term.occurances]
            # we don't use term.occurances directly for text_docs,
            # as the occurances(Posting type) is not hashable, which should be the case
            text_docs = get_joint(text_docs, term.get_first_n_occurances(0))

      else:
        term = ii.get_corresponding_term(util.normalize(text))
        if term is not None:
          text_docs = term.get_first_n_occurances(0)

      # enable for extensive debugging only
      # logging.debug(f"[{text}] found in the docs: {text_docs}")

      if i == 0:
        out_docs = text_docs
      else:
        out_docs = get_intersection_of_sorted(sorted(out_docs), sorted(text_docs))

      logging.debug(f"[DOC-INTERSECTION]: {out_docs}")

    ranks = []
    if support_ranking:
      qtfs, qidfs = IndexController.get_query_frequencies(text_list)

      logging.debug(f"[SIMILARITY] [QUERY: {text_list}]")
      logging.debug(f"[SIMILARITY]   [QTFS]:  {[round(v) for v in qtfs]}\t" + \
                             f"[QIDFS]: {[round(v) for v in qidfs]}")
      for doc in out_docs:
        dtfs, didfs = IndexController.get_doc_frequencies(self.inv_indexer().index, doc, text_list)
        rank = tfidf.get_query_similarity(qtfs, qidfs, dtfs, didfs)
        ranks.append(rank)

        logging.debug(f"[SIMILARITY]   [DTFS]:  {[round(v) for v in dtfs]}\t" + \
                                     f"[DIDFS]: {[round(v) for v in didfs]}\t" + \
                                     f"[VALUE: {round(rank*100)}%] [DOC: {doc.doc_id}]")

      return out_docs, ranks

    # else
    return out_docs, ranks

  def query_intersection_wildcards(self, text):
    return self.query_intersection(text, True)

  def query_intersection(self, text, wildcard=False, ranked=False):
    """Query the intersection of documents in the indexers
       that the given text appeared at, with wildcard support"""
    if isinstance(text, str):
      text_list = [text]
    elif isinstance(text, list):
      text_list = text
    else:
      raise TypeError("Unexpected query type")

    self.build()

    postings, ranks = self.query_intersection_core(text_list, support_wildcards_kgram=wildcard, support_ranking=ranked)

    doc_index = self.doc_indexer().index

    return [doc_index[posting.doc_id] for posting in postings] , ranks

