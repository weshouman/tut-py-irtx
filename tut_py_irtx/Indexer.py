from tut_py_irtx.util import *

class Indexer():

  def __init__(self, docs=None, docs_hash="", build_time=""):
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
