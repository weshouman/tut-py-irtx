import csv
import logging
import math
import unittest
import xmlrunner

# import matplotlib.pyplot as plt

import tut_py_irtx.lev_dist as lev_dist
from tests.stub_lev_dist import *

# Update to a doc
from tut_py_irtx.Instance import *
from tut_py_irtx.PerceptronClassifier import *

import tut_py_irtx.ClassifierUtil as cu

def setUpModule():
  """Triggered before all module tests"""
  logging.debug("setUpModule is triggered")

def tearDownModule():
  """Triggered after all module tests"""
  logging.debug("tearDownModule is triggered")

class PerceptronTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    """Triggered before all class tests"""
    logging.debug("setUpModule is triggered")

  def setUp(self):
    """Triggered before each test"""
    logging.debug("setUp is triggered")

  def parse_csv_reviews(filename):
    reader = csv.reader(open(filename, 'r'), delimiter="\t")

    prediction_map = {"pos": 1, "neg": -1}

    return [ \
             Instance( \
               index=i, \
               text=row[1], \
               labels=[prediction_map[row[0]]], \
             ) for i, row in enumerate(reader)]

  def get_confusion_matrix(instances):
    ys = [instance.labels for instance in instances]
    yhats = [instance.predicted_labels for instance in instances]
    return cu.get_confusion_matrix(ys, yhats)

  # def plot_confusion_matrix(cmatrix, classifier_name):
  #   _, ax = plt.subplots(1, 1)
  #   ax.matshow(cmatrix, cmap='Greens')

  #   for instance in (0, 1):
  #       for y in (0, 1):
  #           ax.text(x, y, cmatrix[y, x])

  #   ax.set_xlabel('predicted label')
  #   ax.set_ylabel('given label')
  #   ax.set_xticklabels(['', 'positive', 'negative'])
  #   ax.set_yticklabels(['', 'positive', 'negative'])
  #   ax.set_title(classifier_name)

  # @unittest.skip("WIP")
  def test01_semantics_read_data(self):
    """The data is correctly read"""

    train_file = "tests/stub_semantics_train.csv"
    train_count = 10

    test_file = "tests/stub_semantics_test.csv"
    test_count = 4

    instances = PerceptronTest.parse_csv_reviews(train_file)

    self.assertEqual(len(instances), train_count, f"{train_file} has {train_count} instances")

    test_instances = PerceptronTest.parse_csv_reviews(test_file)

    self.assertEqual(len(test_instances), test_count, f"{test_file} has {test_count} test instances")

    pc = PerceptronClassifier(instances)
    pc.train()

    test_instances = PerceptronTest.parse_csv_reviews(test_file)
    test_instances = pc.assign_labels(test_instances)

    # print first 10 instances
    for i, ti in enumerate(test_instances):
      if i > 10:
        break
      logging.debug(f"[{ti.index}]: [{ti.text}] [{ti.labels}] [{ti.predicted_labels}]")

    cmatrix = PerceptronTest.get_confusion_matrix(test_instances)

    print(cu.visualize_cmatrix(cmatrix))
    print(f"f1score: {str(cu.get_f1score(cmatrix))}")
    print(pc.get_weights_slice())

  def test02_confusion_matrix_2labels_single_target(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0], [1], [1], [0], [1]]
    yhats = [[0], [1], [0], [1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats)

    self.assertEqual(cmatrix[0][0], 1)
    self.assertEqual(cmatrix[0][1], 1)
    self.assertEqual(cmatrix[1][0], 1)
    self.assertEqual(cmatrix[1][1], 2)

  def test03_confusion_matrix_2labels_single_target_vis(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0], [1], [1], [0], [1]]
    yhats = [[0], [1], [0], [1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats)

    self.assertEqual(cu.visualize_cmatrix(cmatrix), """
                   0          1
       0|          1          1 
       1|          1          2 
""")

  def test04_confusion_matrix_2labels_multi_target(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0,1], [1], [0]  , [0]]
    yhats = [[0]  , [1], [0,1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats)

    self.assertEqual(cu.visualize_cmatrix(cmatrix), """
                   0          1
       0|          2          1 
       1|          0          1 
""")

  def test05_confusion_matrix_2labels_multi_target_NOT_CAT(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0,1], [1], [0]  , [0]]
    yhats = [[0]  , [1], [0,1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats, True)

    self.assertEqual(cu.visualize_cmatrix(cmatrix), """
                   0          1 NOT_CAT   
       0|          2          1          0 
       1|          0          1          1 
NOT_CAT |          0          1          0 
""")

  def test06_confusion_matrix_4labels_multi_target(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0,1], [1], [3]  , [0]]
    yhats = [[0]  , [4], [0,1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats)

    self.assertEqual(cu.visualize_cmatrix(cmatrix), """
                   0          1          3          4
       0|          1          1          0          0 
       1|          0          0          0          1 
       3|          1          1          0          0 
       4|          0          0          0          0 
""")

  def test07_f1score_2labels_single_target(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0], [1], [1], [0], [0], [1]]
    yhats = [[0], [1], [0], [1], [1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats)

    precisions = cu.get_precisions(cmatrix)
    recalls    = cu.get_recalls(cmatrix)
    f1score    = cu.get_f1score(cmatrix) 

    self.assertEqual(precisions, {0: 1/3, 1: 2/3})
    self.assertEqual(recalls, {0: 1/2, 1: 1/2})
    self.assertEqual(f1score, 0.5)

  @unittest.skip("extreme example")
  def test08_f1score_2labels_4labels_multi_target(self):
    """Correct confusion matrix calculation for 2 labels"""
    ys    = [[0,1], [1], [3]  , [0]]
    yhats = [[0]  , [4], [0,1], [1]]

    cmatrix = cu.get_confusion_matrix(ys, yhats)

    precisions = cu.get_precisions(cmatrix)
    recalls    = cu.get_recalls(cmatrix)
    f1score    = cu.get_f1score(cmatrix) 

    # 4 was not available in the train targets, yet we introduced it 
    # into the test outcome, precision would be an infinity (fire)
    # ... may be unsupervised learning mixed with supervised ... !o_O! 
    self.assertEqual(precisions, {0: 1/2, 1: 0, 3: 0})

    # 3 was never recognized in the test targets
    # recall would be an infinity (fire)^2
    self.assertEqual(recalls, {0: 1/2, 1: 0, 4: 0})

    # now for the magic ... positive f1score (fire)^inf
    self.assertEqual(math.round(f1score, 2), 1.11)

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

