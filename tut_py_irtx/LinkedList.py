from functools import total_ordering

class LinkedList():
  def prepend(self, data, ignore_checks=False):
    self.add(data=data, ignore_checks=ignore_checks, from_tail=False)

  def append(self, data, ignore_checks=False):
    self.add(data=data, ignore_checks=ignore_checks, from_tail=True)

  def __init__(self, node=None, unique=False, ordered=False):
    self.count = 0
    # default to unique elements in the list
    self.unique = unique
    # default to ordered list
    self.ordered = ordered

    self.inject_first(node)

  def extend_from_list(self, l):
    """Inject a list of elements, without considering order or uniqueness

    This function should not be called for an ordered and/or
    unique linked list, to avoid adding a headache of sorting it

    One could either use `inject_tail(sorted(set(l)))`,
    or use `add(elem)` directly

    Parameters
    ----------
    l : list of str
      the list to inject from
    """
    for elem in l:
      self.add(elem, from_tail=True, ignore_checks=True)
    return self

  def add(self, data, from_tail=False, ignore_checks=False):
    """ignore_checks enforces unordered, non_unique addition"""
    node = Node(data)
    if self.is_empty():
      self.inject_first(node)
      return

    if ignore_checks or (self.ordered == False and self.unique == False):
      if from_tail:
        self.inject_tail(node)
      else:
        self.inject_head(node)
    elif self.ordered == True:
      if from_tail:
        raise NotImplementedError()
      else:
        self.inject_ordered(node, self.unique)
    else: #if self.ordered == False and self.unique == True:
      raise NotImplementedError()

  def is_empty(self):
    return self.head is None

  def inject_first(self, node):
    """Inject first node into the linked list
       sets up the head and tail"""
    self.head = node
    self.tail = node
    if node is not None:
      self.count = self.count + 1

    return self.head

  def inject_head(self, node):
    if self.is_empty():
      self.inject_first(node)
    else:
      temp = self.head
      self.head = node

      self.head.next = temp
      temp.prev = self.head

      self.count = self.count + 1

    return self.head

  def inject_tail(self, node):
    if self.is_empty():
      self.inject_first(node)
    else:
      self.tail.next = node
      node.prev = self.tail

      self.tail = node

      self.count = self.count + 1

    return self.tail

  def inject_before(self, node, new):
    """Inject new node before the given node

    NOTE: this is a low level function, which passes the uniqueness and order checks
    thus it should be used with care, otherwise the linked list may reach
    an unstable state
    """
    # node.prev.inject(new)
    # self.count += 1

    if node.prev is not None:
      node.prev.inject(new)
      self.count += 1
    else:
      self.inject_head(new)

    return node.prev

  def inject_after(self, node, new):
    """Inject new node after the given node

    NOTE: this is a low level function, which passes the uniqueness and order checks
    thus it should be used with care, otherwise the linked list may reach
    an unstable state
    """
    if node.next is not None:
      self.count += 1
      node.inject(new)
    else:
      self.inject_tail(new)

    return node.next

  def get_count(self):
    node = self.head
    count = 0
    while(node is not None):
      count = count + 1
      node = node.next

    return count

  def get_intersection(self, other):
    intersection = LinkedList()

    node1 = self.head
    node2 = other.head
    while node1 is not None and node2 is not None:
      if node1 == node2:
        intersection.append(node1.data)
        node1 = node1.next
        node2 = node2.next
      elif node1 < node2:
        # we have to use elif, instead of if, as we always need to check if values are None first
        node1 = node1.next
      elif node1 > node2:
        node2 = node2.next

    return intersection

  def get_slice(self, count=5, start=0):
    l = []
    node = self.head
    i = 0
    while node is not None:
      if i >= count and count >= 0:
        break
      if (i >= start):
        l.append(node.data)
      node = node.next
      i = i + 1

    return l

  def get_slice_as_ll(self, count=5, start=0):
    """get first n words as a linked list"""
    if count == 0 or self.is_empty():
      return LinkedList()

    node    = self.head
    llnew   = LinkedList(node.copy())
    nodenew = llnew.head

    i = 0
    while node.next is not None:
      if i >= count-1 and count >= 0:
        break
      node = node.next
      nodenew.next = node.copy()
      nodenew = nodenew.next
      i = i + 1
    return llnew

  def inject_ordered(self, othernode, unique=False):
    """Inject a given node to the ordered linked list

    It is discouraged to check `has(node)` before calling
    `inject_ordered()` as we already move through the linked list
    while injecting in order.
    """
    if othernode.data < self.head.data:
      self.inject_head(othernode)
      return self.head

    if othernode.data == self.head.data:
      if (unique == False):
        # force injecting the head if similar to the original head
        # NOTE: prev_node is not assigned yet
        self.inject_head(othernode)
      return self.head

    # skip moving through the linkedlist if it's to be appended
    if othernode.data > self.tail.data:
      self.inject_tail(othernode)
      return self.tail

    if othernode.data == self.tail.data:
      if (unique == False):
        self.inject_tail(othernode)
      return self.tail

    node = self.head
    # logging.debug(f"{self.head.data:20} | {othernode.data:20} | {self.tail.data:20}")

    while(node.next is not None):
      prev_node = node
      node = node.next
      if  othernode.data < node.data:
        newnode = prev_node.inject(othernode)
        self.count = self.count + 1
        return newnode
      elif othernode.data == node.data:
        if (unique == False):
          newnode = prev_node.inject(othernode)
          self.count = self.count + 1
        return newnode

  def has(self, othernode):
    """

    Return
    ------
    match : Node
      The matching node if found

    stop : Node
      The node that resulted in stopping the search
      - If this is the same node as the match one, then it was found
      - If this is a different node, then it's the reason of invalidation
        That way we don't need to inject_ordered after it, we could just
        inject before

    Note we did not need to return both nodes, only one would be enough
    but it's always preferrable to keep the logic as simple as possible
    """
    node = self.head
    while(node is not None):
      # comparison through the __lt__ and __eq__ consumes a lot of time as this method is extensively used, and optimizing it is a necessity
      # making the following check usage discouraged
      #if node > othernode:
      #elif node == othernode:

      if node.data > othernode.data:
        return [None, node]
      elif node.data == othernode.data:
        return [node, node]
      node = node.next
    return [None, None]

  def prettyprint(self):
    return Node.prettyprint(self.head)

  def prettyprint_reverse(self):
    return Node.prettyprint_reverse(self.tail)

  def __str__(self):
    return self.prettyprint()

  def __len__(self):
    return self.count

