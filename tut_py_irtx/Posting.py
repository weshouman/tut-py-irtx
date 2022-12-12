import tut_py_irtx.tfidf as tfidf

SORT_BY_DOC_ID = 0
SORT_BY_RANK = 1

class Posting():
  """A posting is the structure that terms point at

  The doc_id is the main item of each posting,
  other info include the term position and
  the tf (term frequency)

  Parameters
  ----------
  sort_algo : int
    Flag for the algoritm to sort the postings by
  """

  sort_algo = SORT_BY_DOC_ID
  def __init__(self, doc_id, position=-1, term_count=-1):
    """

    Parameters
    ----------
    doc_id : str
      The global document id
    position: int
      Position of the term inside the document
      -1 means the position is not set
    term_count: int
      count of occurances of a term in the document
    """
    self.doc_id = doc_id
    self.position = position
    self.sort_algo = SORT_BY_DOC_ID
    self.count = 0
    self.tf = 0

  def __lt__(self, other):
    if Posting.sort_algo == SORT_BY_DOC_ID:
      return self.doc_id < other.doc_id
    else:
      raise NotImplementedError()

  def __eq__(self, other):
    try:
      return self.doc_id == other.doc_id
    except AttributeError:
      return False
    except:
      raise

  def __hash__(self):
    return hash(self.doc_id)

  def __str__(self):
    return f"{self.doc_id:20} \t{self.position:5} \t{self.tf}"

  def increase_count(self):
    self.count = self.count + 1

  def update_tf(self):
    self.tf = tfidf.calc_tf(self.count)
