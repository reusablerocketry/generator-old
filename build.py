#!/usr/bin/python3

# REQUIRES MARKDOWN AND HTMLMIN

import os

import dirs

import util

import template
import author
import post

################################################################
# GENERATION
################################################################

class Build:

  def __init__(self):
    self.posts = []
    self.authors = {}
    self.template_list = template.TemplateList()

    self.collect_authors()
    self.posts = self.collect_posts(['article', 'news', 'update', 'term'])

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
  
  def collect_posts(self, category):
    
    if type(category) == type([]):
      a = []
      for x in category:
        a.extend(self.collect_posts(x))
      return a
    
    post_files = self.get_files(os.path.join(dirs.src, category), 'md')
    
    posts = []
    for p in post_files:
      p = p.split('/', 1)[1] # remove dirs.src
      p = post.Post(p, category, self.authors)
      posts.append(p)

    return posts

  # misc pages

  def generate_tools(self):
    page_variables = {}

    page_variables['title'] = 'Tools'
    page_variables['pagetype'] = 'tools'
  
    return self.template_list.get('tools', {}, page_variables)

  def generate_404(self):
    page_variables = {}

    page_variables['title'] = '404'
    page_variables['pagetype'] = '404'
  
    util.save_to('404.html', self.template_list.get('404', {}, page_variables))

  # generation
  
  def generate_post_list(self, categories=[], title='', excluded=[], sort='date'):
    post_list = []
    
    for post in self.posts:
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

  def generate(self):
    self.generate_404()

    self.generate_authors()
    self.generate_posts()

    print('# lists')
    self.generate_index()
    self.generate_list_articles()
    self.generate_list_news()
    self.generate_list_terms()
    self.generate_list_updates()

if __name__ == '__main__':
  b = Build()
  b.generate()
