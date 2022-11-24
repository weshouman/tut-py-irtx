import logging

from tut_py_irtx.Indexer import *

class DocIndexer(Indexer):

  def __init__(self, docs=None, docs_hash="", build_time=""):
    super().__init__(docs, docs_hash, build_time)

  def build(self, force=False):
    """a doc dictionary to capture the dictionary given a document index"""
    logging.info("Building Document Index")

    if (force or self.is_index_built == False):
      self.index = {}
      for doc in self.doc_list:
        self.index.setdefault(doc.index, doc)

      self.is_index_built = True

    return self.index

