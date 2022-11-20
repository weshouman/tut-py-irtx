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
    for val in l:
      self.add(val, from_tail=True, ignore_checks=True)
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
    return self.head == None

  def inject_first(self, node):
    """Inject first node into the linked list
       sets up the head and tail"""
    self.head = node
    self.tail = node
    if node != None:
      self.count = self.count + 1

  def inject_tail(self, node):
    if self.is_empty():
      inject_first(node)
    else:
      self.tail.next = node
      self.tail = node
      self.count = self.count + 1

  def inject_head(self, node):
    if self.is_empty():
      inject_first(node)
    else:
      temp = self.head
      self.head = node
      self.head.next = temp
      self.count = self.count + 1

  def get_count(self):
    node = self.head
    count = 0
    while(node != None):
      count = count + 1
      node = node.next

    return count

  def get_intersection(self, other):
    intersection = LinkedList()

    node1 = self.head
    node2 = other.head
    while node1 != None and node2 != None:
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
    while node != None:
      if i >= count and count >= 0:
        break
      if (i >= start):
        l.append(node.data)
      node = node.next
      i = i + 1

    return l

  def get_slice_as_ll(self, count=5, start=0):
    """get first n words as a linked list"""
    if count == 0:
      return LinkedList()

    node    = self.head
    llnew   = LinkedList(node.copy())
    nodenew = llnew.head

    i = 0
    while node.next != None:
      if i >= count-1 and count >= 0:
        break
      node = node.next
      nodenew.next = node.copy()
      nodenew = nodenew.next
      i = i + 1
    return llnew

  def inject_ordered(self, othernode, unique=False):
    """Inject a given node to the ordered linked list"""
    node = self.head

    if othernode == node:
      if (unique == False):
        self.inject_head(othernode)
      return

    if othernode < node:
      self.inject_head(othernode)
      return

    while(node.next != None):
      prev_node = node
      node = node.next
      if othernode > prev_node and othernode < node:
        prev_node.inject(othernode)
        self.count = self.count + 1
        return
      elif othernode == node:
        if (unique == False):
          prev_node.inject(othernode)
          self.count = self.count + 1
        return

    self.inject_tail(othernode)

  def inject_head(self, node):
    temp = self.head
    self.head = node
    self.head.next = temp
    self.count = self.count + 1

  def has(self, othernode):
    node = self.head
    while(node != None):
      if node == othernode:
        return True
      node = node.next
    return False

  def __str__(self):
    return Node.prettyprint(self.head)

  def __len__(self):
    return self.count

@total_ordering
class Node():
  def __init__(self, data):
    self.data = data
    self.next = None

  def copy(self):
    return Node(self.data)

  def inject(self, nodechain):
    temp = self.next
    self.next = nodechain
    nodechain_end = Node.get_last(nodechain)
    nodechain_end.next = temp

  @staticmethod
  def get_last(node):
    upcoming = node.next
    while (upcoming != None):
      return Node.get_last(upcoming)
    return node

  @staticmethod
  def prettyprint(node):
    current = node
    while (current != None):
      if (current.next == None):
        return f"[{current}]"
      else:
        return f"[{current}]->{Node.prettyprint(current.next)}"
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

