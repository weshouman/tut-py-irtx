import logging

from tut_py_irtx.Indexer import *
from tut_py_irtx.Doc import *
from tut_py_irtx.util import *

class InvertedIndexer(Indexer):
  useTFIDF = True

  def __init__(self, docs=None, docs_hash="", build_time=""):
    super().__init__(docs, docs_hash, build_time)

  def build(self, force=False):
    """Build the inverted indices of the given doc(s) and return it

    Parameter
    ---------
    force : bool
      force rebuilding the index from scratch, terms are fetched from docs
      self.
    """
    logging.info("Building Inverted Index")

    if (force or self.is_index_built == False):
      self.index = {}
      for doc in self.doc_list:
        terms = Doc.fetch_terms(doc)
        self.index = InvertedIndexer.merge_terms(self.index, terms)

        # for each of the updated terms, update its idf
        if (InvertedIndexer.useTFIDF):
          for term in terms:
            self.index[term.text].update_idf(len(self.doc_list))

      self.is_index_built = True

    return self.index

  def get_corresponding_term(self, text):
    """Get corresponding term to the given text form the index

    Parameters
    ----------
    text : str
      Text to look up.

    Returns
    -------
    Term
      The term from the index that corresponds to the given text,
      none if not found.
    """
    term = None
    if text in self.index.keys():
      term = self.index[text]
    return term

  @staticmethod
  def merge_terms(inv_index, term_list):
    """Merge the term_list with the given inv_index and return the updated inv_index"""
    for term in term_list:
      if term.text in inv_index:
        # Doing this check increases the time for a large dataset
        #   ~20 times from 4 to 63 seconds
        #if term.occurances[0] in indices[term.text].occurances:
        index = in_sorted(inv_index[term.text].occurances, term.occurances[0])
        if index >= 0:
          inv_index[term.text].occurances[index].increase_count()
          if (InvertedIndexer.useTFIDF):
            inv_index[term.text].occurances[index].update_tf()
        else:
          last_untouched_occurance = len(inv_index[term.text].occurances)
          inv_index[term.text].occurances.extend(term.occurances)
          occurance_count = len(inv_index[term.text].occurances)
          addition_count = len(term.occurances)
          for occurance in inv_index[term.text].occurances[last_untouched_occurance:occurance_count]:
            occurance.increase_count()

      else:
        inv_index.setdefault(term.text, term)
        inv_index[term.text].occurances[0].increase_count()
      inv_index[term.text].update_count()

    # DO NOT DO THAT: it takes forever for large data
    #for key in indices:
    #  inv_index[key].update_count()

    return inv_index

