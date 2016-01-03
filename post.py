
import shutil
import os
import time

import config
import dirs
import util

import path

required_keys = ['title', 'author']

################################################################
# POSTS
################################################################

class Post:

  def __init__(self, filename, category, author_list, local=False):
    self.filename = filename
    self.shortname = None
    self.category = category
    
    self.title = ''
    self.authors = []

    self.private = False
    self.local = local
    
    self.text = ''

    # hero image
    self.hero = None

    self.hero_caption = None
    
    self.publish_date = 0
    
    self.modify_date = os.stat(filename).st_mtime
    
    self.parse(filename, author_list)

  def __repr__(self):
    return 'Post(' + self.filename + ')'

  def is_private(self):
    if self.local: return False
    if self.publish_date <= 0: return True
    if self.private: return True
    return False

  def get_local_output_path(self):
    return os.path.join(util.category_dir(self.category), self.shortname, 'index.html')

  def get_post_path(self):
    return os.path.join(util.category_dir(self.category), self.shortname) + '/'

  def get_local_root(self):
    return os.path.split(self.filename)[0]

  def get_local_output_root(self):
    return os.path.split(self.get_local_output_path())[0]

  def parse(self, filename, author_list):
    f = open(filename)

    prefix = os.path.split(filename)[0]

    keys = []

    while True:
      line = f.readline()
      if not line or line.strip() == '':
        break

      try:
        key, value = line.split(':')
      except ValueError:
        raise util.GenException('expected "key: value" in "' + self.filename + '"')
      
      key = key.lower()

      keys.append(key)

      if key == 'title':
        self.set_title(value)
      elif key == 'author':
        self.add_author(value, author_list)
      elif key == 'hero':
        value = value.strip()
        self.hero = value
      elif key == 'hero-caption':
        self.hero_caption = value.strip()
      elif key == 'private':
        value = value.lower().strip()
        if value in ['yes', 'true']: self.private = True
      elif key == 'publish-date':
        try:
          self.publish_date = int(value.strip())
        except ValueError:
          raise util.GenException('expected a unix timestamp for "publish-time" in "' + self.filename + '"')
      else:
        raise util.GenException('could not parse key "' + key + '" in "' + self.filename + '"')

    for k in required_keys:
      if k not in keys:
        raise util.GenException('required key "' + k + '" not present in "' + self.filename + '"')

    self.shortname = util.text_to_shortname(self.title)
    self.text = f.read()

    if self.hero:
      ext = os.path.splitext(self.hero)[1]
      self.hero = path.Path(self.hero, 'hero' + ext, self.get_local_root(), self.get_local_output_root())
      if not os.path.isfile(self.hero.get_local_path()) and not self.is_private():
        raise util.GenException('hero image "' + self.hero.get_local_path() + '" does not exist')


  def set_title(self, title):
    self.title = title.strip()

  def add_author(self, author, author_list):
    author = author.strip()
    if author not in author_list:
      raise util.GenException('could not find author "' + author + '" in authors')
    self.authors.append(author_list[author])

  def set_authors(self, author, author_list):
    authors = author.strip().split(',')
    authors = [a.strip() for a in authors]

    for a in authors:
      self.add_author(author, author_list)

  def get_html_text(self):
    return util.md_to_html(self.text)

  def get_images(self):
    return util.md_images(self.text)

  def get_terms(self):
    return util.md_terms(self.text)

  def get_html_authors(self, template_list):
    x = []
    for a in self.authors:
      variables = {}
      variables['link'] = a.get_final_path()
      variables['name'] = a.get_name()
      x.append(template_list.get_raw('post-author', variables))
    return util.andify(x)
  
  def get_html_item(self, template_list):
    variables = {}
    
    variables['title'] = self.title
    variables['authors'] = self.get_html_authors(template_list)
    
    variables['category'] = self.category
    
    variables['link'] = self.get_post_path()

    variables['publish-date'] = time.strftime('%b %d, %Y %I %p (UTC)', time.gmtime(self.publish_date))
    variables['publish-date-epoch'] = self.publish_date
    
    return template_list.get_raw('post-list-item', variables)
    
  def get_html(self, template_list):
    page_variables = {}
    variables = {}
    
    variables['shortname'] = self.shortname
    
    variables['title'] = self.title
    variables['authors'] = self.get_html_authors(template_list)
    
    variables['category'] = self.category
    
    variables['text'] = self.get_html_text()
    
    variables['publish-date'] = time.strftime('%b %d, %Y %I %p (UTC)', time.gmtime(self.publish_date))
    variables['publish-date-epoch'] = self.publish_date
    
    if self.hero:
      variables['hero'] = self.hero.get_output_path()
      variables['hero-caption'] = self.hero_caption
      variables['header'] = template_list.get_raw('post-header-hero', variables)
    else:
      variables['header'] = template_list.get_raw('post-header', variables)

    page_variables['title'] = self.title
    page_variables['pagetype'] = self.category + ' post'
    return template_list.get('post', variables, page_variables)
  
  # GENERATE

  def generate(self, template_list):
    if self.is_private(): return

    print('  ' + util.category_dir(self.category) + ' ' + self.shortname + '...', end='')
    
    filename = os.path.join(dirs.build, self.get_local_output_path())
    prefix = os.path.split(filename)[0]
    
    os.makedirs(os.path.split(filename)[0], exist_ok=True)
    
    if self.hero:
      shutil.copyfile(self.hero.get_local_path(), self.hero.get_local_output_path())

    images = self.get_images()
    
    for i in images:
      image_path = path.Path(i, i, self.get_local_root(), self.get_local_output_root())
      src = image_path.get_local_path();
      dest = image_path.get_local_output_path()
      print(dest)
      os.makedirs(os.path.split(dest)[0], exist_ok=True)
      shutil.copyfile(src, dest)
    
    open(filename, 'w').write(util.minify_html(self.get_html(template_list)))
    
    print('done')
