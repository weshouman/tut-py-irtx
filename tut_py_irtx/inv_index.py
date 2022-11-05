import logging

def get_terms(doc):
  tokens = doc.lower().split()
  terms = set(tokens)
  return list(terms)

def get_term_lists(docs):
  term_lists = []
  for doc in docs:
    term_lists.append(get_terms(doc))

  return term_lists

def get_indices(term_lists, doc_ids=[]):
  indices = {}

  for i, term_list in enumerate(term_lists):
    doc_id = doc_ids[i] if len(doc_ids) > 0 else i

    logging.debug(f"{doc_id}: {term_list}")
    for term in term_list:
      indices.setdefault(term, [])
      indices[term].append(doc_id)

  return indices


