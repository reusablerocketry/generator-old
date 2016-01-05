
import os
import re

import markdown
import htmlmin

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.util import etree

import dirs

import hashlib

shortname_maxlength = 100

class ImageExtension(Extension):
  
  def extendMarkdown(self, md, md_globals):
    img_ext = ImageTreeprocessor(md)
    md.treeprocessors.add('imgext', img_ext, '>inline')

class ImageTreeprocessor(Treeprocessor):
  
  def run(self, doc):
    
    "Find all images and append to markdown.images. "
    self.markdown.images = []
    for image in doc.findall('.//img'):
      self.markdown.images.append(image.get('src'))

# LINK CHANGING

def wikify(link):
  return link.title().replace(' ', '_')

class LinkExtension(markdown.Extension):

  def extendMarkdown(self, md, md_globals):

    treeprocessor = LinkTreeprocessor(md)
    treeprocessor.ext = self
    md.treeprocessors['links'] = treeprocessor

class LinkTreeprocessor(markdown.treeprocessors.Treeprocessor):

  def process_term(self, term):
    if term in self.term_synonyms:
      term = self.term_synonyms[term]
      
    self.terms.append(term)
    return '/term/' + term

  def process(self, element):
    if type(element) != type(''): url = element.attrib['href']
    else: url = element
    
    if url.startswith('wikipedia:'):
      return 'https://en.wikipedia.org/wiki/' + wikify(url[len('wikipedia:'):])
    elif url.startswith('reddit:'):
      return url.replace('reddit:', 'https://redd.it/')
    elif url.startswith('term:'):
      term = text_to_shortname(url[len('term:'):])
      return self.process_term(term)
    elif url == 'wikipedia':
      return self.process('wikipedia:' + element.text)
    elif url == 'term':
      return self.process('term:' + element.text)
    else:
      return url

  def children(self, element):
    children = []

    for node in element:
      children.append(node)
      if len(node):
        children.extend(self.children(node))
    return children

  def run(self, root):
    self.terms = []
    
    for element in self.children(root):
      if element.tag == 'a':
        if 'href' in element.attrib:
          element.attrib['href'] = self.process(element)

def markdown_convert(text, term_synonyms):
  md = markdown.Markdown(extensions=[LinkExtension()], output_format='html5')
  md.treeprocessors['links'].term_synonyms = term_synonyms
  html = md.convert(text)
  return (html, md)

def md_to_html(i):
  md = markdown.Markdown(extensions=[LinkExtension()], output_format='html5')
  html = md.convert(i)
  return html

def md_terms(i):
  md = markdown.Markdown(extensions=[LinkExtension()], output_format='html5')
  md.convert(i)
  return md.treeprocessors['links'].terms

def md_images(i):
  md = markdown.Markdown(extensions=[ImageExtension()], output_format='html5')
  md.convert(i)
  return md.images

def text_to_shortname(text):
  text = '-'.join(text.split()).lower()
  text = re.sub('[^0-9a-zA-Z\-]+', '', text)
  text = text[:shortname_maxlength]
  if len(text) == shortname_maxlength: text += '-'
  return text

def andify(l):
  if len(l) == 0: return ''
  if len(l) == 1: return l[0]
  if len(l) >= 3: c = ','
  else:           c = ''
  return ', '.join(l[:-1]) + c + ' and ' + l[-1]

def minify_html(i):
  return htmlmin.minify(i, remove_empty_space=False)

def category_dir(cat):
  if cat == 'article': return 'article'
  if cat == 'news': return 'news'
  if cat == 'update': return 'update'
  if cat == 'term': return 'term'
  return 'unsorted'

class GenException(Exception):
  pass

def unique_hash(t):
  hash_object = hashlib.md5(bytes(t, 'utf-8'))
  return hash_object.hexdigest()


def redirect(url):
  return """<!doctype html><html><head><title>Redirecting</title><meta http-equiv="refresh" content="0; url={url}"></head><body class="redirect">Redirecting...</body></html>""".format(url=url)
  

def save_to(filename, text):
  if type(filename) == type([]):
    for x in filename:
      save_to(x, text)
    return
  
  os.makedirs(os.path.split(os.path.join(dirs.build, filename))[0], exist_ok=True)
  open(os.path.join(dirs.build, filename), 'w').write(minify_html(text))

