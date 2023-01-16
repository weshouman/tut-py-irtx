from tut_py_irtx.Term import *
from tut_py_irtx.Instance import *

class PerceptronClassifier():
  """A document is a representation of the structured form
     that the code retrieves info from"""
  def __init__(self, instances=None):
    self.instances = [] if instances is None else instances
    self.weights = {}

  def __str__(self):
    return f"{len(self.instances)}-{(len(self.weights.keys()))}"

  def fit(X, y):
    pass

  def train(self):
    # update self.weights
    pass

  def predict(self, instance):
    # stub to a specific target
    return ["neg"]
    # pass

  def assign_labels(self, in_insts):
    out_insts = []

    for instance in in_insts:
      out_insts.append(self.assign_label(instance))

    return out_insts

  def assign_label(self, instance):
    labels = self.predict(instance)
    instance.predicted_labels.extend(labels)
    return instance
