import logging
import math
import numpy as np

TF_MULTIPLIER  = 1000
IDF_MULTIPLIER = 1000

def calc_tf(term_count):
  """
  Returns
  ---------
  tf: int
    Term Frequency, a measure for how frequent a term in a document is.
    0: if document does not have the word.
    [1+log(countOfTermAppearanceInDoc)]*1000: if document has the word.
    The value is multiplied by 1000 to use integers instead of floats.
  """
  if term_count < 1:
    return 0
  else:
    return (1 + math.log10(term_count)) * TF_MULTIPLIER

def calc_idf(docs, total_docs):
  """
  Returns
  -------
  idf: int
    Inverted Document Frequency, a measure of how rare a word is by
    getting the log(totalDocs/docsThisTermAppearedIn)

    Note: The idf is different from calculating based on the 
    Collection Frequency, which is log(totalTokens/countOfToken).
    Calculation based on the collection frequency does not give 
    a real measure of rarity, as a generic word that's common
    between many docs would would give a similar result to a word
    that is a topic-based common, and is usually used a lot when
    talking about a specific topic.
  """
  if docs == 0:
    raise ValueError(f"[IDF] A term appeared in 0 docs, should not be in the dictionary")
    return 0
  elif total_docs < docs:
    raise ValueError(f"[IDF] The term is stated to appear in {docs} documents, however the max document number is {total_docs}")
  else:
    return (math.log10(total_docs/docs)) * IDF_MULTIPLIER

def get_query_similarity(qtf_list, qidf_list, dtf_list, didf_list, tfweight=1, idfweight=1):
  """Calculate cosine similarity.

  Even though the similarity is calculated between queries and documents
  this method could be used to get the similarity between documents.

  Parameters
  ----------
  qtf_list : list of int
    term frequencies of query elements
  qidf_list : list of int 
    inverted document frequencies of query elements
  dtf_list : list of int
    term frequencies of document elements
  didf_list : list of int 
    inverted document frequencies of document elements
  """
  # Prepare arrays
  qtf  = np.array(qtf_list)
  qidf = np.array(qidf_list)
  dtf  = np.array(dtf_list)
  didf = np.array(didf_list)

  q = qtf * qidf
  d = dtf * didf

  qd = np.dot(q, d)
  qlen = np.sqrt(np.dot(q, q))
  dlen = np.sqrt(np.dot(d, d))

  logging.debug(f"\n[q:{q}] \t[d:{d}] \t[qd:{qd}] \t[qlen is {qlen}] \t[dlen is {dlen}]")

  similarity = qd / (qlen * dlen)

  return similarity
