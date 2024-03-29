import logging

NOT_CAT = "NOT_CAT"

def append_unique(inlist, val):
  return inlist if val in inlist else inlist + [val]

def get_confusion_matrix(ys, yhats, support_not_categorized=False):
  """
  Parameters
  ----------
  support_not_categorized : bool
    If a target is not categorized at all and it should be categorized
    add a new label called NOT_CAT and append into it
    This should only be needed if a multi target labeling problem is given
  """
  cm = {}

  visited_labels = []

  logging.debug("\n")
  for i in range(len(ys)):
    logging.debug(f"[CM][INSTANCE: {i}][LABELS:      {ys[i]}]")
    logging.debug(f"[CM][INSTANCE: {i}][PRED_LABELS: {yhats[i]}]")
    yl_iter  = iter(ys[i])
    yhl_iter = iter(yhats[i])
    try:
      non_matched_yls = []
      non_matched_yhls = []

      ylabel    = next(yl_iter)
      yhatlabel = next(yhl_iter)
      while True:
        matching_y = False
        matching_yh = False

        # for a single labeled target, there is only one or none
        if ylabel == yhatlabel:
          visited_labels = append_unique(visited_labels, ylabel)

          yl = ylabel
          cm.setdefault(yl, {})
          cm[yl].setdefault(yl, 0)
          cm[yl][yl] = cm[yl][yl] + 1

          try:
            ylabel    = next(yl_iter)
          except StopIteration as ex:
            while True:
              non_matched_yhls.append(next(yhl_iter))

          try:
            yhatlabel    = next(yhl_iter)
          except StopIteration as ex:
            while True:
              non_matched_yls.append(ylabel)
              ylabel = next(yl_iter)

        if ylabel < yhatlabel:
          matching_yh = True
          non_matched_yls.append(ylabel)
          ylabel = next(yl_iter)

          visited_labels = append_unique(visited_labels, ylabel)

        if ylabel > yhatlabel:
          matching_y = True
          non_matched_yhls.append(yhatlabel)
          yhatlabel = next(yhl_iter)

          visited_labels = append_unique(visited_labels, yhatlabel)

    except StopIteration as ex:
      # eventually, add all non_matched_yls vs all non_matched_yls to cm[yl][yhl]
      # to cover the FP and FN

      # just before the exception, we may have been searching for a match
      # for either y or yh, and we couldn't find a match, so we append it here
      if matching_y:
        non_matched_yls.append(ylabel)
      if matching_yh:
        non_matched_yhls.append(yhatlabel)

      if len(non_matched_yhls) == len(non_matched_yls) == 0:
        pass
      elif len(non_matched_yls) > 0 and len(non_matched_yhls) > 0:
        for nmyl in non_matched_yls:
          cm.setdefault(nmyl, {})

          for nmyhl in non_matched_yhls:
            cm[nmyl].setdefault(nmyhl, 0)
            cm[nmyl][nmyhl] += 1

      elif support_not_categorized:
        visited_labels = append_unique(visited_labels, NOT_CAT)
        for nmyl in non_matched_yls:
          cm.setdefault(nmyl, {})
          cm[nmyl].setdefault(NOT_CAT, 0)
          cm[nmyl][NOT_CAT] += 1

        for nmyhl in non_matched_yhls:
          cm.setdefault(NOT_CAT, {})
          cm[NOT_CAT].setdefault(nmyhl, 0)
          cm[NOT_CAT][nmyhl] += 1

      for nmyl in non_matched_yls:
        visited_labels = append_unique(visited_labels, nmyl)
      for nmyhl in non_matched_yhls:
        visited_labels = append_unique(visited_labels, nmyhl)

  # Add zero cells 
  for visited_label in visited_labels:
    cm.setdefault(visited_label, {})
  for key in cm.keys():
    for visited_label in visited_labels:
      cm[key].setdefault(visited_label, 0)

  return cm

