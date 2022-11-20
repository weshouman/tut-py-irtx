import logging
import unittest
import xmlrunner

from tut_py_irtx.IndexController import *
from tut_py_irtx.InvertedIndexer import *
from tut_py_irtx.DocIndexer import *
from tut_py_irtx.KGramIndexer import *
from tut_py_irtx.Doc import *
from tests.stub_inv_index import *

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class InvIndexTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def test01_inverted_index_generation(self):
    """The inverted index is correctly generated"""

    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    ic   = IndexController(Doc(text=""))

    self.assertIsInstance(Doc.fetch_terms(Doc("")), list, 'fetch_terms("") returned non list')

    ii   = InvertedIndexer([])
    ii.build()
    self.assertIsInstance(ii.build(force=True), dict, 'ii.build([]) returned non dict')

    ii.doc_list = [doc1]
    inv_index = ii.build(force=True)
    self.assertIsInstance(inv_index, dict, "ii.build returned non dict")

    self.assertEqual(len(inv_index), doc1_term_count)

    self.assertTrue("hello" in inv_index, "index hello is not created")
    self.assertListEqual(inv_index["hello"].occurances, [id1], "index hello is not set correctly")

    ii.doc_list = [doc1, doc2]
    inv_index = ii.build(force=True)

    self.assertTrue("hello" in inv_index, "index hello is not created")
    self.assertListEqual(inv_index["hello"].occurances, [id1], "index hello is not set correctly")

    self.assertTrue("test" in inv_index, "index test is not created")
    # the docs shall get sorted, thus id2 shall preceed id1
    self.assertListEqual(inv_index["test"].occurances, [id1, id2], "index test is not set correctly")

    self.assertTrue("Hello" not in inv_index, "index Hello is created")
    self.assertNotEqual(len(inv_index), 44, "commas and dots are not stripped from the string, thus some terms are stored multiple times")
    self.assertEqual(len(inv_index), doc1_and_doc2_term_count)

  def test02_correct_index_slicing(self):
    """Slicing the dictionary works fine"""

    n    = 10
    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    ii   = InvertedIndexer([doc1, doc2])

    inv_index = ii.build()

    indices_slice = ii.get_slice(n)
    # it should return equal or less, but for this example, we know that the doc has more than n terms
    # thus it's sufficient
    self.assertEqual(len(indices_slice), n, "get_inv_index_slice returned unexpected number of inv_index")

    # enable for debugging only
    # for i in indices_slice:
    #   print(i.text, i.occurances, i.count)

    indices_slice = ii.get_slice(len(inv_index) + 1)
    self.assertEqual(len(indices_slice), len(inv_index), "get_inv_index_slice returned more than the original inv_index count")
    logging.debug(Term.get_header())
    for i in sorted(indices_slice):
      logging.debug(i)


  # NOTE: Here we only test the upper limit, we could be more detailed and test also for specific terms if desired
  def test03_correct_occurance_count(self):
    """Occruances are unique"""

    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    ii   = InvertedIndexer([doc1, doc2])

    inv_index = ii.build()

    indices_slice = ii.get_slice(len(inv_index) + 1)
    for i in sorted(indices_slice):
      err = f"the term '{i.text}' got assigned more than the number of given documents, most probably the term showed more than the doc count"
      self.assertLessEqual(i.count, 2, err)

  @unittest.skip("WIP")
  def test04_query_test(self):
    """query() shall return relevant documents to the given term"""

    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    ic   = IndexController([doc1, doc2])

    ic.build()
    inv_index = ic.get_inv_index()

    sample = "information"
    docs = ic.query_intersection(sample)
    self.assertEqual(len(docs), inv_index[sample].count, "Simple query is not working: 'information' exists in both the documents")

    samples = ["infromation", "test"]
    docs = ic.query_intersection(samples)
    self.assertEqual(len(docs), 2, "Query intersection is not working: 'information' and 'test' is found in both the documents, we should get both the docs")

    logging.debug("\n")
    logging.debug(f"{samples} were found in the following docs\n---")
    logging.debug("---\n".join([ doc.index + ": " + doc.text for doc in docs]))
    logging.debug("---")

  @unittest.skip("WIP")
  def test05_regex_docs(self):
    doc1 = Doc(text=stub_doc1, index=stub_doc1_id)
    doc2 = Doc(text=stub_doc2, index=stub_doc2_id)

    ic   = IndexController([doc1, doc2])

    inv_index = ic.build()

    matches = ic._regex_docs("a.*")
    self.assertEqual(len(matches), 2, "regex_docs('a.*') should match both the docs")
    logging.debug([m.index for m in matches])

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

