import logging
import unittest
import xmlrunner

from tut_py_irtx.LinkedList import *

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class LinkedListTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def test01_generic(self):
    """Generic linkedlist tests"""
    ll = LinkedList()
    ll.append("abc")
    ll.append("def")

    self.assertEqual(len(ll), 2)
    self.assertEqual(ll.get_count(), 2, "LinkedList.get_count() shall report 2")
    self.assertEqual(ll.get_slice(), ["abc", "def"], "LinkedList.get_slice(5) shall bring by max the 2 elements")
    self.assertEqual(ll.has(Node("abc")), True, "LinkedList.has(node) shall report having the node")
    ll.inject_ordered(Node("bcd"))
    self.assertEqual(ll.get_count(), 3, "LinkedList.get_count() shall report 3")
    ll.inject_ordered(Node("abc"), unique=True)
    self.assertEqual(ll.get_count(), 3, "LinkedList.get_count() shall report 3, if 4 is reported, than a duplicate got inserted")
    self.assertEqual(str(ll), "[abc]->[bcd]->[def]", "LinkedList.__str__() does not print correctly")
    self.assertEqual(len(ll), 3)


  def test02_unique_insertion(self):
    """Unique linkedlist tests"""
    ll = LinkedList()
    ll.append("a")
    ll.append("b")
    ll.append("b")
    self.assertEqual(str(ll), "[a]->[b]->[b]")
    ll.inject_ordered(Node("b"), unique=True)
    self.assertEqual(str(ll), "[a]->[b]->[b]", "uniqueness shall be overwriteable at inject_ordered")
    ll.inject_ordered(Node("b"))
    self.assertEqual(str(ll), "[a]->[b]->[b]->[b]", "default unique flag is checked")

  def test03_ordered_insertion(self):
    """Ordered linkedlist tests"""
    ll = LinkedList(unique=True, ordered=True)
    ll.add("ant")
    ll.add("zebra")
    ll.add("must")
    self.assertEqual(str(ll), "[ant]->[must]->[zebra]")
    ll.inject_ordered(Node("neon"), unique=True)
    self.assertEqual(str(ll), "[ant]->[must]->[neon]->[zebra]")
    ll.inject_ordered(Node("acre"), unique=False)
    self.assertEqual(str(ll), "[acre]->[ant]->[must]->[neon]->[zebra]")
    ll.inject_ordered(Node("zoo"), unique=False)
    self.assertEqual(str(ll), "[acre]->[ant]->[must]->[neon]->[zebra]->[zoo]")

  def test04_get_first_n(self):
    """Ordered linkedlist tests"""
    ll = LinkedList(unique=True, ordered=True)
    ll.add("ant")
    ll.add("must")
    ll.add("neon")
    ll.add("zebra")

    self.assertEqual(str(ll), "[ant]->[must]->[neon]->[zebra]")
    self.assertEqual(str(ll.get_slice_as_ll(2)), "[ant]->[must]")
    self.assertEqual(str(ll.get_slice_as_ll(0)), "")
    self.assertEqual(str(ll.get_slice_as_ll(5)), "[ant]->[must]->[neon]->[zebra]")
    self.assertEqual(str(ll.get_slice(2)), "['ant', 'must']")
    self.assertEqual(str(ll.get_slice(0)), "[]")
    self.assertEqual(str(ll.get_slice(5)), "['ant', 'must', 'neon', 'zebra']")
    self.assertEqual(str(ll.get_slice(-1)), "['ant', 'must', 'neon', 'zebra']")

  def test05_extension(self):
    ll = LinkedList(unique=True, ordered=True)
    ll.add("cement")
    self.assertEqual(str(ll.get_slice()), "['cement']")
    ll.extend_from_list(["algebra", "turtle", "books"])
    self.assertEqual(str(ll.get_slice()), "['cement', 'algebra', 'turtle', 'books']")

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

