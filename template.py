
import os

import datetime
import settings
import dirs

################################################################
# TEMPLATE
################################################################

class Template:

  def __init__(self, template):
    self.template = open(os.path.join(dirs.template, template + '.html')).read()

  def get(self, variables={}, alternate=''):
    # variables CANNOT be nested
    x = self.template
    if alternate: x = alternate
    return x.format(**variables)

################################################################
# TEMPLATELIST
################################################################

class TemplateList:

  def __init__(self):
    self.master = Template('master')
    self.templates = {}

  def add_template(self, template):
    self.templates[template] = Template(template)

  def get(self, template, variables={}, page_variables={}):
    if template not in self.templates and template:
      self.add_template(template)

    page_variables['body'] = self.templates[template].get(variables)
    
    if 'title' not in page_variables or not page_variables['title']:
      page_variables['title'] = settings.name
    else:
      page_variables['title'] = page_variables['title'] + settings.titlesep + settings.name
      
    page_variables['date'] = datetime.datetime.now().isoformat()
    
    return self.master.get(page_variables)

  def get_raw(self, template, variables={}):
    if template not in self.templates:
      self.add_template(template)
      
    return self.templates[template].get(variables)
  
