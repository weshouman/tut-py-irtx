import logging

# a negative more than one eases debugging
NOT_EXISTENT = 1000

def get_matrix_detailed(word1, word2):
  matrix = []
  prev_l = []
  # "0" is any character, just to make the initialization
  for i, c2 in enumerate("0" + word2):
    logging.debug(f"c2: {c2}")
    l = []
    for j, c1 in enumerate("0" + word1):

      candidates = []
      logging.debug(f"c1: {c1}")

      if len(prev_l) > 0 and len(l) > 0:
        diag = prev_l[j-1]
        if c1 == c2:
          if diag[3] == NOT_EXISTENT:
            candidates.append(0)
          else:
            candidates.append(diag[3])
        else:
          if diag[3] == NOT_EXISTENT:
            candidates.append(1)
          else:
            candidates.append(diag[3]+1)
      else:
        candidates.append(NOT_EXISTENT)
      logging.debug(f"candidates after diag:  {candidates}")

      if len(prev_l) > 0:
        above = prev_l[j]
        if above[3] == NOT_EXISTENT:
          candidates.append(1)
        else:
          candidates.append(above[3]+1)
      else:
        candidates.append(NOT_EXISTENT)
      logging.debug(f"candidates after above: {candidates}")

      if len(l) > 0:
        left = l[j-1]
        if left[3] == NOT_EXISTENT:
          candidates.append(1)
        else:
          candidates.append(left[3]+1)
      else:
        candidates.append(NOT_EXISTENT)
      logging.debug(f"candidates after left:  {candidates}")

      current = min(candidates)
      logging.debug("current")
      logging.debug(current)

      candidates.append(current)
      l.append(candidates)

    prev_l = l
    matrix.append(l)

  return matrix

def get_matrix(word1, word2):
  matrix = []
  prev_l = []
  for i, c2 in enumerate("0" + word2):
    l = []
    for j, c1 in enumerate("0" + word1):

      candidates = []

      if len(prev_l) > 0:
        above = prev_l[j]
        candidates.append(above+1)

      if len(l) > 0:
        left = l[j-1]
        candidates.append(left+1)

      if len(prev_l) > 0 and len(l) > 0:
        diag = prev_l[j-1]
        if c1 == c2:
          candidates.append(diag)
        else:
          candidates.append(diag+1)

      current = min(candidates) if len(candidates) > 0 else 0
      l.append(current)

    prev_l = l
    matrix.append(l)

  return matrix

def display_matrix(word1, word2, matrix):
  out = "\n      " + ", ".join(word1) + "\n"
  out += (len(out)-1) * "-" + "\n"
  for i, l in enumerate(matrix):
    if (i >= 1):
      out +=  word2[i-1] + "|"  + str(l) + "\n"
    else:
      out += " |" + str(l) + "\n"

  return out

def clean_list(l):
  newl = []
  for subl in l:
    newsubl = []
    for val in subl:
      if val == NOT_EXISTENT:
        newval = " "
      else:
        newval = str(val)
      newsubl.append(newval)
    newl.append(newsubl)
  logging.debug(f"l: {l}")
  logging.debug(f"newl: {newl}")
  return newl

def display_matrix_detailed(word1, word2, matrix):
  out = "\n          " + "    , ".join(word1) + "\n"
  out += (len(out)-1) * "-" + "\n"
  for i, l in enumerate(matrix):
    for j in range(2):
      if j == 0 and i >= 1:
        out += f"{word2[i-1]}|"
      else:
        out += " |"
      if j == 0:
        newl = [ f"/{val[0]}, {val[1]}\\" for val in clean_list(l)]
        out += " ".join(newl) + "\n"
      else: #j == 1
        newl = [ f"\{val[2]}, {val[3]}/" for val in clean_list(l)]
        out += ",".join(newl) + "\n\n"

  return out

def get_from_words(word1, word2):
  matrix = get_matrix(word1, word2)

  return matrix[-1][-1]

def get(matrix):
  return matrix[-1][-1]