def get_mapped_labels(labels, label_map):
  """
  Transform the given ordered labels to an ordered label_map based on the
  given unordered label_map

  Parameters
  ----------
  labels : []
    list of labels as seen in a cmatrix

  label_map : dict
    dict of friendly names of labels, along with the value of each,
    as seen in the cmatrix

  Returns
  -------
  ordered_label_map : dict
    dict of friendly names of labels, along with the value of each,
    as seen in the cmatrix, with the correct order of the cmatrix

    If label_map is None, the labels are used as friendly names
  """
  ordered_label_map = {}
  if label_map is not None:
    for l in labels:
      for key in label_map.keys():
        if l == label_map[key]:
          ordered_label_map.setdefault(key, l)
          continue
  else:
    for l in labels:
      ordered_label_map.setdefault(l, l)

  return ordered_label_map

def visualize_cmatrix(cmatrix, label_map=None):
  labels = cmatrix.keys()

  ordered_label_map = get_mapped_labels(labels, label_map)

  out = f"\n {' ':8}"
  for l in ordered_label_map.keys():
    out += f" {l:>10}"
  out += "\n"

  for l in ordered_label_map.keys():
    out += f"{l:8}| "
    for subl in ordered_label_map.keys():
      # out += f"({l},{subl}){cmatrix[l][subl]:5} "
      out += f"{cmatrix[ordered_label_map[l]][ordered_label_map[subl]]:10} "
    out += "\n"
  return out

def get_precisions(cmatrix):
  labels = cmatrix.keys()

  precisions = {}

  for current in labels:

    tp = cmatrix[current][current]
    tpfp = 0
    for label in labels:
      tpfp += cmatrix[current][label]

    if tpfp == 0:
      continue

    precisions.setdefault(current, (float(tp)/float(tpfp)))

  return precisions

def get_recalls(cmatrix):
  labels = cmatrix.keys()

  recalls = {}

  for current in labels:

    tp = cmatrix[current][current]
    tptn = 0
    for label in labels:
      tptn += cmatrix[label][current]

    if tptn == 0:
      continue

    recalls.setdefault(current, (float(tp)/float(tptn)))

  return recalls

def get_f1score(cmatrix):
  count = len(cmatrix.keys())

  precision = sum(get_precisions(cmatrix).values())/count
  recall = sum(get_recalls(cmatrix).values())/count

  if (precision + recall) == 0:
    logging.error("The classifier got 0 precision and 0 recall!\
      The labels could be inverted")
    return 0

  return (2 * precision * recall) / (precision + recall)

def visualize_tps(cmatrix, label_map=None):
  """Visualize true positives"""
  labels = cmatrix.keys()

  ordered_label_map = get_mapped_labels(labels, label_map)

  out = "true-positives:\n"
  for current in ordered_label_map.keys():
    out += f"  - {current}: {cmatrix[ordered_label_map[current]][ordered_label_map[current]]}\n"

  return out

def visualize_fps(cmatrix, label_map=None):
  """Visualize false positives"""
  labels = cmatrix.keys()

  ordered_label_map = get_mapped_labels(labels, label_map)

  out = "false-positivess:\n"
  for current in ordered_label_map.keys():
    out += f"  - {current}:\n"
    for other in ordered_label_map.keys():
      if current != other:
        out += f"    - {other}: {cmatrix[ordered_label_map[other]][ordered_label_map[current]]}\n"

  return out

def visualize_tns(cmatrix, label_map=None):
  """Visualize true negatives"""
  labels = cmatrix.keys()

  ordered_label_map = get_mapped_labels(labels, label_map)

  out = "true-negatives:\n"
  for current in ordered_label_map.keys():
    out += f"  - {current}:\n"
    for other in ordered_label_map.keys():
      if current != other:
        out += f"    - {other}: {cmatrix[ordered_label_map[current]][ordered_label_map[other]]}\n"

  return out
