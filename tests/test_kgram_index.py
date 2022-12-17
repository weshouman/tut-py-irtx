import logging
import unittest
import xmlrunner
import cProfile

from tut_py_irtx.IndexController import *
from tut_py_irtx.InvertedIndexer import *
from tut_py_irtx.KGramIndexer import *
from tests.stub_inv_index import *

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class KGramIndexTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def test01_kgram_index_generation(self):
    """The kgram index is correctly generated"""

    doc1 = Doc(text=stub_doc1, index=stub_doc1_id)
    doc2 = Doc(text=stub_doc2, index=stub_doc2_id)

    ki   = KGramIndexer(Doc(text=""))

    self.assertIsInstance(ki.fetch_grams(["text"]), list, 'fetch_grams("") returned non list')

    ki.set_docs([])
    self.assertIsInstance(ki.build(force=True), dict, 'KGramIndex.build([]) returned non dict')

    ki.set_docs([doc1])
    kgram_index = ki.build(force=True)
    self.assertIsInstance(kgram_index, dict, "KGramIndex.build returned non dict")

    doc1_bigram_count = 84
    self.assertEqual(len(kgram_index), doc1_bigram_count)

    self.assertTrue("he" in kgram_index, "index 'he' is not created")
    self.assertListEqual(kgram_index["he"].words.get_slice(), ["hello"], "index hello is not set correctly")

    ki.set_docs([doc1, doc2])
    kgram_index = ki.build(force=True)

    self.assertTrue("he" in kgram_index, "index 'he' is not created")
    self.assertListEqual(kgram_index["he"].words.get_slice(), ["hello"], "index hello is not set correctly")

    self.assertTrue("ne" in kgram_index, "index 'ne' is not created")
    # the docs shall get sorted, thus id2 shall preceed id1
    self.assertListEqual(kgram_index["ne"].words.get_slice(), ["imagine", "one", "one-liner"], "index test is not set correctly")

    self.assertTrue("Hello" not in kgram_index, "index Hello is created")
    self.assertNotEqual(len(kgram_index), 44, "commas and dots are not stripped from the string, thus some terms are stored multiple times")
    doc1_and_doc2_gram_count = 144
    self.assertEqual(len(kgram_index), doc1_and_doc2_gram_count)

  def test02_correct_index_slicing(self):
    """Slicing the dictionary works fine"""

    n    = 10
    doc1 = Doc(text=stub_doc1, index=stub_doc1_id)
    doc2 = Doc(text=stub_doc2, index=stub_doc2_id)

    ki   = KGramIndexer(docs=[doc1, doc2], k=2)

    kgram_index = ki.build()

    indices_slice = ki.get_slice(n)
    # it should return equal or less, but for this example, we know that the doc has more than n terms
    # thus it's sufficient
    self.assertEqual(len(indices_slice), n, "get_inv_index_slice returned unexpected number of inv_index")

    indices_slice = ki.get_slice(len(kgram_index) + 1)
    self.assertEqual(len(indices_slice), len(kgram_index), "get_slice returned more than the original inv_index count")

    logging.debug(ki.index_string())

  def test03_query_test(self):
    """query() shall return relevant documents to the given term"""

    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)

    ic   = IndexController([doc1, doc2])

    index_controller = ic.build()

    sample = "inf*"
    docs = ic.query_intersection_wildcards(sample)
    self.assertEqual(len(docs), 2, "Simple query is not working: 'information' exists in both the documents")

    samples = ["hello", "inf*"]
    docs = ic.query_intersection_wildcards(samples)
    self.assertEqual(len(docs), 1, f"Simple query is not working: {samples} exists in a single documents")

    samples = ["*nf*", "*est"]
    docs = ic.query_intersection_wildcards(samples)
    self.assertEqual(len(docs), 2, "Query intersection is not working: 'information' and 'test' is found in both the documents, we should get both the docs")

    logging.debug("\n")
    logging.debug(f"{samples} were found in the following docs\n---")
    logging.debug("---\n".join([ doc.index + ": " + doc.text for doc in docs]))
    logging.debug("---")

  def test04_wildcard_expansion(self):
    kgram_index = {}
    kgram_index["$c"] = Gram("$c", ["cat"])
    kgram_index["ca"] = Gram("ca", ["cat"])
    kgram_index["at"] = Gram("at", ["cat"])
    kgram_index["t$"] = Gram("t$", ["cat"])

    terms = KGramIndexer.expand_wildcard_to_list("ca*", kgram_index)
    self.assertEqual(terms, ["cat"])

  @staticmethod
  def build_core():
    id1  = stub_doc1_id
    id2  = stub_doc2_id
    doc1 = Doc(text=stub_doc1, index=id1)
    doc2 = Doc(text=stub_doc2, index=id2)
    docs = []
    docs.append(doc1)

    for i in range(1000):
      docs.append(doc2)
    ic   = IndexController(docs)

    index_controller = ic.build()

  @staticmethod
  def build_core_various():
    from essential_generators import DocumentGenerator
    docs = []
    gen = DocumentGenerator()
    gen.init_word_cache(5000)
    gen.init_sentence_cache(5000)

    for i in range(500):
      gen_doc = gen.paragraph()
      doc = Doc(text=gen_doc, index=i)
      docs.append(doc)
    ic   = IndexController(docs)

    index_controller = ic.build()

  def test05_profile_redundant_kgrams(self):
    """query() shall return relevant documents to the given term"""
    profiled_exec = False

    d1 = datetime.datetime.now()
    if profiled_exec:
      cProfile.runctx('KGramIndexTest.build_core()', globals(), locals())
    else:
      KGramIndexTest.build_core()

    d2 = datetime.datetime.now()
    threshold = 2
    self.assertLessEqual((d2-d1).seconds, threshold, f"time shall be less than or equal {threshold} seconds")

  def test06_profile_various_kgrams(self):
    """query() shall return relevant documents to the given term"""
    profiled_exec = False
    d1 = datetime.datetime.now()
    if profiled_exec:
      cProfile.runctx('KGramIndexTest.build_core_various()', globals(), locals())
    else:
      KGramIndexTest.build_core_various()

    d2 = datetime.datetime.now()
    threshold = 5
    self.assertLessEqual((d2-d1).seconds, threshold, f"time shall be less than or equal {threshold} seconds")

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

