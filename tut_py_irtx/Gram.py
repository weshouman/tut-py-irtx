import tut_py_irtx.util as util
from tut_py_irtx.LinkedList import *

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


