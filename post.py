
import shutil
import os
import time

import settings
import dirs
import util

import path

required_keys = ['title', 'author']

class TypeException(Exception):

  pass

################################################################
# POSTS
################################################################

class Post:

  def __init__(self, filename, category, build):
    self.build = build
    
    self.filename = filename
    self.path = path.Path(filename, 'index.html')
    self.shortname = None
    self.category = category
    
    self.title = ''
    self.unique = '' # unique string, used for hashing
    self.unique_hash = None # hash of unique
    self.synonyms = []
    self.authors = []
    
    self.draft = False
    self.private = False

    self.text = ''

    self.md = None

    # hero image
    self.hero = None

    self.hero_caption = None
    
    self.publish_date = 0
    
    self.modify_date = os.stat(self.get_local_path()).st_mtime
    
    self.parse()

  def __repr__(self):
    return 'Post(' + self.filename + ')'

  def is_private(self):
    if self.draft: return True
    if self.publish_date <= 0: return True
    if self.private: return True
    return False

  def get_local_path(self, with_prefix=True):
    # content/post/adsf/adsf.md
    return self.path.get_local_path(with_prefix)

  def get_local_output_path(self, with_prefix=True):
    # output/post/name-foo-bar/index.html
    return self.path.get_local_output_path(with_prefix)

  # root

  def get_local_root(self, with_prefix=True):
    # output/post/name-foo-bar/
    return os.path.dirname(self.get_local_path(with_prefix))

  def get_local_output_root(self, with_prefix=True):
    # output/post/name-foo-bar/
    return os.path.dirname(self.get_local_output_path(with_prefix))

  # post

  def get_post_path(self):
    # /post/name-foo-bar/
    return os.path.dirname(self.path.get_output_path())

  # PARSE FILE

  def parse(self):
    f = open(self.get_local_path(True))

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

      if not self.parse_key(key, value):
        raise util.GenException('could not parse key "' + key + '" in "' + self.filename + '"')

    for k in required_keys:
      if k not in keys and self.key_is_required(k):
        raise util.GenException('required key "' + k + '" not present in "' + self.filename + '"')

    if not self.unique:
      self.set_unique(self.title)
    else:
      self.add_synonym(self.title)

    self.set_shortname(self.unique)
    
    self.text = f.read()

    if self.hero:
      ext = os.path.splitext(self.hero)[1]
      self.hero = path.Path(self.hero, 'hero' + ext, self.get_local_root(False), self.get_local_output_root(False))
      if not os.path.isfile(self.hero.get_local_path(True)):
        raise util.GenException('hero image "' + self.hero.get_local_path(True) + '" does not exist ' + \
                                '(wanted by "' + self.path.get_local_path(True) + '")')

  def key_is_required(self, key):
    if key in required_keys: return True
    return False

  def parse_key(self, key, value):
    # title: awesome foobar title
    if key == 'title':
      self.set_title(value)

    # author: foo
    # author: bar
    elif key == 'author':
      self.add_author(value)
      
    elif key == 'unique':
      self.set_unique(value.strip())

    elif key == 'synonym':
      self.add_synonym(value.strip())

    # hero: /media/spacex-mars.jpg
    elif key == 'hero':
      value = value.strip()
      self.hero = value
    elif key == 'hero-caption':
      self.hero_caption = value.strip()

    # private: true
    elif key == 'private':
      value = value.lower().strip()
      if value in ['yes', 'true']: self.private = True

    # publish-date: <epoch>
    elif key == 'publish-date':
      try:
        self.publish_date = int(value.strip())
      except ValueError:
        raise util.GenException('expected a unix timestamp for "publish-time" in "' + self.filename + '"')
    else:
      return False
    return True

  def set_shortname(self, shortname):
    self.shortname = util.text_to_shortname(self.unique)
    self.term = util.text_to_shortname(self.unique)
    self.path.set_output_root(os.path.join(util.category_dir(self.category), self.shortname))

  def set_title(self, title):
    self.title = title.strip()

  def set_unique(self, unique):
    self.unique = unique
    self.unique_hash = util.unique_hash(unique.strip())
    self.add_synonym(unique)

  def add_synonym(self, synonym):
    self.synonyms.append(synonym)

  def add_author(self, author):
    author = author.strip()
    author_list = self.build.authors
    if author not in author_list:
      raise util.GenException('could not find author "' + author + '" in authors')
    self.authors.append(author_list[author])

  def set_authors(self, author):
    authors = author.strip().split(',')
    authors = [a.strip() for a in authors]

    for a in authors:
      self.add_author(author, self.build.author_list)

  def get_html_text(self):
    md = util.markdown_convert(self.text, self.build.synonyms)
    self.md = md[1]
    return md[0]

  def get_images(self):
    return util.md_images(self.text)

  def get_synonyms(self):
    return self.synonyms

  def get_terms(self):
    if not self.md:
      self.get_html_text()
    return self.md.treeprocessors['links'].terms

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
    
  def generate_html(self, template_list):
    page_variables = {}
    variables = {}
    
    variables['shortname'] = self.shortname
    
    variables['title'] = self.title
    variables['authors'] = self.get_html_authors(template_list)
    
    variables['category'] = self.category
    
    variables['text'] = self.get_html_text()
    
    variables['publish-date'] = time.strftime('%b %d, %Y %I %p (UTC)', time.gmtime(self.publish_date))
    variables['publish-date-epoch'] = self.publish_date
    
    variables['header-classes'] = ''
    if self.hero:
      variables['hero'] = self.hero.get_output_path()
      variables['hero-caption'] = util.markdown_convert(self.hero_caption or '')[0]
      if self.hero_caption:
        variables['header-classes'] += ' has-caption'
      variables['header'] = template_list.get_raw('post-header-hero', variables)
    else:
      variables['header'] = template_list.get_raw('post-header', variables)

    page_variables['title'] = self.title
    page_variables['pagetype'] = self.category + ' post'
    return template_list.get('post', variables, page_variables)
  
  # GENERATE

  def copy_files(self, filename):

    if self.hero:
      shutil.copyfile(self.hero.get_local_path(), self.hero.get_local_output_path())

    images = self.get_images()
    
    for i in images:
      image_path = path.Path(i, i, self.get_local_root(), filename.get_local_output_root())
      src = image_path.get_local_path()
      dest = image_path.get_local_output_path()
      os.makedirs(os.path.split(dest)[0], exist_ok=True)
      shutil.copyfile(src, dest)

  def print_message(self):
    print('  ' + util.category_dir(self.category) + ' ' + self.shortname)
    
  def generate(self, template_list):
    self.print_message()

    content = util.minify_html(self.generate_html(template_list))

    filenames = []
    filenames.append(self.path)
    filenames.append(path.Path('', self.unique_hash[:8] + '/index.html'))

    # for s in self.synonyms:
    #   p = path.Path()
    #   p.copy_from(self.path)
    #   p.set_output_root(os.path.join(util.category_dir(self.category), util.text_to_shortname(s)))
    #   filenames.append(p)

    for s in self.synonyms:
      p = path.Path()
      p.copy_from(self.path)
      p.set_output_root(os.path.join(util.category_dir(self.category), util.text_to_shortname(s)))
      os.makedirs(p.get_local_output_root(), exist_ok=True)
      open(p.get_local_output_path(), 'w').write(util.redirect(self.path.get_output_path()))

    for filename in filenames:
      os.makedirs(filename.get_local_output_root(), exist_ok=True)
      open(filename.get_local_output_path(), 'w').write(content)
      
    self.copy_files(self.path)
      
    
