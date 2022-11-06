import logging
import unittest
import xmlrunner

from tut_py_irtx.inv_index import *
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

    self.assertIsInstance(get_terms(Doc(text="")), list, 'get_terms("") returned non list')
    self.assertIsInstance(get_term_dict([]), dict, 'get_term_dict([]) returned non dict')

    indices = get_term_dict(doc1)
    self.assertIsInstance(indices, dict, "get_term_dict(doc1) returned non dict")

    self.assertEqual(len(indices), doc1_term_count)

    self.assertTrue("hello" in indices, "index hello is not created")
    self.assertListEqual(indices["hello"].occurances, [id1], "index hello is not set correctly")

    indices = get_term_dict([doc1, doc2])

    self.assertTrue("hello" in indices, "index hello is not created")
    self.assertListEqual(indices["hello"].occurances, [id1], "index hello is not set correctly")

    self.assertTrue("test" in indices, "index test is not created")
    # the docs shall get sorted, thus id2 shall preceed id1
    self.assertListEqual(indices["test"].occurances, [id2, id1], "index test is not set correctly")

    self.assertTrue("Hello" not in indices, "index Hello is created")
    self.assertNotEqual(len(indices), 44, "commas and dots are not stripped from the string, thus some terms are stored multiple times")
    self.assertEqual(len(indices), doc1_and_doc2_term_count)

  def test02_correct_index_slicing(self):
    """Slicing the dictionary works fine"""

    n    = 10
    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    indices = get_term_dict([doc1, doc2])

    indices_slice = get_n_indices(indices, n)
    # it should return equal or less, but for this example, we know that the doc has more than n terms
    # thus it's sufficient
    self.assertEqual(len(indices_slice), n, "get_n_indices returned unexpected number of indices")

    # enable for debugging only
    # for i in indices_slice:
    #   print(i.text, i.occurances, i.count)

    indices_slice = get_n_indices(indices, len(indices) + 1)
    self.assertEqual(len(indices_slice), len(indices), "get_n_indices returned more than the original indices count")

  # NOTE: Here we only test the upper limit, we could be more detailed and test also for specific terms if desired
  def test03_correct_occurance_count(self):
    """Occruances are unique"""

    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    indices = get_term_dict([doc1, doc2])

    indices_slice = get_n_indices(indices, len(indices) + 1)
    for i in sorted(indices_slice):
      err = f"the term '{i.text}' got assigned more than the number of given documents, most probably the term showed more than the doc count"
      self.assertLessEqual(i.count, 2, err)

  def tearDown(self):
    """Triggered after each test"""
    logging.debug("tearDown is triggered")

  def test04_query_test(self):
    """query() shall return relevant documents to the given term"""

    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    indices = get_term_dict([doc1, doc2])

    docs = query_docs(indices, "information")
    self.assertLessEqual(len(docs), indices["information"].count, "We should get at max a number of documents equal to the ones that 'information' exists in, as we currently support only simple match queries")

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

