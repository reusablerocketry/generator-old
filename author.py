
import os

import dirs
import util


################################################################
# ACCOUNT
################################################################

class Account:

  def __init__(self, line):
    self.name = ''
    self.link = ''
    self.service = ''

    if line: self.parse(line)

  def parse(self, line):
    self.service, name = line.strip().split(':')

    if self.service in ['reddit', 'twitter', 'email']:
      self.name = name.strip()

    if self.service == 'reddit':
      self.link = 'http://www.reddit.com/user/' + self.name
      self.name = '/u/' + self.name
    if self.service == 'twitter':
      self.link = 'http://twitter.com/' + self.name
      self.name = '@' + self.name
    if self.service == 'email':
      self.link = 'mailto:' + self.name

  # GENERATE

  def generate(self, templates):
    keys = {}
    keys['name'] = self.name
    keys['link'] = self.link
    keys['service'] = self.service

    return templates.get_raw('author-account', keys)
    
################################################################
# AUTHOR
################################################################

class Author:

  def __init__(self, filename):
    self.shortname = os.path.split(filename)[1]
    self.name = ''
    self.bio = ''
    self.accounts = []
    self.date = os.stat(filename).st_mtime
    
    self.parse(filename)

    self.key = self.shortname

  def get_html_path(self):
    return os.path.join('author', self.shortname, 'index.html')

  def get_final_path(self):
    return os.path.join('author', self.shortname) + '/'

  def __repr__(self):
    return 'Author(' + self.shortname + ')'

  def parse(self, filename):
    f = open(filename)

    self.set_name(f.readline())
    if len(f.readline().strip()) != 0:
      raise util.GenException('did not expect anything on line 2 of file "' + filename + '"')

    bio = ''
    while True:
      line = f.readline()
      if not line or len(line.strip()) == 0: break
      bio += ' ' + line

    self.set_bio(bio)
    
    while True:
      line = f.readline()
      if not line or len(line.strip()) == 0: break
      self.add_account(line)
      
    self.set_bio(bio)

  # NAME

  def set_name(self, name):
    self.name = name.strip()

  def get_name(self):
    return self.name

  # BIO

  def set_bio(self, bio):
    self.bio = bio.strip()

  def get_html_bio(self):
    return util.md_to_html(self.bio)

  # ACCOUNTS

  def add_account(self, line):
    self.accounts.append(Account(line))

  def get_html(self, templates):
    page_variables = {}
    variables = {}
    
    variables['shortname'] = self.shortname
    variables['name'] = self.name
    variables['bio'] = self.get_html_bio()

    variables['accounts'] = ''
    for account in self.accounts:
      variables['accounts'] += account.generate(templates)
    
    page_variables['title'] = self.name
    page_variables['pagetype'] = 'author'
    return templates.get('author', variables, page_variables)
  
  # GENERATE

  def generate(self, templates):
    print('author ' + self.shortname + '...', end='')
    filename = os.path.join(dirs.build, self.get_html_path())
    
    os.makedirs(os.path.split(filename)[0], exist_ok=True)
    open(filename, 'w').write(util.minify_html(self.get_html(templates)))
    print('done')
    