@total_ordering
class Node():
  def __init__(self, data):
    self.data = data
    self.next = None
    self.prev = None

  def copy(self):
    return Node(self.data)

  def inject(self, othernode):
    temp = self.next

    self.next = othernode
    othernode.prev = self

    othernode.next = temp
    temp.prev = othernode

    return self.next

  def inject_chain(self, nodechain):
    temp = self.next

    self.next = nodechain.head
    nodechain.head.prev = self

    nodechain.tail.next = temp
    temp.prev = nodechain.tail

    return self.next

  @staticmethod
  def get_last(node):
    upcoming = node.next
    while (upcoming is not None):
      return Node.get_last(upcoming)
    return node

  @staticmethod
  def prettyprint(node):
    current = node
    while (current is not None):
      if (current.next is None):
        return f"[{current}]"
      else:
        return f"[{current}]->{Node.prettyprint(current.next)}"
    # if current is None
    return ""

  @staticmethod
  def prettyprint_reverse(node):
    current = node
    while (current is not None):
      if (current.prev is None):
        return f"[{current}]"
      else:
        return f"[{current}]->{Node.prettyprint_reverse(current.prev)}"
    # if current is None
    return ""

  def __lt__(self, other):
    return self.data < other.data

  def __eq__(self, other):
    try:
      return self.data == other.data
    except AttributeError:
      return False
    except:
      raise

  def __str__(self):
    return str(self.data)

