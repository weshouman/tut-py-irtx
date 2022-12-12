from tut_py_irtx.util import *
from tut_py_irtx.Doc import *

class Indexer():

  def __init__(self, docs=None, docs_hash="", build_time=""):
    """Base class for the different indexers
    Attributes
    ----------
    doc_list : list of Doc
      List of documents to be indexed
    index : dict
      The index
    is_index_built : True
      Set upon index creation
    doc_hash : str
      Hash of the indexed documents, to be used to check if the
      the doc_list is updated
    build_time : str
      Time spent building the index
    """
    self.set_docs(docs)
    self.index = {}
    self.is_index_built = False
    self.doc_hash = docs_hash
    self.build_time = build_time

  def set_docs(self, docs):
    # we should make the postings a linked list to avoid the need of sorting docs beforehand
    # Performance needs to be measured though
    if isinstance(docs, Doc):
      self.doc_list = [docs]
    elif isinstance(docs, list):
      if len(docs) > 0 and not isinstance(docs[0], Doc):
        raise TypeError(f"Unsupported Document, given type is [{type(Doc)}]")
      else:
        self.doc_list = sorted(docs)
    elif docs is None:
      # NOTE: This occurs when the IndexController is initialzing the indexer
      #       We may decide to use a single doc_list source if possible
      self.doc_list = []
    else:
      raise TypeError(f"Unsupported Document, given type is {type(docs)}")

    self.invalidate()

  def get_index(self):
    if not self.is_index_built:
      self.build()
    return self.index

  def set_index(self, index):
    self.index = index

  def get_slice(self, size=10):
    return slice_list_of_dict(self.index, size)

  def build(self, data={}, force=False):
    """a doc dictionary to capture the dictionary given a document index"""
    raise(NotImplementedError())

  def invalidate(self):
    self.is_index_built = False
