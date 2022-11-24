import datetime
import logging

from tut_py_irtx.Indexer import *
from tut_py_irtx.Doc import *
from tut_py_irtx.Gram import *

class KGramIndexer(Indexer):
  def __init__(self, docs=None, k=2, late_sort=True, docs_hash="", build_time=""):
    """KGram Indexer

    Attributes
    ----------
    k : int
      Gram size, by default it's a bigram
    late_sort : bool
      Use late sorting strategy for building the index,
      setting it to True prevents from repeated ordered injections for the
      same Gram.words linked list, until a buffer list is compiled for all
      the index grams
    """
    self.k = 2
    self.late_sort = late_sort
    super().__init__(docs, docs_hash, build_time)

  @staticmethod
  def is_term_ignored(text):
    """return true if a text is not kgram indexed"""
    return text.startswith("https:")

  def build(self, force=False):
    """Build the KGram index of the given doc(s) and return it"""
    logging.info("Building KGram Index")

    if (force or self.is_index_built == False):
      self.index = {}

      date_old = datetime.datetime.now()
      doc_count = len(self.doc_list)

      for i, doc in enumerate(self.doc_list):

        # Info purposes
        if i > 0 and \
           ((not self.late_sort and i % 100  == 0) or \
            (    self.late_sort and i % 1000 == 0)):
          date_new = datetime.datetime.now()
          logging.info(f"[GRAM-MERGING] [FINISHED: {i:5}/{doc_count}] [AT: {doc.index}] [{(date_new-date_old).seconds} SECONDS] [{len(self.index.keys())} GRAMS] [{self.index_words_count()} WORDS]")
          date_old = date_new
          if i == 100:
            logging.debug(Gram.get_header())
            for s in self.get_slice(-1):
              logging.debug(s)
        # End of info purposes

        for term in Doc.fetch_terms(doc):
          if KGramIndexer.is_term_ignored(term.text):
            continue
          if self.late_sort:
            self.index = self.merge_grams_buffer_unordered(self.index, KGramIndexer.fetch_grams_raw(term.text, self.k), word=term.text)
          else:
            self.index = self.merge_grams_ordered(self.index, KGramIndexer.fetch_grams(term.text, self.k))

      if self.late_sort:

        date_old = datetime.datetime.now()
        gram_count = len(self.index.keys())

        for i, key in enumerate(self.index.keys()):

          # Info purposes
          if i % 100 == 0:
            date_new = datetime.datetime.now()
            logging.info(f"[GRAM-SORTING] [SORTED {i}/{gram_count} GRAMS] [AT: {self.index[key].text} {len(self.index[key].buffer)}][{(date_new-date_old).seconds} SECONDS] [{self.index_words_count()} WORDS]")
            date_old = date_new
          # End of info purposes

          self.index[key].populate_from_processed_buffer()

        logging.info(f"[POST-GRAM-SORTING] [{len(self.index.keys())} GRAMS] [{self.index_words_count()} WORDS]")

      self.is_index_built = True

    return self.index

  def index_string(self, size=-1):
    size = size if size > 0 else len(self.index) + 1

    index_slice = self.get_slice(size)
    out = f"{Gram.get_header()}\n"
    for i in sorted(index_slice):
      out += f"{i}\n"
    return out

  def index_words_count(self):
    """return count of words the index keys point to"""
    counts = [self.index[key].words.get_count() for key in self.index.keys()]
    return sum(counts)

  @staticmethod
  def fetch_grams(term, k=2):
    grams = []
    for gram in KGramIndexer.fetch_grams_raw(term=term, k=k):
      grams.append(Gram(gram, [term]))
    return grams

  @staticmethod
  def fetch_grams_raw(term, k=2):
    grams = []
    grams.append(f"${term[0:k-1]}")
    for i, char in enumerate(term):
      if len(term) + 1 <= i+k:
        # last item
        chars = term[i:]
        grams.append(f"{''.join(chars)}$")
      else:
        chars = term[i:i+k]
        grams.append("".join(chars))

    return grams

  @staticmethod
  def merge_grams_ordered(index, grams):
    """Merge the grams into the given index in order

    Merging implies adding a new gram if not found,
    or appending the word into the found gram's buffer list.

    Ordered injection into the linkedlist of each gram
    of the index dict takes a lot of time,
    however that's space efficient compared to using
    a buffer for the linkedlist then ordering that buffer afterwords

    This function does not allow repeated injection of the same word.

    Parameters
    ----------
    index : dict
      the index to merge into
    grams : list of Gram
      the list of the grams to merge into the index

    Returns
    -------
    dict
      the updated index
    """
    #logging.debug(f"[MERGING-GRAMS] [WORD: {grams[0].words.head.data}]")
    for gram in grams:
      if gram.text in index.keys():
        # d1 = datetime.datetime.now()
        # logging.debug(f"[MERGING-GRAMS][WORD: {gram.words.head.data}][GRAM: {gram.text}]")
        # logging.debug(f"[MERGING-GRAMS][INDEX][PRE] [{index[gram.text].words}]")

        index[gram.text].words.inject_ordered(Node(gram.words.head.data), unique=True)
        # logging.debug(f"[MERGING-GRAMS][INDEX][POST][{index[gram.text}]")
        # d2 = datetime.datetime.now()
        # logging.debug(f"[MERGING-GRAMS][TIME: {(d2-d1).seconds} seconds]")

      else:
        index.setdefault(gram.text, gram)

    return index

  @staticmethod
  def merge_grams_buffer_unordered(index, grams, word):
    """Merge the grams into the given index

    Merging implies adding a new gram if not found,
    or appending the word into the found gram's buffer list.

    Unordered injection into the linkedlist of each gram
    of the index dict takes uses a buffer, thus taking more space,
    however that's time efficient compared to ordered injection
    into the linkedlist.

    This function allows repeated injection of the same word.

    Parameters
    ----------
    index : dict
      the index to merge into
    grams : list of str
      the list of the gram text to merge into the index
    word : str
      the word that the grams appeared in

    Returns
    -------
    dict
      the updated index
    """
    #logging.debug(f"[MERGING-GRAMS] [WORD: {word}]")
    for gram in grams:
      if gram in index.keys():
        # d1 = datetime.datetime.now()
        # logging.debug(f"[MERGING-GRAMS][WORD: {word}][GRAM: {gram}]")
        # logging.debug(f"[MERGING-GRAMS][INDEX][PRE] [{index[gram}]")
        index[gram].buffer.append(word)
        # logging.debug(f"[MERGING-GRAMS][INDEX][POST][{index[gram}]")

        # d2 = datetime.datetime.now()
        # logging.debug(f"[MERGING-GRAMS][TIME: {(d2-d1).seconds} seconds]")
      else:
        index.setdefault(gram, Gram(gram, [word], hot_load=False))

    return index

  @staticmethod
  def expand_wildcard_to_list(wildcard, kgram_index):
    """Captures text list that matches a wildcard based on a kgram_index
    Parameters
    ----------
    wildcard: str
      text to expand, for example 'ha*'
    kgram_index: dict
      index to look up the kgrams
    Returns
    -------
    list of str:
      A list of expanded text, for example ['have', 'had', ...].
      Expanded words are based on the words stored in the kgram_index
    """
    terms = []
    grams_buffer = []
    for gram in Gram.fetch_wildcard_grams(wildcard):
      if gram.text in kgram_index.keys():
        grams_buffer.append(kgram_index[gram.text])
      else:
        # stop fast, as at least one gram is not in our index
        logging.info(f"[{wildcard}] expanded to []")
        return []

    # intersect the grams into terms to be searched for
    ll = Gram.get_intersection(grams_buffer)
    terms.extend(ll.get_slice(-1))
    logging.info(f"[{wildcard}] expanded to {terms}")
    return terms

