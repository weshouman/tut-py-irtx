import random
import logging
import math

DEFAULT_DIMENSIONS=2

class KMeansClusterOptimizer:
  def __init__(self, k=2, dimensions=DEFAULT_DIMENSIONS, seed_count=3):
    self.k = k
    self.dimensions = dimensions
    self.seed_count = seed_count

  def train(self, instances):
    kmeans_tries = []
    for seed in range(self.seed_count):
      print(f"[KMEANS][OPTIMIZATION][SEED][STARTED]")
      kmeans = KMeansCluster(self.k, dimensions=self.dimensions)
      kmeans.train(instances, seed=seed)
      kmeans_tries.append(kmeans)
      print(f"[KMEANS][OPTIMIZATION][SEED][FINISHED][CURRENT_RSS: {kmeans.RSS()}]")
    
    min_kmeans = min(kmeans_tries, key=lambda x: x.RSS())
    print(f"[KMEANS][OPTIMIZATION][BEST_RSS: {min_kmeans.RSS()}]")

    return min_kmeans

class KMeansCluster:
  """
  KMeans Cluster algorithm
  """
  def __init__(self, k=2, dimensions=DEFAULT_DIMENSIONS):
    self.k = k
    self.clusters = []
    self.dimensions = dimensions

  def get_init_instances(self, instances, seed):
    """
    Parameters
    ----------
    seed : int
      if 0 return the elements in order
    """
    init_instances = []

    instances_range = range(len(instances))
    if seed == 0:
      for iter in range(min(self.k, len(instances))):
        init_instances.append(instances[iter]) 
    elif self.k > len(instances):
      for iter in len(instances):
        next = random.choice(instances_range)
        init_instances.append(instances[next])
    else:
      sample = random.sample(instances_range, self.k)
      for iter in sample:
        init_instances.append(instances[iter])

    return init_instances

  def train(self, instances, seed=0):
    """
    Parameters
    ----------
    seed : int
      if 0, instances assigned initially to each cluster are not shuffled, but used in order 
    """
    # Step 1: Create k clusters with random centroids
    for c_iter in range(self.k):
      # NOTE: if a cluster's centroid was chosen very far,
      #       the RSS may saturate while the cluster has no instances
      #       to avoid that we could preassign each cluster an instance
      #       that way the centroid would be updated next to the instance it has
      #       and thus the cluster would converge to a state where each cluster
      #       has at least one instance if K is =< len(instances)
      init_instances = self.get_init_instances(instances, seed)
      if c_iter < len(init_instances):
        cluster = Cluster(dimensions=self.dimensions, label=str(c_iter), instances=[init_instances[c_iter]])
      else:
        cluster = Cluster(dimensions=self.dimensions, label=str(c_iter))
      self.clusters.append(cluster)

    # Step 2: Calculate the RSS
    rss_old = 1000000 # <- TODO: use infinity
    while (True):
    # Step 3: While() -> Re-assign instances to the nearest cluster


      logging.info(f"\n[KMEANS][CURRENT-CLUSTERING]\n{self}")

      for cluster in self.clusters:
        cluster.instances = [] # <- the "re" part in "reassign"

      distances = {}
      logging.info(f"[KMEANS][REASSIGNMENTS]")
      for instance in instances:
        for c_iter, cluster in enumerate(self.clusters):
          distances.setdefault(c_iter, 0)
          distances[c_iter] = instance.get_dist(cluster.GetCentroid())

        nearest_cluster_iter = min(distances.items(), key=lambda x: x[1]) 
        logging.info(f"Instance {instance} got assigned to cluster {nearest_cluster_iter[0]} [DIST: {nearest_cluster_iter[1]}]")
        self.clusters[nearest_cluster_iter[0]].instances.append(instance)

    # Step 4: While() -> Adjust the centroid
      for c_iter, cluster in enumerate(self.clusters):
        cluster.UpdateCentroid()

      # Step 5: Once RSS converges break the while()
      rss_new = self.RSS(True)

      print(f"[KMEANS][RSS: ({round(rss_old,2)} -> {round(rss_new,2)}][DIFF: {abs(rss_new-rss_old)}]")
      if KMeansCluster.is_rss_similar(rss_old, rss_new):
        print(f"\n[KMEANS][FINAL-CLUSTERING]\n{self}")
        break

      rss_old = rss_new

  @staticmethod
  def is_rss_similar(rss1, rss2, threshold=0.00001):
    return abs(rss2 - rss1) < threshold

  def RSS(self, force_recompute=False):
    total_rss = 0
    for cluster in self.clusters:
      # self.k is the cluster count
      total_rss += cluster.GetRSS(force_recompute)/self.k

    return total_rss

  def __str__(self):
    out = ""
    for i, cluster in enumerate(self.clusters):
      # sample instances
      out += f"- Cluster #{cluster}\n"
    return out


