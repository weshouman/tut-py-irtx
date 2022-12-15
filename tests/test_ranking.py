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
    logging.debug("setUpModule is triggered")

    # Build the index only once before the different tests
    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    docs = [doc1, doc2]

    cls.ic = IndexController(docs)
    cls.ic.indexers = cls.ic.indexers[0:2] # remove the kgram indexer

    cls.ic.build()

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def test01_calc_rank(self):
    """The term frequency is correctly computed"""

    ic = self.ic

    ii = ic.inv_indexer()
    inv_index = ii.index

    queries = ["information", "retrieval"]
    docs, ranks = ic.query_intersection(queries, ranked=True)

    for i, doc in enumerate(docs):
      print(f"{i:3}: [RANK: {round(ranks[i]*100,2):5.2f}%] [DOC: {doc.index}]")

    self.assertNotEqual(len(docs), 0, f"2 documents should be matching to the queries {queries}")

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

