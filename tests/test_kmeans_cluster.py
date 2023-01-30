from essential_generators import DocumentGenerator
import logging
import unittest
import xmlrunner

from tut_py_irtx.IndexController import *
from tut_py_irtx.InvertedIndexer import *
from tut_py_irtx.DocIndexer import *
from tut_py_irtx.KGramIndexer import *
from tut_py_irtx.Doc import *
from tests.stub_inv_index import *
from tut_py_irtx.KMeansCluster import *

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class KMeansTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  @staticmethod
  def get_docs():
    docs = []
    gen = DocumentGenerator()
    gen.init_word_cache(5000)
    gen.init_sentence_cache(5000)

    for i in range(500):
      gen_doc = gen.paragraph()
      doc = Doc(text=gen_doc, index=i)
      docs.append(doc)

    return docs

  def test01_kmeans_cluster_2d(self):
    """KMeans clusters in 2D"""
    log = logging.getLogger( "test01" )
    # logging.getLogger( "test01" ).setLevel( logging.DEBUG )

    instances = []
    for values in [[1,1], [1,2], [1,3]]:
      instances.append(Instance(values=values))

    for values in [[6,6], [7,6]]:
      instances.append(Instance(values=values))

    kmeans = KMeansCluster(2, dimensions=2)

    kmeans.train(instances)

    clustered_instances_count = 0
    for cluster in kmeans.clusters:
      self.assertNotEqual(len(cluster.instances), 0, "An empty cluster was not expected for k<len(instances)")
      for instance in cluster.instances:
        # NOTE: If the instance constructor was appending one extra dimension by mistake
        #       this check would not catch it, and actually that would not make a
        #       difference in the results, it would only increase the computation time
        #       unnecessarily for calculating the euclidean distance for those new dimensions
        self.assertIn(instance, instances, "Instance got mutated while being appended")
        clustered_instances_count += 1

    self.assertEqual(clustered_instances_count, len(instances), "All elements should have been clustered and only clustered once")

    self.assertEqual(len(kmeans.clusters), 2)

    self.assertEqual(kmeans.RSS(), 1.5)

  def test02_kmeans_cluster_3d(self):
    """KMeans clusters in 3D"""
    log = logging.getLogger( "test02" )

    instances = []
    for values in [[1,1,25], [1,1,20]]:
      instances.append(Instance(values=values))

    for values in [[0,20,5], [0,23,2], [0,25,1], [2,24,0]]:
      instances.append(Instance(values=values))

    for values in [[15,10,0], [15,15,5], [10,10,0]]:
      instances.append(Instance(values=values))

    kmeans = KMeansCluster(3, dimensions=3)

    kmeans.train(instances)

    clustered_instances_count = 0
    for cluster in kmeans.clusters:
      self.assertNotEqual(len(cluster.instances), 0, "An empty cluster was not expected for k<len(instances)")
      for instance in cluster.instances:
        self.assertIn(instance, instances, "Instance got mutated while being appended")
        clustered_instances_count += 1

    self.assertEqual(clustered_instances_count, len(instances), "All elements should have been clustered and only clustered once")

    self.assertEqual(len(kmeans.clusters), 3)

    # NOTE: for a seed of zero we actually get the higher cluster RSS, a non optimal one
    self.assertEqual(kmeans.RSS(), 20.93469202522198, "For the seed of 0 we expect a non-optimal cluster")

  def test03_kmeans_cluster_3d_with_multi_seed_optimization(self):
    """KMeans clusters in 3D"""
    log = logging.getLogger( "test02" )

    instances = []
    for values in [[1,1,25], [1,1,20]]:
      instances.append(Instance(values=values))

    for values in [[0,20,5], [0,23,2], [0,25,1], [2,24,0]]:
      instances.append(Instance(values=values))

    for values in [[15,10,0], [15,15,5], [10,10,0]]:
      instances.append(Instance(values=values))

    kmeansOptimizer = KMeansClusterOptimizer(3, dimensions=3)
    kmeans = kmeansOptimizer.train(instances)

    print(kmeans)

    clustered_instances_count = 0
    for cluster in kmeans.clusters:
      self.assertNotEqual(len(cluster.instances), 0, "An empty cluster was not expected for k<len(instances)")
      for instance in cluster.instances:
        self.assertIn(instance, instances, "Instance got mutated while being appended")
        clustered_instances_count += 1

    self.assertEqual(clustered_instances_count, len(instances), "All elements should have been clustered and only clustered once")

    self.assertEqual(len(kmeans.clusters), 3)

    expected_rss = [20.93, 8.91, 24.18]
    self.assertIn(round(kmeans.RSS(),2), expected_rss, "Incorrect cluster is found")

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

