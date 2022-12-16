import logging

from tut_py_irtx.Indexer import *
from tut_py_irtx.Doc import *
from tut_py_irtx.util import *

class InvertedIndexerStats():
  def __init__(self, index=None):
    """
    frequencies is a dictionary of the
    max_frequency is the max number of docs referenced for a single term
    term_count count of terms
    """
    self.frequencies = {}
    self.max_frequency = 0
    self.term_count = 0
    self.index = index

    if self.index is not None:
      self.calculate()

  def calculate(self):
    """Get stats about the index
    Currently only the count of terms that are found in a specific number of docs are saved
    to show how frequent each length of the posting list is
    """
    if self.index is None:
      logging.error("Could not calculate Inverted Indexer statistics: index not set")
      return

    keys = self.index.keys()
    for key in keys:
      doc_count = self.index[key].count
      # initialize to zero if key not found
      self.frequencies.setdefault(doc_count, 0)
      # record match
      self.frequencies[doc_count] = self.frequencies[doc_count] + 1

      self.max_frequency = doc_count if self.max_frequency < doc_count else self.max_frequency

    self.term_count = len(keys)

class InvertedIndexer(Indexer):
  useTFIDF = True
  MAX_OCCURANCES = 3 # max occurances to display

  def __init__(self, docs=None, docs_hash="", build_time=""):
    super().__init__(docs, docs_hash, build_time)
    self.is_stats_calced = False
    self.stats = InvertedIndexerStats()

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
            # Use the following for debugging the change of a term idf/tf, during indexing
            #if term.text == "the":
            #  print(InvertedIndexer.visualization_header() + \
            #        self.visualize_term(term.text))
            self.index[term.text].update_idf(len(self.doc_list))

      self.is_index_built = True

    return self.index

  def __str__(self):
    return self.visualize_index(0)

  def visualize_index(self, slice_size=10):
    """
    Parameter
    ---------
    slice_size : int
      0 to get the whole index
    """

    if slice_size > 0:
      index_slice = slice_list_of_dict(self.index, slice_size)
    else:
      index_slice = self.index

    out = InvertedIndexer.visualization_header()
    for key in self.index.keys():
      out += self.visualize_term(key)

    return out

  @staticmethod
  def visualization_header():
    header = f"[{'TERM':13} - DOC_COUNT - IDF] -> [DOC - TERM_COUNT - TF]\n"
    header += f"------------------------------------------------------------\n"
    return header

  def visualize_term(self, term_text):
    tfs = [ f"{occ.doc_id} - {occ.count} - {round(occ.tf):5}" for occ in self.index[term_text].occurances[0:self.MAX_OCCURANCES]]
    # visualize more than 3 elements
    tfs_str = f"{tfs}" if self.index[term_text].count <= self.MAX_OCCURANCES else f"{str(tfs)[:-1]},...]"
    return f"[{term_text:18}- {self.index[term_text].count:4} -{round(self.index[term_text].idf):5}] -> {tfs_str}\n"


  def get_stats(self):
    if self.is_stats_calced == False:
      self.stats.index = self.index
      self.stats.calculate()
      self.is_stats_calced = True

    return self.stats

  def visualize_stats(self, display_sparse=False):
    stats = self.get_stats()

    if (display_sparse):
      # set all others to zero
      for i in range(stats.max_frequency):
        stats.setdefault(i, 0)

    # turn into chart
    out = ""
    freqs = stats.frequencies
    for key in sorted(freqs.keys()):
      count = freqs[key]
      percent = round((count * 100)/stats.term_count, 2)
      if count > 30:
        out += f"{count:5} ({percent:5.2f}%) terms in {key:4} docs|{30*'.'}|\n"
      else:
        out += f"{count:5} ({percent:5.2f}%) terms in {key:4} docs|{(count) * '.'}\n"
    return out

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
  def merge_terms(inv_index, term_list, update_tfs=True):
    """Merge the term_list with the given inv_index and return the updated inv_index"""

    log = logging.getLogger( "InvertedIndexer.merge_terms" )
    # when debugging is enabled, one could trace whether
    # the added term's posting was considered a new or an old posting (amendment)
    # for example, if addition was not in order, the in_sorted would return a wrong decision
    # thus new postings would be added, when they should be only amended
    #logging.getLogger( "InvertedIndexer.merge_terms" ).setLevel( logging.INFO )

    new_term_count = 0
    inc_term_count = 0
    new_posting_count = 0
    for term in term_list:
      newterm = not term.text in inv_index

      if newterm:
        log.debug(f"[MERGE][TERM: {term.text:10}][NEW_TERM]")
        new_term_count += 1
        inv_index.setdefault(term.text, term)

        for occurance in inv_index[term.text].occurances:
          occurance.increase_count()
          if (InvertedIndexer.useTFIDF and update_tfs):
            occurance.update_tf()

      else:
        # posting_count_pre = len(inv_index[term.text].occurances)
        # Doing this check increases the time for a large dataset
        #   ~20 times from 4 to 63 seconds
        #if term.occurances[0] in indices[term.text].occurances:
        for occurance in term.occurances:

          index = in_sorted(inv_index[term.text].occurances, occurance)

          posting_index = -1
          if index >= 0:
            log.debug(f"[MERGE][TERM: {term.text:10}][AMEND POSTING: {occurance.doc_id}]")
            inc_term_count += 1
            posting_index = index
          else:
            log.debug(f"[MERGE][TERM: {term.text:10}][NEW   POSTING: {occurance.doc_id}]")
            new_posting_count += 1
            inv_index[term.text].occurances.append(occurance)
            posting_index = len(inv_index[term.text].occurances)-1

          inv_index[term.text].occurances[posting_index].increase_count()
          if (InvertedIndexer.useTFIDF and update_tfs):
            inv_index[term.text].occurances[index].update_tf()


      inv_index[term.text].update_count()

    log.info(f"[MERGE] [STATS] [NEW_TERMS {new_term_count}][NEW_POSTINGS {new_posting_count}][INC_TERM {inc_term_count}]")

    # DO NOT DO THAT: it takes forever for large data
    #for key in indices:
    #  inv_index[key].update_count()

    return inv_index

