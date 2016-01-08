
import os
import shutil

import util
import path

import settings

class Image(path.Path):

  def __init__(self, build, local_path='', output_path='', local_root='', output_root=''):
    path.Path.__init__(self, local_path, output_path, local_root, output_root)

    self.manifest_path = None

    self.build = build

    self.image_filename = None
    self.image_caption = None
    self.image_credit = None
    self.image_license = None
    self.image_type = None
    self.image_gravity = 'center'
    self.image_contains = []

    self.terms = []

    self.image_used = False

    if self.local_path:
      self.parse()

  def parse(self):
    if not self.manifest_path:
      self.manifest_path = self.local_path

    self.local_path = self.manifest_path + '.md'
    
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
    self.output_path = self.output_path + '.jpg'
    self.get_terms()

  def get_output_path_thumb(self):
    path = os.path.join(self.output_root, self.output_path)
    path = os.path.splitext(path)[0] + '@thumb' + os.path.splitext(path)[1]
    return os.path.join('/', path)
  
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
    elif key == 'gravity':
      if value in ['top', 'center', 'middle', 'bottom', 'left', 'right']:
        self.image_gravity = value
      else:
        raise util.GenException('invalid gravity "' + value + '"')
    elif key == 'contains':
      term = util.text_to_shortname(value)
      self.image_contains.append(term)
      self.terms.append(term)
    else:
      return False
    return True

  def __repr__(self):
    return 'Image(' + self.get_local_path() + ', ' + self.get_output_path() + ')'

  def blurred(self, src, dest):
    
    dest = os.path.splitext(dest)[0] + '@thumb' + os.path.splitext(dest)[1]

    resolution = settings.resolution_blurred

    image_size = util.get_image_size(src)

    command = 'convert '+ src + ' '

    command += '-thumbnail ' + 'x'.join([str(x) for x in resolution]) + '^ '

    command += dest

    if os.path.isfile(dest):
      return
    
    os.system(command)

  def resize(self, src, dest, hidpi=False):
    if hidpi:
      resolution = settings.resolution_hidpi
      dest = os.path.splitext(dest)[0] + '@2x' + os.path.splitext(dest)[1]
    else:
      resolution = settings.resolution

    image_size = util.get_image_size(src)

    if image_size[0] < resolution[0] or image_size[1] < resolution[1]:
      print('! image "' + src + '" is too small; blurring will result when scaled up')
    
    command = 'convert '+ src + ' '

    command += '-resize ' + 'x'.join([str(x) for x in resolution]) + '^ '

    command += dest

    if os.path.isfile(dest):
      return
    
    os.system(command)

  def copy(self):
    src = self.get_local_path()
    dest = self.get_local_output_path()

    if not os.path.isfile(src):
      raise util.GenException('could not find image file "' + src + '"')
    
    os.makedirs(os.path.split(dest)[0], exist_ok=True)

    self.blurred(src, dest)
    self.resize(src, dest, False)

    if settings.hidpi:
      self.resize(src, dest, True)
    
    #shutil.copyfile(src, dest)
