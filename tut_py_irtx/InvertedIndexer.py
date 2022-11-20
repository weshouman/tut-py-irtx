import logging

from tut_py_irtx.Indexer import *
from tut_py_irtx.Doc import *
from tut_py_irtx.util import *

class InvertedIndexer(Indexer):
  def __init__(self, docs=None, docs_hash="", build_time=""):
    super().__init__(docs, docs_hash, build_time)

  def build(self, force=False):
    """Build the inverted indices of the given doc(s) and return it"""
    if (force or self.is_index_built == False):
      self.index = {}
      for doc in self.doc_list:
        self.index = InvertedIndexer.merge_terms(self.index, Doc.fetch_terms(doc))

      self.is_index_built = True

    return self.index

  @staticmethod
  def merge_terms(inv_index, term_list):
    """Merge the term_list with the given inv_index and return the updated inv_index"""
    for term in term_list:
      if term.text in inv_index:
        # Doing this check increases the time for a large dataset
        #   ~20 times from 4 to 63 seconds
        #if term.occurances[0] in indices[term.text].occurances:
        if in_sorted(inv_index[term.text].occurances, term.occurances[0]):
          pass
        else:
          inv_index[term.text].occurances.extend(term.occurances)
      else:
        inv_index.setdefault(term.text, term)
      inv_index[term.text].update_count()

    # DO NOT DO THAT: it takes forever for large data
    #for key in indices:
    #  inv_index[key].update_count()

    return inv_index

