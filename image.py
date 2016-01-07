
import os
import shutil

import util
import path

class Image(path.Path):

  def __init__(self, build, local_path='', output_path='', local_root='', output_root=''):
    path.Path.__init__(self, local_path, output_path, local_root, output_root)

    self.build = build
    
    self.image_filename = None
    self.image_caption = None
    self.image_credit = None
    self.image_license = None
    self.image_type = None
    self.image_contains = []

    self.terms = []

    self.image_used = False

    if local_path:
      self.parse()

  def parse(self):
    self.local_path += '.md'
    
    self.filename = self.get_local_path(True)
    
    if not os.path.isfile(self.filename):
      raise util.GenException('could not find image metadata file "' + self.filename + '"')
    if os.path.splitext(self.filename)[1] != '.md':
      raise util.GenException('expected metadata image file, not "' + self.filename + '"')
    
    f = open(self.filename)

    keys = []

    while True:
      line = f.readline()
      
      if not line:
        break

      if line.strip() == '':
        continue

      try:
        key, value = line.split(':')
      except ValueError:
        raise util.GenException('expected "key: value" in "' + self.filename + '"')

      value = value.strip()
      if value[-1] == '\\':
        value = value[:-1]
        while True:
          line = f.readline()
          if not line: break
          value += ' ' + line.strip()[:-1]
          if line.endswith('\\'):
            continue
          break

      key = key.lower()

      keys.append(key)

      if not self.parse_key(key, value.strip()):
        raise util.GenException('could not parse key "' + key + '" in "' + self.filename + '"')

    self.set_local_root(os.path.dirname(self.filename).split('/', 1)[1])
    self.local_path = self.image_filename
    self.output_path = self.output_path + os.path.splitext(self.local_path)[1]
    self.get_terms()

  def get_terms(self):
    if self.image_caption:
      md = util.markdown_convert(self.image_caption, self.build.synonyms)[1]
      terms = md.terms + self.terms
      return terms
    else:
      return self.terms

  def parse_key(self, key, value):
    if key == 'file':
      self.image_filename = value
    elif key == 'caption':
      self.image_caption = value
    elif key == 'credit':
      self.image_credit = value
    elif key == 'license':
      self.image_license = value
    elif key == 'type':
      self.image_type = value
    elif key == 'contains':
      term = util.text_to_shortname(value)
      self.image_contains.append(term)
      self.terms.append(term)
    else:
      return False
    return True

  def __repr__(self):
    return 'Image(' + self.get_local_path() + ', ' + self.get_output_path() + ')'

  def copy(self):
    src = self.get_local_path()
    dest = self.get_local_output_path()

    if not os.path.isfile(src):
      raise util.GenException('could not find image file "' + src + '"')
    
    os.makedirs(os.path.split(dest)[0], exist_ok=True)
    shutil.copyfile(src, dest)
