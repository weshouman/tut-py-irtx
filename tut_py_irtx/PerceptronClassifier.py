import logging
import random

from tut_py_irtx.util import *
# from tut_py_irtx.Term import *
from tut_py_irtx.Doc import *

class PerceptronClassifier():
  """A document is a representation of the structured form
     that the code retrieves info from"""
  def __init__(self, instances=None):
    self.instances = [] if instances is None else instances
    self.weights = {}

  def __str__(self):
    return f"{len(self.instances)}-{(len(self.weights.keys()))}"

  def train(self):
    # update self.weights

    # New observations affect to 70% w.r.t. the previous ones
    # a factor of the learning rate
    FACTOR = 0.7

    for instance in self.instances:
      if not isinstance(instance.labels, list) or \
         len(instance.labels) == 0 or \
         not isinstance(instance.labels[0], int):
        logging.error("instance labels[0] was expected to exist and be either -1 or +1")

      prediction = self.predict(instance, test=False)
      # this line consumes a lot of time
      # logging.debug(self.get_weights_slice(0))
      if prediction == instance.labels[0]:
        pass
      else:
        # update weights
        terms = Doc.fetch_terms(instance)

        weight_sum = sum([self.weights[term.text] for term in terms])
        # sign is a learning rate of 0.5 of the y-yhat
        sign = 1 if weight_sum > 0 else -1
        for term in terms:
          logging.debug( "[PERCEPTRON_CLASSIFIER]" +
                        f"[PREV_WEIGHT: {self.weights[term.text]}]" +
                        f"[STEP: {FACTOR *sign}]")
          self.weights[term.text] = self.weights[term.text] - FACTOR * sign

      # this line consumes a lot of time
      # logging.debug(self.get_weights_slice(0))

  def predict(self, instance, test=True):
    # stub to a specific target
    instance_weights = []
    for term in Doc.fetch_terms(instance):
      if test == False:
        self.weights.setdefault(term.text, random.uniform(-0.3, 0.3))

      if term.text in self.weights.keys():
        instance_weights.append(self.weights[term.text])
    # weights are multiplied by 1 due to existence in the current instance
    total_weight = sum(instance_weights)

    if total_weight > 0:
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

  def get_weights_slice(self, n=10, order=0):
    """
    Parameters
    ----------
    order : int
      0  for no order
      1  for ascending (least weights first)
      -1 for descending (highest weights first)

    Returns
    -------
    out : str
      formatted text of the list
    """
    if order == 0:
      source = self.weights
    elif order == 1:
      source = dict(sorted(self.weights.items(), key=lambda item: item[1]))
    elif order == -1:
      source = dict(sorted(self.weights.items(), key=lambda item: item[1], reverse=True))
    else:
      source = self.weights

    out = f"\nterm      | weight\n"
    for i, key in enumerate(source.keys()):
      if n > 0 and i > n:
        break
      out += f"{key:10}| {self.weights[key]}\n"

    return out

  def get_extreme_weights(self, n=10, order=1):
    """
    Parameters
    ----------
    order : int
      1  for ascending (least weights first)
      -1 for descending (highest weights first)

    Returns
    -------
    out : []
      a list of the texts in order
    """
    if order == 1:
      source = dict(sorted(self.weights.items(), key=lambda item: item[1]))
    else: # order == -1 and default
      source = dict(sorted(self.weights.items(), key=lambda item: item[1], reverse=True))

    out = []
    for i, key in enumerate(source.keys()):
      if n > 0 and i > n:
        break
      out.append(key)

    return out