class Cluster:

  # Maximum visualized instances
  MAX_INSTANCES = 2

  def __init__(self, instances=None, dimensions=DEFAULT_DIMENSIONS, label=""):
    self.instances = [] if instances is None else instances
    # set self.cache_centroid
    self.dimensions = dimensions
    self.label = label # an identifier, useful for debugging
    self.UpdateCentroid(init=True)
    # set self.cache_rss
    self.cache_rss = None
    self.UpdateRSS()

  def GetCentroid(self, force_recompute=False):
    centroid = self.cache_centroid

    if force_recompute or centroid is None:
      centroid = self.UpdateCentroid(init=True)
    return centroid

  def GetRSS(self, force_recompute=False):
    if force_recompute or self.cache_rss is None:
      self.UpdateRSS()
    else:
      # keep the previous cache_rss
      pass

    return self.cache_rss

  def UpdateRSS(self):
    logging.debug(f"[KMeans][RSS-UPDATE][CLUSTER: {self.label}]")
    sum = 0
    for inst in self.instances:
      sum += inst.get_dist(self.cache_centroid)
    self.cache_rss = sum
    logging.debug(f"[KMeans][RSS-UPDATE][{self.cache_rss}]")

  def UpdateCentroid(self, init=False):
    logging.debug(f"[KMEANS][CENTROID-UPDATE][CLUSTER: {self.label}][{len(self.instances)} INSTANCES]")
    if len(self.instances) > 0:
      sum = Instance(self.dimensions)
      for inst in self.instances:
        sum += inst
      self.cache_centroid = sum/len(self.instances)

    elif init:
      self.cache_centroid = Instance(self.dimensions, generate_random=True)

    else:
      # keep the cache_centroid, we have got no instances
      # assigned to the cluster to update it
      pass
    logging.debug(f"[KMEANS][CENTROID-UPDATE][{self.cache_centroid}]")

  def __str__(self):
    return f"{self.label} | centroid: {str(self.cache_centroid):14} | {len(self.instances)} instances | {self.visualize_instances()}"

  def visualize_instances(self):
    instances = self.instances[:self.MAX_INSTANCES]
    # stringify elements
    instances_str = [f"{i}" for i in instances]
    return f"{instances_str}" if len(self.instances) <= self.MAX_INSTANCES else f"{str(instances_str)[:-1]},...]"

  def get_instances_ordered_by_dist(self):
    # no need for capturing the sqrt, the squared_dist is sufficient
    # even a sum of absolute differences could be sufficient too
    return sorted(self.instances, key=lambda x: x.get_dist_squared(self.cache_centroid))

class Instance():
  MAX_DIMENSION_VIS = 10

  def __init__(self, dimensions=DEFAULT_DIMENSIONS, values=None, generate_random=False, data=None):
    # override the dimensions param with the shape if a value if given
    self.dimensions = dimensions if (values is None) else len(values)

    self.set_values(dimensions, values, generate_random)

    # Used for connecting the algorithm to other problems
    # for example it would store the Doc for this project
    self.data = data

  def set_values(self, dimensions, values, generate_random):
    if values is None:
      self.values = []
      if generate_random:
        for d in range(self.dimensions):
          self.values.append(random.randrange(0, 100))
      else:
        for d in range(dimensions):
          self.values.append(0)
    else:
      self.values = values

  def __add__(self, other):
    values = []
    for dim in range(self.dimensions):
      if isinstance(other, int) or isinstance(other, float):
        val = self.values[dim] + other
      elif isinstance(other, Instance):
        val = self.values[dim] + other.values[dim]
      else:
        print(f"Given type is {type(other)}")
        raise TypeError
      values.append(val)

    return Instance(self.dimensions, values)

  def __truediv__(self, other):
    values = []
    for dim in range(self.dimensions):
      if isinstance(other, int):
        val = self.values[dim] / other
      elif isinstance(other, Instance):
        val = self.values[dim] / other.values[dim]
      values.append(val)

    return Instance(self.dimensions, values)

  def __eq__(self, other):
    for dim in range(self.dimensions):
      if self.values[dim] != other.values[dim]:
        return False
    return True

  def __str__(self):
    if self.dimensions > self.MAX_DIMENSION_VIS:
      return f"point in {self.dimensions} dimensions"
    else:
      rounded_values = [round(val,3) for val in self.values]
      return f"{rounded_values}"

  def get_dist_squared(self, other):
    distsquared = 0
    for dim in range(self.dimensions):
      distsquared += (self.values[dim] - other.values[dim])**2

    return distsquared

  def get_dist(self, other):
    distsquared = 0
    for dim in range(self.dimensions):
      distsquared += (self.values[dim] - other.values[dim])**2

    # if (distsquared == 0):
    #   print(self.values)
    #   print(other.values)
    #   print(f"squared_dist: {distsquared}")
    #   print(f"dist: {math.sqrt(distsquared)}")

    return math.sqrt(distsquared)
