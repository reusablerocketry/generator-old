
import re

import markdown
import htmlmin

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.util import etree

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

  def process(self, element):
    if type(element) != type(''): url = element.attrib['href']
    else: url = element
    
    if url.startswith('wikipedia:'):
      return 'https://en.wikipedia.org/wiki/' + wikify(url[len('wikipedia:'):])
    elif url.startswith('reddit:'):
      return url.replace('reddit:', 'https://redd.it/')
    elif url.startswith('term:'):
      term = text_to_shortname(url[len('term:'):])
      self.terms.append(term)
      return '/term/' + term
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
  if cat == 'event': return 'event'
  if cat == 'news': return 'news'
  if cat == 'update': return 'update'
  if cat == 'terms': return 'term'
  return 'unsorted'

class GenException(Exception):
  pass
