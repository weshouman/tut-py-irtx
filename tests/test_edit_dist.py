import logging
import unittest
import xmlrunner

import tut_py_irtx.lev_dist as lev_dist
from tests.stub_lev_dist import *

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

  def test01_calc_dist(self):
    """The inverted index is correctly generated"""
    dist = lev_dist.get_from_words(stub_word1, stub_word2)
    self.assertEqual(dist, 3, f"distance between {stub_word1} and {stub_word2} should be 3")

    matrix = lev_dist.get_matrix(stub_word1, stub_word2)
    dist = lev_dist.get(matrix)
    self.assertEqual(dist, 3, f"distance between {stub_word1} and {stub_word2} should be 3")

    matrix = lev_dist.get_matrix(stub_word3, stub_word4)
    dist = lev_dist.get(matrix)
    self.assertEqual(dist, 6, f"distance between {stub_word3} and {stub_word4} should be 6")

    matrix = lev_dist.get_matrix(stub_word5, stub_word6)
    dist = lev_dist.get(matrix)
    self.assertEqual(dist, 3, f"distance between {stub_word5} and {stub_word6} should be 3")

  def test02_display_dist_matrix(self):
    """show edit distance matrix"""
    matrix = lev_dist.get_matrix(stub_word1, stub_word2)
    display_matrix = lev_dist.display_matrix(stub_word1, stub_word2, matrix)
    logging.debug(display_matrix)
    self.assertEqual(display_matrix, """
      l, a, s, t
-----------------
 |[0, 1, 2, 3, 4]
r|[1, 1, 2, 3, 4]
a|[2, 2, 1, 2, 3]
t|[3, 3, 2, 2, 2]
s|[4, 4, 3, 2, 3]
""")

    matrix = lev_dist.get_matrix(stub_word3, stub_word4)
    display_matrix = lev_dist.display_matrix(stub_word3, stub_word4, matrix)
    logging.debug(display_matrix)
    self.assertEqual(display_matrix, """
      y, e, l, l, o, w
-----------------------
 |[0, 1, 2, 3, 4, 5, 6]
p|[1, 1, 2, 3, 4, 5, 6]
a|[2, 2, 2, 3, 4, 5, 6]
n|[3, 3, 3, 3, 4, 5, 6]
d|[4, 4, 4, 4, 4, 5, 6]
a|[5, 5, 5, 5, 5, 5, 6]
""")

    matrix = lev_dist.get_matrix(stub_word5, stub_word6)
    display_matrix = lev_dist.display_matrix(stub_word5, stub_word6, matrix)
    logging.debug(display_matrix)
    self.assertEqual(display_matrix, """
      b, a, t
--------------
 |[0, 1, 2, 3]
b|[1, 0, 1, 2]
a|[2, 1, 0, 1]
t|[3, 2, 1, 0]
m|[4, 3, 2, 1]
a|[5, 4, 3, 2]
n|[6, 5, 4, 3]
""")

  def test03_show_detailed_dist_matrix(self):
    """show detailed edit distance matrix"""
    matrix = lev_dist.get_matrix_detailed(stub_word1, stub_word2)
    display_matrix = lev_dist.display_matrix_detailed(stub_word1, stub_word2, matrix)
    self.assertEqual(display_matrix, r"""
          l    , a    , s    , t
---------------------------------
 |/ ,  \ / ,  \ / ,  \ / ,  \ / ,  \
 |\ ,  /,\1, 1/,\2, 2/,\3, 3/,\4, 4/

r|/ , 1\ /1, 2\ /2, 3\ /3, 4\ /4, 5\
 |\ , 1/,\2, 1/,\2, 2/,\3, 3/,\4, 4/

a|/ , 2\ /2, 2\ /1, 3\ /3, 4\ /4, 5\
 |\ , 2/,\3, 2/,\3, 1/,\2, 2/,\3, 3/

t|/ , 3\ /3, 3\ /3, 2\ /2, 3\ /2, 4\
 |\ , 3/,\4, 3/,\4, 2/,\3, 2/,\3, 2/

s|/ , 4\ /4, 4\ /4, 3\ /2, 3\ /3, 3\
 |\ , 4/,\5, 4/,\5, 3/,\4, 2/,\3, 3/

""")

    matrix = lev_dist.get_matrix_detailed(stub_word3, stub_word4)
    display_matrix = lev_dist.display_matrix_detailed(stub_word3, stub_word4, matrix)
    self.assertEqual(display_matrix, r"""
          y    , e    , l    , l    , o    , w
-----------------------------------------------
 |/ ,  \ / ,  \ / ,  \ / ,  \ / ,  \ / ,  \ / ,  \
 |\ ,  /,\1, 1/,\2, 2/,\3, 3/,\4, 4/,\5, 5/,\6, 6/

p|/ , 1\ /1, 2\ /2, 3\ /3, 4\ /4, 5\ /5, 6\ /6, 7\
 |\ , 1/,\2, 1/,\2, 2/,\3, 3/,\4, 4/,\5, 5/,\6, 6/

a|/ , 2\ /2, 2\ /2, 3\ /3, 4\ /4, 5\ /5, 6\ /6, 7\
 |\ , 2/,\3, 2/,\3, 2/,\3, 3/,\4, 4/,\5, 5/,\6, 6/

n|/ , 3\ /3, 3\ /3, 3\ /3, 4\ /4, 5\ /5, 6\ /6, 7\
 |\ , 3/,\4, 3/,\4, 3/,\4, 3/,\4, 4/,\5, 5/,\6, 6/

d|/ , 4\ /4, 4\ /4, 4\ /4, 4\ /4, 5\ /5, 6\ /6, 7\
 |\ , 4/,\5, 4/,\5, 4/,\5, 4/,\5, 4/,\5, 5/,\6, 6/

a|/ , 5\ /5, 5\ /5, 5\ /5, 5\ /5, 5\ /5, 6\ /6, 7\
 |\ , 5/,\6, 5/,\6, 5/,\6, 5/,\6, 5/,\6, 5/,\6, 6/

""")

    matrix = lev_dist.get_matrix_detailed(stub_word5, stub_word6)
    display_matrix = lev_dist.display_matrix_detailed(stub_word5, stub_word6, matrix)
    self.assertEqual(display_matrix, r"""
          b    , a    , t
--------------------------
 |/ ,  \ / ,  \ / ,  \ / ,  \
 |\ ,  /,\1, 1/,\2, 2/,\3, 3/

b|/ , 1\ /0, 2\ /2, 3\ /3, 4\
 |\ , 1/,\2, 0/,\1, 1/,\2, 2/

a|/ , 2\ /2, 1\ /0, 2\ /2, 3\
 |\ , 2/,\3, 1/,\2, 0/,\1, 1/

t|/ , 3\ /3, 2\ /2, 1\ /0, 2\
 |\ , 3/,\4, 2/,\3, 1/,\2, 0/

m|/ , 4\ /4, 3\ /3, 2\ /2, 1\
 |\ , 4/,\5, 3/,\4, 2/,\3, 1/

a|/ , 5\ /5, 4\ /3, 3\ /3, 2\
 |\ , 5/,\6, 4/,\5, 3/,\4, 2/

n|/ , 6\ /6, 5\ /5, 4\ /4, 3\
 |\ , 6/,\7, 5/,\6, 4/,\5, 3/

""")

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

