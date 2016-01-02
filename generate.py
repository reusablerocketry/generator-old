#!/usr/bin/python3

# REQUIRES MARKDOWN AND HTMLMIN

import htmlmin
import markdown
import os
import hashlib
import re

import dirs
import config

import util

import template
import author
import post

################################################################
# GENERATION
################################################################

def get_files(path, ext='md'):
  filenames = [os.path.join(path, f) for path, dirs, files in os.walk(path) for f in files]
  filenames = [x for x in filenames if os.path.splitext(x)[1][1:] == ext]
  return filenames

# author

def get_authors(template_list):
  author_files = get_files(os.path.join('src', 'author'), '')
  authors = {}
  for a in author_files:
    a = author.Author(a)
    authors[a.shortname] = a
    
  return authors

def generate_authors(template_list, author_list):
  for a in author_list.values():
    a.generate(template_list)

def generate_posts(template_list, authors, category):
  if type(category) == type([]):
    a = []
    for x in category:
      a.extend(generate_posts(templates, authors, x))
    return a
  post_files = get_files(os.path.join('src', category), 'md')
  posts = []
  for p in post_files:
    p = post.Post(p, category, authors)
    posts.append(p)
    p.generate(template_list)
    
  return posts

def generate_post_list(templates, posts, categories=[], title='', excluded=[]):
  post_list = []
  
  for post in posts:
    if (categories and post.category not in categories) or post.is_private() or post.category in excluded:
      continue
    post_list.append(post)

  post_list.sort(key=lambda post: post.publish_date, reverse=True) # sort by newest first

  page_variables = {}
  variables = {}
    
  variables['categories'] = ' '.join(categories)
  
  variables['posts'] = ''.join([p.get_html_item(templates) for p in post_list])

  if len(post_list) == 0:
    variables['posts'] = templates.get_raw('post-list-empty', {'categories': variables['categories']})
  
  page_variables['title'] = title
  page_variables['pagetype'] = ' '.join(categories) + ' post-list'
  
  return templates.get('post-list', variables, page_variables)

def generate_about(templates, authors):
  page_variables = {}
  variables = {}

  x = []
  
  authors_sorted = list(authors.values())
  authors_sorted.sort(key=lambda author: author.name, reverse=True)
  for a in authors.values():
    variables = {}
    variables['link'] = a.get_final_path()
    variables['name'] = a.get_name()
    x.append(templates.get_raw('post-author', variables))
    
  variables['authorlist'] = util.andify(x)
    
  page_variables['title'] = 'About'
  page_variables['pagetype'] = 'about'
  
  return templates.get('about', variables, page_variables)

def generate_tools(templates):
  page_variables = {}

  page_variables['title'] = 'Tools'
  page_variables['pagetype'] = 'tools'
  
  return templates.get('tools', {}, page_variables)

def generate_404(templates):
  page_variables = {}

  page_variables['title'] = '404'
  page_variables['pagetype'] = '404'
  
  return templates.get('404', {}, page_variables)

def save_to(filename, text):
  if type(filename) == type([]):
    for x in filename:
      save_to(x, text)
    return
  
  os.makedirs(os.path.split(os.path.join(dirs.build, filename))[0], exist_ok=True)
  open(os.path.join(dirs.build, filename), 'w').write(util.minify_html(text))

if __name__ == '__main__':
  try:
    templates = template.TemplateList()
    authors = get_authors(templates)
    posts = generate_posts(templates, authors, ['article', 'news', 'events', 'update'])

    save_to('index.html', generate_post_list(templates, posts, excluded=['update'], \
                                             title='Welcoming the future of space launch'))
    
    save_to(['articles/index.html', 'article/index.html'], generate_post_list(templates, posts, ['article']))
    save_to('news/index.html', generate_post_list(templates, posts, ['news']))
    save_to('events/index.html', generate_post_list(templates, posts, ['events']))
    save_to(['updates/index.html', 'update/index.html'], generate_post_list(templates, posts, ['update']))
    
    save_to('about/index.html', generate_about(templates, authors))
    save_to('tools/index.html', generate_tools(templates))
    save_to('404.html', generate_404(templates))

    generate_authors(templates, authors)
  except util.GenException as e:
    print('! ' + str(e))
    
