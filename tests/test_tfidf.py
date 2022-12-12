import logging
import unittest
import xmlrunner

import tut_py_irtx.tfidf as tfidf

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class TFIDFTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def assert_tf(self, term_count, expected_tf):
    tf = tfidf.calc_tf(term_count)
    self.assertEqual(round(tf), round(expected_tf), f"Term Frequency of {term_count} should be {expected_tf}")

  def test01_calc_tf(self):
    """The term frequency is correctly computed"""

    tfmul = tfidf.TF_MULTIPLIER
    self.assert_tf(-1000, 0)
    self.assert_tf(0, 0)
    self.assert_tf(1,    1     * tfmul)
    self.assert_tf(10,   2     * tfmul)
    self.assert_tf(15,   2.176 * tfmul)
    self.assert_tf(100,  3     * tfmul)
    self.assert_tf(370,  3.568 * tfmul)
    self.assert_tf(1000, 4     * tfmul)
    self.assert_tf(4000, 4.602 * tfmul)

  def assert_idf(self, docs, total_docs, expected_idf):
    idf = tfidf.calc_idf(docs, total_docs)
    self.assertEqual(round(idf), round(expected_idf), f"Term Frequency of {docs}/{total_docs} should be {expected_idf}")

  def test02_calc_idf(self):
    """The inverted document frequency is correctly computed"""

    idfmul = tfidf.IDF_MULTIPLIER

    with self.assertRaises(ValueError):
      tfidf.calc_idf(1001, 1000)

    self.assert_idf(1000, 1000, 0)
    self.assert_idf(100,  1000, 1     * idfmul)
    self.assert_idf(10,   1000, 2     * idfmul)
    self.assert_idf(5,    1000, 2.301 * idfmul)
    self.assert_idf(1,    1000, 3     * idfmul)

  def test03_calc_similarity(self):
    """The cosine similarity is correctly computed"""
    # using tfmul and idfmul do not do any difference,
    #   as similarity function would normalize
    # it is only used here to match with real scenarios
    tfmul = tfidf.TF_MULTIPLIER
    idfmul = tfidf.IDF_MULTIPLIER

    # query -> home sweet home
    qtf  = [1 * tfmul, 2 * tfmul]
    # the query resembles a single document, no rarity difference
    qidf = [1 * idfmul, 1 * idfmul]
    # document -> has both the words only once 
    dtf  = [1 * tfmul, 1 * tfmul]
    # sweet is rarer than home 
    didf = [2 * idfmul, 3.3 * idfmul]

    similarity = tfidf.get_query_similarity(qtf, qidf, dtf, didf)
    self.assertEqual(round(similarity, 4), 0.9967)

    # sweet is as rare as home 
    didf = [2 * idfmul, 2 * idfmul]

    similarity = tfidf.get_query_similarity(qtf, qidf, dtf, didf)
    self.assertEqual(round(similarity, 4), 0.9487)

    # document -> has `sweet` twice as much it has `home``
    dtf  = [1 * tfmul, 2 * tfmul]

    similarity = tfidf.get_query_similarity(qtf, qidf, dtf, didf)
    self.assertEqual(round(similarity, 7), 1)

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

