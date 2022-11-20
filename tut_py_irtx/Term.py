import tut_py_irtx.util as util

class Term():
  """A term contains a text, the occurances list and the occurances count"""
  def __init__(self, text, occurances=None):
    self.text = Term.normalize(text)

    if occurances == None:
      self.occurances = []
    else:
      self.occurances = occurances

  verbose = False
  DEFAULT_VERBOSE_OCCURANCE_COUNT = 3

  @classmethod
  def normalize(cls, text):
    return util.normalize(text)

  def update_count(self):
    self.count = len(self.occurances)

  def get_first_n_occurances(self, n=DEFAULT_VERBOSE_OCCURANCE_COUNT):
    return self.occurances[:n]

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

