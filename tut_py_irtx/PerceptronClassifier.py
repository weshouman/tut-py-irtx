import logging
import random

from tut_py_irtx.util import *
# from tut_py_irtx.Term import *
from tut_py_irtx.Instance import *

class PerceptronClassifier():
  """A document is a representation of the structured form
     that the code retrieves info from"""
  def __init__(self, instances=None):
    self.instances = [] if instances is None else instances
    self.weights = {}

  def __str__(self):
    return f"{len(self.instances)}-{(len(self.weights.keys()))}"

  THETA_PARAM = "THETA_PARAMETER"
  theta_term = Term(THETA_PARAM)

  def train(self):
    # update self.weights
    self.weights.setdefault(self.theta_term.text, random.uniform(-0.3, 0.3))

    # New observations affect to 70% w.r.t. the previous ones 
    FACTOR = 0.7

    for instance in self.instances:
      if not isinstance(instance.labels, list) or \
         len(instance.labels) == 0 or \
         not isinstance(instance.labels[0], int):
        logging.error("instance labels[0] was expected to exist and be either -1 or +1")

      prediction = self.predict(instance, test=False)
      logging.debug(self.get_weights_slice(0))
      if prediction == instance.labels[0]:
        pass
      else:
        # update weights
        terms = Instance.fetch_terms(instance) + [self.theta_term]

        weight_sum = sum([self.weights[term.text] for term in terms])
        sign = 1 if weight_sum > 0 else -1
        for term in terms:
          # self.weights.setdefault(term.text, random.uniform(-1, 1))
          logging.debug( "[PERCEPTRON_CLASSIFIER]" +
                        f"[PREV_WEIGHT: {self.weights[term.text]}]" +
                        f"[STEP: {FACTOR *sign}]")
          self.weights[term.text] = self.weights[term.text] - FACTOR * sign


      logging.debug(self.get_weights_slice(0))

  def predict(self, instance, test=True):
    # stub to a specific target
    instance_weights = []
    for term in Instance.fetch_terms(instance):
      if test == False:
        self.weights.setdefault(term.text, random.uniform(-0.3, 0.3))

      if term.text in self.weights.keys():
        instance_weights.append(self.weights[term.text])
    # weights are multiplied by 1 due to existence in the current instance
    total_weight = sum(instance_weights)

    if total_weight > self.weights[self.theta_term.text]:
    #if total_weight > 0:
      return [1]
    else:
      return [-1]

  def assign_labels(self, in_insts):
    out_insts = []

    for instance in in_insts:
      out_insts.append(self.assign_label(instance))

    return out_insts

  def assign_label(self, instance):
    labels = self.predict(instance)
    instance.predicted_labels.extend(labels)
    return instance

  def get_weights_slice(self, n=10):
    out = f"\nterm      | weight\n"
    for i, key in enumerate(self.weights.keys()):
      if n > 0 and i > n:
        break
      out += f"{key:10}| {self.weights[key]}\n"

    return out