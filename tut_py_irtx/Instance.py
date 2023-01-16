from tut_py_irtx.Term import *
from tut_py_irtx.Posting import *

class Instance():
  """An instance is a representation of the structured form
     that the code retrieves info from alongside with a label or more"""
  def __init__(self, index="0", text="", timestamp="", labels=None):
    self.index = index
    self.text = text
    self.timestamp = timestamp

    self.labels = [] if labels is None else labels

    self.predicted_labels = []

  def __lt__(self, other):
    return self.index < other.index

  def __str__(self):
    out  = self.index
    out += f" \tauthored by {self.author_id}" if self.author_id else ""
    out += f" \tat {self.timestamp}"          if self.timestamp else ""
    return out

  @staticmethod
  def preprocess(text):
    return text.replace("[newline]", " "). \
        replace("[NEWLINE]", " "). \
        replace(",", " "). \
        replace('"', " "). \
        replace("”", " "). \
        replace("“", " "). \
        replace("?", " "). \
        replace("!", " "). \
        encode('ascii', 'ignore').decode('ascii')

  @staticmethod
  def fetch_terms(doc):
    """Get a list of terms given a doc"""
    if not isinstance(doc, Instance):
      raise TypeError("Unsupported Document type")

    text = doc.text

    text = Instance.preprocess(text)

    tokens = text.split()
    terms = [Term(elem, [Posting(doc.index)]) for elem in tokens]
    return terms
