from tut_py_irtx.util import *

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
    self.doc_list = docs
    self.index = {}
    self.is_index_built = False
    self.doc_hash = docs_hash
    self.build_time = build_time

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
