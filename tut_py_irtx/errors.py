class IndexNotFoundError(Exception):
  def __init__(self, indextype, message=None):
    if message == None:
      self.message = f"Index({indextype}) not set"
    else:
      self.message = message

    super().__init__(self.message)
