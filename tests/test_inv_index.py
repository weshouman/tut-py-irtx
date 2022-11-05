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

  def test01_doc1(self):
    print("get_indices output...")
    self.assertIsInstance(get_terms(""), list, 'get_terms("") returned non list')
    self.assertIsInstance(get_indices([]), dict, 'get_indices([]) returned non dict')
    self.assertIsInstance(get_indices([],[]), dict, 'get_indices([],[]) returned non dict')

    indices = get_indices(get_term_lists([doc1]))
    self.assertIsInstance(indices, dict, "get_indices(doc1) returned non dict")
    print(indices)

    self.assertEqual(len(indices), doc1_term_count)

    self.assertTrue("hello" in indices, "index hello is not created")
    self.assertListEqual(indices["hello"], [0], "index hello is not set correctly")

    indices = get_indices(get_term_lists([doc1, doc2]))

    self.assertTrue("hello" in indices, "index hello is not created")
    self.assertListEqual(indices["hello"], [0], "index hello is not set correctly")

    self.assertTrue("test" in indices, "index test is not created")
    self.assertListEqual(indices["test"], [0,1], "index test is not set correctly")

    self.assertTrue("Hello" not in indices, "index Hello is created")
    self.assertEqual(len(indices), doc1_and_doc2_term_count)

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

