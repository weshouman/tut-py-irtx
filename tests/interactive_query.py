import logging
import unittest
import xmlrunner
import cProfile
import sys, os, pathlib

sys.path.append(os.path.join(pathlib.Path(__file__).parent.resolve(), ".."))

from tut_py_irtx.IndexController import *
from tut_py_irtx.InvertedIndexer import *
from tests.stub_inv_index import *

import csv
import os

DEBUG = False

def main():
  profiled_exec = False
  sample_count = 10

  docs = [Doc(text=stub_doc1, index=stub_doc1_id), \
          Doc(text=stub_doc2, index=stub_doc2_id)]


  ic = IndexController(docs)

  print("building_index")
  if profiled_exec == True:
    cProfile.runctx('ic.build()', globals(), locals())
  else:
    ic.build()

  ii = ic.inv_indexer()
  ki = ic.kgram_indexer()

  if DEBUG:
    indices_slice = ii.get_slice(10)
    print(Term.get_header())
    for i in indices_slice:
      print(i)

  queries = []

  while True:
    text = input("keyword (type ':' to exit, double-enter to query):")
    if text == ":":
      return
    elif text == "":
      print(f"query for {queries}")
      docs = ic.query_intersection_wildcards(queries)
      print(f"found {len(docs)}")
      print(f"first {min(sample_count, len(docs))} doc(s) are:")
      for i, doc in enumerate(docs):
        if i > sample_count:
          break
        print(f"{doc}: {doc.text}")
      queries = []
    else:
      queries.append(text)

      for g in Gram.fetch_wildcard_grams(text):
        if g.text in ki.index.keys():
          print(ki.index[g.text])

if __name__ == "__main__":
  main()

