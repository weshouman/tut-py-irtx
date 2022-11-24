from tut_py_irtx.Term import *

class Doc():
  """A document is a representation of the structured form
     that the code retrieves info from"""
  def __init__(self, index="0", author_id="", text="", timestamp=""):
    self.index = index
    self.author_id = author_id
    self.text = text
    self.timestamp = timestamp

  def __lt__(self, other):
    return self.index < other.index

  def __str__(self):
    out = self.index

    if self.author_id:
      out += f" \tauthored by {self.author_id}"

    if self.timestamp:
      out += f" \tat {self.timestamp}"

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
    if not isinstance(doc, Doc):
      raise TypeError("Unsupported Document type")

    text = doc.text

    text = Doc.preprocess(text)

    tokens = text.split()
    terms = [Term(elem, [doc.index]) for elem in set(tokens)]
    return terms

