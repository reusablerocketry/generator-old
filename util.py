
import re

import markdown
import htmlmin

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

shortname_maxlength = 100

class ImgExtractor(Treeprocessor):
  def run(self, doc):
    "Find all images and append to markdown.images. "
    self.markdown.images = []
    for image in doc.findall('.//img'):
      self.markdown.images.append(image.get('src'))
      
class ImgExtExtension(Extension):
  def extendMarkdown(self, md, md_globals):
    img_ext = ImgExtractor(md)
    md.treeprocessors.add('imgext', img_ext, '>inline')


def md_to_html(i):
  md = markdown.Markdown(extensions=[ImgExtExtension()], output_format='html5')
  return md.convert(i)

def md_images(i):
  md = markdown.Markdown(extensions=[ImgExtExtension()], output_format='html5')
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
  return htmlmin.minify(i, remove_empty_space=True)

def category_dir(cat):
  if cat == 'article': return 'article'
  if cat == 'event': return 'event'
  if cat == 'news': return 'news'

class GenException(Exception):
  pass
