
import os

import dirs

class Path:

  def __init__(self, local_path, output_path='', local_root='', output_root=''):
    local_path = local_path.strip()
    output_path = output_path.strip()

    self.local_path = local_path
    self.local_root = local_root
    self.output_path = output_path
    self.output_root = output_root

  def __repr__(self):
    return 'Path(' + self.get_local_path() + ', ' + self.get_output_path() + ')'

  def set_local_root(self, local_root):
    self.local_root = local_root

  def set_output_root(self, output_root):
    self.output_root = output_root

  def get_local_path(self, with_prefix=True):
    if self.local_path[0] == '/':
      path = self.local_path[1:]
    else:
      path = os.path.join(self.local_root, self.local_path)

    if with_prefix:
      return os.path.join(dirs.src, path)
    return path
  
  def get_local_output_path(self, with_prefix=True):
    path = os.path.join(self.output_root, self.output_path)
    if with_prefix:
      return os.path.join(dirs.build, path)
    return path

  def get_output_path(self):
    path = os.path.join(self.output_root, self.output_path)
    return os.path.join('/', path)
