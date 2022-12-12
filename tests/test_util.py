import logging
import unittest
import xmlrunner

import tut_py_irtx.util as util

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class UtilTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def test01_insorted(self):
    """Hit while checking insorted"""

    a = [1, 2, 128]
    index = util.in_sorted(a, 1)
    self.assertEqual(index, 0)
    index = util.in_sorted(a, 2)
    self.assertEqual(index, 1)
    index = util.in_sorted(a, 128)
    self.assertEqual(index, 2)

  def test02_not_insorted(self):
    """Missed while checking insorted"""

    small = 2
    mid   = 10
    large = 128

    a = [small, mid, large]
    index = util.in_sorted(a, small-1)
    self.assertEqual(index, -2, "in_sorted shall return without checking all items")
    index = util.in_sorted(a, mid+1)
    self.assertEqual(index, -2, "in_sorted shall return without checking all items")
    index = util.in_sorted(a, large+1)
    self.assertEqual(index, -1, "in_sorted shall return after checking all items")


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

