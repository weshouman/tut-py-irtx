import logging
import unittest
import xmlrunner

import tut_py_irtx.tfidf as tfidf
from tut_py_irtx.IndexController import *
from tut_py_irtx.Doc import *
from tests.stub_inv_index import *

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class RankingTest(unittest.TestCase):
  ic = None

  log = logging.getLogger( "RankingTest" )

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    cls.log.debug("setUpModule is triggered")

    from essential_generators import DocumentGenerator
    docs = []
    gen = DocumentGenerator()
    gen.init_word_cache(5000)
    gen.init_sentence_cache(5000)

    for i in range(500):
      gen_doc = gen.paragraph()
      doc = Doc(text=gen_doc, index=i)
      docs.append(doc)

    cls.ic = IndexController(docs)
    cls.ic.indexers = cls.ic.indexers[0:2] # remove the kgram indexer

    cls.ic.build()

  def setUp(self):
    """Triggered before each test"""
    self.log.debug("setUp is triggered")

  @staticmethod
  def print_ranked_docs(docs, query=None, page=10):
    query_cache = query if query is not None else []

    count = 0

    print(f"Found {len(docs)} matches for {query_cache}")
    for i, doc in enumerate(docs, 1):
      if (count < page):
        print(f"result {i:3}: [RANK: {round(doc.rank*100,2):5.2f}%] [DOC: {doc.index}]")
        if doc.rank > 0.85:
          print(doc.text + "\n")
        count = count+1

  def test01_calc_rank(self):
    """The term frequency is correctly computed"""
    ic = self.ic

    queries = ["great", "is"]
    docs = ic.query_intersection(queries, ranked=True)

    RankingTest.print_ranked_docs(docs, queries)

    self.assertNotEqual(len(docs), 0, f"some documents should be matching the queries {queries}")

  def test02_calc_rank_compact(self):
    # Build the index only once before the different tests
    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    docs = [doc1, doc2]

    ic = IndexController(docs)
    ic.indexers = ic.indexers[0:2] # remove the kgram indexer

    ic.build()

    queries = ["information", "retrieval"]
    docs = ic.query_intersection(queries, ranked=True)

    RankingTest.print_ranked_docs(docs, queries)

    self.assertNotEqual(len(docs), 0, f"some documents should be matching the queries {queries}")

  def tearDown(self):
    """Triggered after each test"""
    logging.debug("tearDown is triggered")

  @classmethod
  def tearDownClass(cls):
    """Triggered  after all class tests"""
    logging.debug("tearDownClass is triggered")


# if __name__ == '__main__':
#     unittest.main(
#         testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
#         # these make sure that some options that are not applicable
#         # remain hidden from the help menu.
#         failfast=False, buffer=False, catchbreak=False)

