
import os

import dirs

class Path:

  def __init__(self, local_path, output_path, local_root='', output_root=''):
    local_path = local_path.strip()
    output_path = output_path.strip()
    self.local_path = local_path
    self.output_path = os.path.join(output_root, output_path)

    if self.local_path[0] == '/':
      self.local_path = os.path.join(dirs.src, local_path[1:])
    elif local_root:
      self.local_path = os.path.join(local_root, local_path)

  def get_local_path(self):
    return self.local_path
  
  def get_local_output_path(self):
    return os.path.join(dirs.build, self.output_path)

  def get_output_path(self):
    return os.path.join('/', self.output_path)
