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

from datetime import datetime

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
    self.test_start_time = datetime.now()

  @staticmethod
  def get_docs(count=500):
    docs = []
    gen = DocumentGenerator()
    gen.init_word_cache(5000)
    gen.init_sentence_cache(5000)

    for i in range(count):
      gen_doc = gen.paragraph()
      doc = Doc(text=gen_doc, index=i)
      docs.append(doc)

    return docs

  def get_tweets(filename):
    import csv
    reader = csv.reader(open(filename, 'r'), quoting=csv.QUOTE_NONE, delimiter="\t")
    return [ \
             Doc( \
               timestamp=row[0], \
               index=row[1], \
               author_id=row[2], \
               text=row[4], \
             ) for row in reader]

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
    log = logging.getLogger( "test03" )

    instances = []
    for values in [[1,1,25], [1,1,20]]:
      instances.append(Instance(values=values))

    for values in [[0,20,5], [0,23,2], [0,25,1], [2,24,0]]:
      instances.append(Instance(values=values))

    for values in [[15,10,0], [15,15,5], [10,10,0]]:
      instances.append(Instance(values=values))

    kmeansOptimizer = KMeansClusterOptimizer(3, dimensions=3)
    kmeans = kmeansOptimizer.train(instances)

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

  def test04_kmeans_close_instances(self):
    """Capturing close instances"""
    instances = []
    for values in [[1,1], [1,2], [1,3]]:
      instances.append(Instance(values=values))

    for values in [[6,6], [7,6]]:
      instances.append(Instance(values=values))

    kmeans = KMeansCluster(2, dimensions=2)

    kmeans.train(instances)

    ordered_instances = kmeans.clusters[0].get_instances_ordered_by_dist()
    ordered_values = [ordered_inst.values for ordered_inst in ordered_instances]
    self.assertEqual(ordered_values, [[1,2], [1,1], [1,3]], "Elements were captured in a wrong order")

    ordered_instances = kmeans.clusters[1].get_instances_ordered_by_dist()
    ordered_values = [ordered_inst.values for ordered_inst in ordered_instances]
    # NOTE: the cluster center is in the middle, allowing for a change of order
    #       but we expect the instances to be ordered lexicographically anyway
    self.assertEqual(ordered_values, [[6,6], [7,6]], "Elements were captured in a wrong order")

  def test05_kmeans_cluster_docs(self):
    """Clustering documents"""
    log = logging.getLogger( "test05" )

    docs = KMeansTest.get_docs(500)

    ic   = IndexController(docs)

    ic.build()
    ii = ic.inv_indexer()
    elapsed = datetime.now() - self.test_start_time
    print(f"Indexed in {elapsed.total_seconds()} seconds")

    print(f"Ordering terms ...")
    for i, key in enumerate(ii.index.keys()):
      ii.index[key].order = i
    elapsed = (datetime.now() - self.test_start_time) - elapsed
    print(f"Ordered in {elapsed.total_seconds()} seconds")

    print("Updating docs locations and Creating Instances ... ")
    term_count = len(ii.index)

    instances = []
    for doc in docs:
      doc.values = [0]* term_count
      for term in Doc.fetch_terms(doc):
        doc.values[ii.index[term.text].order] += 1
      instances.append(Instance(values=doc.values, data=doc))
    elapsed = (datetime.now() - self.test_start_time) - elapsed
    print(f"Updated docs in {elapsed.total_seconds()} seconds")

    self.verbose_clustering(2, 3, instances, term_count)
    self.verbose_clustering(20, 1, instances, term_count)

  def verbose_clustering(self, cluster_count, seed_count, instances, dimensions):
    start_time = datetime.now()

    print(f"Clustering into {cluster_count} clusters... ")
    kmeansOptimizer = KMeansClusterOptimizer(cluster_count, dimensions=dimensions, seed_count=seed_count)
    kmeans = kmeansOptimizer.train(instances)

    elapsed = (datetime.now() - start_time)
    print(f"Clustered in {elapsed.total_seconds()} seconds")

    elapsed = datetime.now() - self.test_start_time
    print(f"Finished in {elapsed.total_seconds()} seconds")

    print(kmeans)

    print("Instances closest to each cluster center are:")
    for cluster in kmeans.clusters:
      ordered_instances = cluster.get_instances_ordered_by_dist()

      print(f"- Cluster # {cluster.label} [RSS: {cluster.GetRSS()}]:")
      for i, instance in enumerate(ordered_instances):
        if i > 3:
          break
        print(f"  - #{i} [DIST: {instance.get_dist(cluster.cache_centroid)}] {instance.data} {instance.data.text}")

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

