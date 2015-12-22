#!/usr/bin/python3

import markdown
import os

class GenException(Exception):
  pass
    
################################################################
# TEMPLATE
################################################################

class Template:

  def __init__(self, template):
    self.template = open(os.path.join('templates', template)).read()

  def replace(self, variables):
    pass

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

    if self.service == 'reddit': self.link = 'http://www.reddit.com/user/' + self.name
    if self.service == 'twitter': self.link = 'http://twitter.com/' + self.name
    if self.service == 'email': self.link = 'mailto:' + self.name

################################################################
# AUTHOR
################################################################

class Author:

  def __init__(self, filename):
    self.key = os.path.split(filename)[1]
    self.name = ''
    self.bio = ''
    self.accounts = []
    
    if filename: self.parse(filename)

  def __repr__(self):
    return self.key + ':' + self.name

  def parse(self, filename):
    f = open(filename)

    self.set_name(f.readline())
    if len(f.readline().strip()) != 0:
      raise GenException('did not expect anything on line 2 of file "' + filename + '"')

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
    return markdown.markdown(self.bio)

  def get_html(self):
    return

  # ACCOUNTS

  def add_account(self, line):
    self.accounts.append(Account(line))

################################################################
# POSTS
################################################################

class Post:

  def __init__(self, filename, category, authors):
    self.category = category
    self.title = ''
    self.author = None
    self.text = ''
    
    if filename: self.parse(filename, authors)

  def parse(self, filename, authors):
    f = open(filename)

    self.set_title(f.readline())
    self.set_author(f.readline(), authors)

  def set_title(self, title):
    self.title = title.strip()

  def set_author(self, author, authors):
    author = author.strip()
    if author not in authors:
      raise GenException('could not find ' + author + ' in authors')
    self.author = authors[author]

################################################################
# GENERATION
################################################################

def get_files(path):
  filenames = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
  return filenames

# author

def generate_authors():
  author_files = get_files('src/author/')
  authors = {}
  for author in author_files:
    a = Author(author)
    authors[a.key] = a
    
  return authors

def generate_articles(authors):
  article_files = get_files('src/article/')
  articles = {}
  for article in article_files:
    a = Post(article, 'article', authors)
    articles.append(a)
    
  return articles

if __name__ == '__main__':
  authors = generate_authors()
  generate_articles(authors)
