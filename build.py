#!/usr/bin/python3

# REQUIRES MARKDOWN AND HTMLMIN

import os

import dirs

import util

import template
import author
import post
import term

################################################################
# GENERATION
################################################################

class Build:

  def __init__(self):
    self.posts = []
    self.authors = {}
    self.template_list = template.TemplateList()

    self.collect_authors()
    
    self.synonyms = {}

    self.posts = []
    self.terms = []
    
    self.collect_posts(['article', 'news', 'update'])
    self.collect_terms(['term'])

    for term in self.terms:
      s = [util.text_to_shortname(x) for x in term.synonyms]
      for x in s:
        if x == term.shortname: continue
        self.synonyms[x] = term.shortname

    self.term_crossreference()

  def term_crossreference(self):
    for term in self.terms:
      term.crossreference()
      
  def get_files(self, path, ext='md'):
    filenames = [os.path.join(path, f) for path, dirs, files in os.walk(path) for f in files]
    filenames = [x for x in filenames if os.path.splitext(x)[1][1:] == ext]
    return filenames

  # AUTHORS

  def collect_authors(self):
    author_files = self.get_files(os.path.join(dirs.src, dirs.src_author), '')
    self.authors = {}
    for a in author_files:
      a = author.Author(a)
      self.authors[a.shortname] = a
      
  # POSTS

  def post_shortname_exists(self, shortname):
    shortname = util.text_to_shortname(shortname)
    for post in self.terms + self.posts:
      if post.shortname == shortname: return post
    return False
  
  def post_get_by_reference(self, reference):
    reference = util.text_to_shortname(reference)
    for post in self.terms + self.posts:
      if reference in post.get_synonyms(): return post
    return False
  
  def collect_posts(self, category):
    
    if type(category) == type([]):
      for x in category:
        self.collect_posts(x)
      return
    
    post_files = self.get_files(os.path.join(dirs.src, category), 'md')
    
    for f in post_files:
      f = f.split('/', 1)[1] # remove dirs.src
      p = post.Post(f, category, self)
      self.posts.append(p)

  def collect_terms(self, directory):
    
    if type(directory) == type([]):
      for x in directory:
        self.collect_terms(x)
      return
    
    term_files = self.get_files(os.path.join(dirs.src, directory), 'md')
    
    for f in term_files:
      f = f.split('/', 1)[1] # remove dirs.src
      p = term.Term(f, self)
      self.terms.append(p)

  def get_all_terms(self):
    terms = []
    for p in self.terms:
      terms.extend(p.get_synonyms())
    return terms

  def get_missing_terms(self):
    used_terms = []
    
    for p in self.posts + self.terms:
      used_terms.extend(p.get_terms())

    all_terms = self.get_all_terms()

    missing_terms = []
    
    for term in used_terms:
      if term not in all_terms:
        missing_terms.append(term)

    missing_terms = list(set(missing_terms))
    return sorted(missing_terms)

  # misc pages

  def generate_tools(self):
    page_variables = {}

    page_variables['title'] = 'Tools'
    page_variables['pagetype'] = 'tools'

    variables = {}
    variables['missing-terms'] = ''.join(['<li><a href="/term/' + x + '/">' + x + '</a></li>' for x in self.get_missing_terms()])
  
    util.save_to('tools/index.html', self.template_list.get('tools', variables, page_variables))

  def generate_404(self):
    page_variables = {}

    page_variables['title'] = '404'
    page_variables['pagetype'] = '404'
  
    util.save_to('404.html', self.template_list.get('404', {}, page_variables))

  def generate_about(self):
    page_variables = {}

    page_variables['title'] = 'About us'
    page_variables['pagetype'] = 'about'
  
    util.save_to('about/index.html', self.template_list.get('about', {}, page_variables))

  # generation
  
  def generate_post_list(self, categories=[], title='', excluded=[], sort='date'):
    post_list = []
    
    for post in self.posts + self.terms:
      if (categories and post.category not in categories) or post.is_private() or post.category in excluded:
        continue
      post_list.append(post)
  
    if sort == 'date':
      post_list.sort(key=lambda post: post.publish_date, reverse=True) # sort by newest first
    elif sort == 'title':
      post_list.sort(key=lambda post: post.title)
  
    page_variables = {}
    variables = {}
      
    variables['categories'] = ' '.join(categories)
    
    variables['posts'] = ''.join([p.get_html_item(self.template_list) for p in post_list])
  
    if len(post_list) == 0:
      variables['posts'] = self.template_list.get_raw('post-list-empty', {'categories': variables['categories']})
    
    page_variables['title'] = title
    page_variables['pagetype'] = ' '.join(categories) + ' post-list'
    
    return self.template_list.get('post-list', variables, page_variables)

  def generate_authors(self):
    print('# authors (' + str(len(self.authors.keys())) + ')')
    for a in self.authors.values():
      a.generate(self.template_list)

  def generate_posts(self):
    print('# posts (' + str(len(self.posts)) + ')')
    for p in self.posts:
      p.generate(self.template_list)

  def generate_terms(self):
    print('# terms (' + str(len(self.terms)) + ')')
    for t in self.terms:
      t.generate(self.template_list)

  # indexes

  def generate_index(self):
    print('  index')
    content = self.generate_post_list(excluded=['update', 'term'], title='Welcoming the future of space launch')
    util.save_to('index.html', content)

  def generate_list_news(self):
    print('  news')
    content = self.generate_post_list(categories=['news'], title='News')
    util.save_to('news/index.html', content)

  def generate_list_articles(self):
    print('  articles')
    content = self.generate_post_list(categories=['articles'], title='Articles')
    util.save_to(['article/index.html', 'articles/index.html'], content)

  def generate_list_terms(self):
    print('  terms')
    content = self.generate_post_list(categories=['term'], title='Terms', sort='title')
    util.save_to(['term/index.html', 'terms/index.html'], content)

  def generate_list_updates(self):
    print('  updates')
    content = self.generate_post_list(categories=['update'], title='Updates', sort='title')
    util.save_to(['update/index.html', 'updates/index.html'], content)

  def generate_missing_terms(self):
    text = open(os.path.join(dirs.src, 'missing-term.md')).read()
    for term in self.get_missing_terms():
      title = 'The entry for "' + term + '" does not exist.'
      
      page_variables = {}
      variables = {}
      
      page_variables['title'] = title
      page_variables['pagetype'] = 'missing-term'

      variables['title'] = title
      variables['text'] = util.markdown_convert(text.format(term=term))[0]

      filename = os.path.join(util.category_dir('term'), term, 'index.html')
      util.save_to(filename, self.template_list.get('missing-term', variables, page_variables))

  def generate(self):
    self.generate_404()

    self.generate_authors()
    self.generate_posts()
    self.generate_terms()
    
    print('# lists')
    self.generate_index()
    self.generate_list_articles()
    self.generate_list_news()
    self.generate_list_terms()
    self.generate_list_updates()

    self.generate_tools()
    self.generate_about()
    
    self.generate_missing_terms()

if __name__ == '__main__':
  try:
    b = Build()
    b.generate()
  except util.GenException as e:
    print('! ' + str(e))
    
