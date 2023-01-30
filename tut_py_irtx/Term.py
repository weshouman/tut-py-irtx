import tut_py_irtx.util as util
import tut_py_irtx.tfidf as tfidf
from tut_py_irtx.LinkedList import *

class Term():
  """A term contains a text, the occurances list and the occurances count"""

  def __init__(self, text, occurances=None, hot_load=True):
    self.text = Term.normalize(text)

    self.buffer = [] if occurances is None else occurances
    self.hot_load = hot_load
    self.populated = False

    self.occurances = LinkedList(unique=True, ordered=True)

    if self.hot_load:
      self.populate_from_buffer()

    self.idf = 0

    # Used for Clustering, as each term should represent a dimension
    # known by this order
    self.order = 0

  verbose = False
  DEFAULT_VERBOSE_OCCURANCE_COUNT = 3

  def populate_from_buffer(self):
    """Follow populte_from_buffer for Gram.py"""
    for occ in self.buffer:
      self.occurances.add(occ)

    self.populated = True

  @classmethod
  def normalize(cls, text):
    return util.normalize(text)

  def update_count(self):
    self.count = self.occurances.count

  def update_idf(self, total_docs):
    self.idf = tfidf.calc_idf(self.count, total_docs)

  def get_first_n_occurances(self, n=DEFAULT_VERBOSE_OCCURANCE_COUNT):
    return self.occurances.get_slice(n)

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

