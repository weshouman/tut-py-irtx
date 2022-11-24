import logging

import tut_py_irtx.util as util
from tut_py_irtx.LinkedList import *
from tut_py_irtx.Indexer import *
from tut_py_irtx.Doc import *

class Gram():
  def __init__(self, text, words=None):
    self.text = Gram.normalize(text)

    self.words = LinkedList()
    if words != None:
      self.words.extend_from_list(words)

  verbose = True
  DEFAULT_VERBOSE_WORD_COUNT = 3

  @classmethod
  def normalize(cls, text):
    return util.normalize(text)

  def update_count(self):
    self.count = self.words.get_count()

  def get_first_n_words(self, n=DEFAULT_VERBOSE_WORD_COUNT):
    return self.words.get_slice_as_ll(n)

  def __lt__(self, other):
    return self.text < other.text

  @staticmethod
  def fetch_wildcard_grams(text, k=2):
    """Return a list of gram texts extracted from
       the given wildcard string.
       k=2 is a bigram, k=3 is a trigram ..."""

    grams = []
    if (text.startswith("*") == False):
      grams.append(Gram(f"${text[0:k-1]}", [text]))

    for i, char in enumerate(text):
      if len(text) + 1 <= i+k:
        # last item
        chars = text[i:]
        if ("*" not in chars):
          grams.append(Gram(f"{''.join(chars)}$", [text]))
      else:
        chars = text[i:i+k]
        if ("*" not in chars):
          grams.append(Gram("".join(chars), [text]))

    return grams

  @classmethod
  def get_header(cls):
    text  = "[Gram text]"
    count = "[Count in words]"
    words = f"[first {cls.DEFAULT_VERBOSE_WORD_COUNT} words]"
    if Gram.verbose:
      out =  f"\n{text:20} \t{count:>15} \t{words}"
      out += f"\n{len(out)*'-'}--------"
    else:
      out =  f"\n{text:20} \t{count:15}"
      out += f"\n{len(out)*'-'}-"

    return out

  def __str__(self):
    if Gram.verbose:
      out = f"{self.text:20} \t{len(self.words):15} \t{self.get_first_n_words()}"
    else:
      out = f"{self.text:20} \t{len(self.words):15}"
    return out

  @staticmethod
  def get_intersection(grams):
    if len(grams) == 0:
      return LinkedList()
    elif len(grams) == 1:
      return grams[0].words
    else:
      out = grams[0].words.get_intersection(grams[1].words)
      for i, gram in enumerate(grams[1:]):
        out = out.get_intersection(gram.words)

      return out

class KGramIndexer(Indexer):
  def __init__(self, docs=None, k=2, docs_hash="", build_time=""):
    self.k = 2
    super().__init__(docs, docs_hash, build_time)

  def build(self, force=False):
    """Build the KGram indices of the given doc(s) and return it"""
    logging.info("Building KGram Index")

    if (force or self.is_index_built == False):
      self.index = {}
      for doc in self.doc_list:
        for term in Doc.fetch_terms(doc):
          self.index = self.merge_grams(self.index, KGramIndexer.fetch_grams(term.text, self.k))

      self.is_index_built = True

    return self.index

  def index_string(self, size=-1):
    size = size if size > 0 else len(self.index) + 1

    index_slice = self.get_slice(size)
    out = f"{Gram.get_header()}\n"
    for i in sorted(index_slice):
      out += f"{i}\n"
    return out

  @staticmethod
  def fetch_grams(term, k=2):
    grams = []
    grams.append(Gram(f"${term[0:k-1]}", [term]))
    for i, char in enumerate(term):
      if len(term) + 1 <= i+k:
        # last item
        chars = term[i:]
        grams.append(Gram(f"{''.join(chars)}$", [term]))
      else:
        chars = term[i:i+k]
        grams.append(Gram("".join(chars), [term]))

    return grams

  @staticmethod
  def merge_grams(index, grams):
    """Merge the term_list with the given index and return the updated index"""
    for gram in grams:
      if gram.text in index:
        # Doing this check increases the time for a large dataset
        #   ~20 times from 4 to 63 seconds
        #if gram.words[0] in indices[gram.text].words:
        if index[gram.text].words.has(gram.words.head.data):
          pass
        else:
          logging.debug(f"[{gram.text}]: {gram.words.head.data}")
          logging.debug(f"before: {index[gram.text].words}")
          index[gram.text].words.inject_ordered(Node(gram.words.head.data), unique=True)
          logging.debug(f"after:  {index[gram.text].words}")
      else:
        index.setdefault(gram.text, gram)
      index[gram.text].update_count()

    # DO NOT DO THAT: it takes forever for large data
    #for key in indices:
    #  index[key].update_count()

    return index

  @staticmethod
  def wildcard_to_terms(wildcard, kgram_index):
    """convert the wildcard into terms that match the wildcard, following the kgram_index"""
    terms = []
    grams_buffer = []
    for gram in Gram.fetch_wildcard_grams(wildcard):
      if gram.text in kgram_index.keys():
        grams_buffer.append(kgram_index[gram.text])
      else:
        # stop fast, as at least one gram is not in our index
        return []

    # intersect the grams into terms to be searched for
    ll = Gram.get_intersection(grams_buffer)
    terms.extend(ll.get_slice(-1))
    return terms

