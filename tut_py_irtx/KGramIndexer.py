import datetime
import logging

import tut_py_irtx.util as util
from tut_py_irtx.LinkedList import *
from tut_py_irtx.Indexer import *
from tut_py_irtx.Doc import *

class Gram():
  verbose = True
  DEFAULT_VERBOSE_WORD_COUNT = 3

  def __init__(self, text, words=None, hot_load=True):
    """

    Attributes
    ----------
    text : str
      The gram text, for example 'th'
    words : LinkedList
      An ordered linked list of the words this gram appeared in,
      for example ['rather']->['the']->['this']
    buffer : list of str
      Words to be injected into the Gram.words linked list,
      for example ['the', 'the', 'rather', 'this']
    hot_load : bool
      Immediately populate the words into the Gram.words linked list.
      Useful for buffered late-order injection, as it's faster to NOT populate
      the Gram.words linked list until all the gram buffers are created
    """
    self.text = Gram.normalize(text)

    self.words = LinkedList(unique=True, ordered=True)

    self.buffer = words
    self.hot_load = hot_load
    self.populated = False

    if self.hot_load:
      self.populate_from_buffer()

  def populate_from_processed_buffer(self):
    """Populate the Gram.buffer list into Gram.words linkedlist in order

    Buffer processing implies ordering and removing unsorted elements
    from the buffer.

    This function is informed about the words data structure, by using
    the inject tail to avoid further checks on the linked list side,
    making it faster than populate_from_buffer.
    """

    # However, this function is originally not intended to be called
    # after Gram.words linked list got populated as it would call
    # inject_tail for 2 different ordered buffers,
    # which both combind usually resorts to non-orderd elements.
    # The workaround for calling this function twice is to empty
    # the Gram.words linked list then repopulate from the buffer
    if self.populated:
      self.words = LinkedList(unique=True, ordered=True)
      self.populated = False

    for word in sorted(set(self.buffer)):
      self.words.inject_tail(Node(word))

    self.populated = True

  def populate_from_buffer(self):
    """Populate the Gram.buffer list into Gram.words linkedlistr

    This function is generic, does not have any assumptions about
    the buffer whether ordered or not, or the word data structure
    whether it should be ordered or not, and delegates the ordering
    to the word data structure for ordering, in our case this is
    a linked list, making the ordered injection time consuming,
    thus this function would be time-consuming
    """
    for word in self.buffer:
      self.words.add(word)

    self.populated = True

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
      for gram in grams[1:]:
        out = out.get_intersection(gram.words)

      return out

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

