
import post

import util
import re

required_keys = ['role', 'title', 'author']
possible_roles = ['manufacturer', 'vehicle', 'location', 'component']

engine_number_re = re.compile('([a-zA-Z\-0-9]+)\s+\(([0-9]+)\)')

class Role:

  def __init__(self, role, build, term):
    self.role = role
    self.build = build
    self.term = term
    
    self.manufacturers = []
    self.vehicles = []
    self.locations = []
    self.engines = []
    self.stages = []

  def parse_key(self, key, value):
    if key == 'manufacturer':
      self.add_manufacturer(value)
    elif key == 'location':
      self.add_location(value)
    elif key == 'vehicle':
      self.add_vehicle(value)
    elif key == 'engine':
      self.add_engine(value)
    elif key == 'stage':
      self.add_stage(value)
    else:
      return False
    return True

  def has_manufacturer(self, value):
    value = util.text_to_shortname(value)
    if value in self.manufacturers: return True

  def add_manufacturer(self, value):
    value = util.text_to_shortname(value)
    if value in self.manufacturers: return
    self.manufacturers.append(value)
    self.term.add_term(value)

  def add_location(self, value):
    value = util.text_to_shortname(value)
    if value in self.locations: return
    self.locations.append(value)
    self.term.add_term(value)

  def add_vehicle(self, value):
    value = util.text_to_shortname(value)
    if value in self.vehicles: return
    self.vehicles.append(value)
    self.term.add_term(value)

  def add_stage(self, value):
    value = util.text_to_shortname(value)
    if value in self.stage: return
    self.stages.append(value)
    self.term.add_term(value)

  def add_engine(self, value):
    m = engine_number_re.match(value)
    if m:
      name = m.group(1)
      number = m.group(2)
    else:
      name = value
    if name in self.engines: return
    self.engines.append(name)
    self.term.add_term(name)

  # NAME

  def get_name(self):
    return self.term.title
    
  def get_unique(self):
    return self.term.unique

  # GENERATION
    
  def generate_item_html(self):
    t = self.build.template_list

    variables = {}
    variables['class'] = self.role
    variables['name'] = self.get_name()
    variables['link'] = self.term.get_post_path()

    return t.get_raw('term-sidebar-item', variables)

  def get_page_list(self, shortnames, thing):
    items = []
    for sn in shortnames:
      p = self.build.post_get_by_reference(sn)
      if not p:
        print('! ' + thing + ' "' + sn + '" not found (wanted by "' + self.term.get_local_path() + '")')
        continue
      if not p.data:
        print('! ' + thing + ' "' + sn + '" has no metadata (wanted by "' + self.term.get_local_path() + '")')
        continue
      items.append(p.data.generate_item_html())
    return items

  def generate_items_html(self, thing, source_list):
    things = self.get_page_list(source_list, thing)

    if not things: return ''
    
    variables = {}
    variables['class'] = thing
    variables['list'] = ' '.join(things)
    variables['title'] = thing.title() + util.plural_list(things)
    
    return self.build.template_list.get_raw('term-sidebar-list', variables)
  
  def generate_manufacturers(self):
    self.variables['contents'] += self.generate_items_html('manufacturer', self.manufacturers)
    
  def generate_vehicles(self):
    self.variables['contents'] += self.generate_items_html('vehicle', self.vehicles)
    
  def generate_locations(self):
    self.variables['contents'] += self.generate_items_html('location', self.locations)
    
  def generate_engines(self):
    self.variables['contents'] += self.generate_items_html('engine', self.engines)
    
  def generate_stages(self):
    self.variables['contents'] += self.generate_items_html('stage', self.stages)
    
  def generate_html(self):
    t = self.build.template_list

    self.variables = {}

    self.variables['contents'] = ''

    self.role_generate_contents()

    if self.variables['contents'] == '': return ''
    
    return t.get_raw('term-sidebar', self.variables)
  
  def role_generate_contents(self):
    pass

  def crossreference_things(self, things, role):
    things = []
    for t in self.build.terms:
      if t.data and t.data.role == role:
        things.append(t)
    return things

  def crossreference(self):
    synonyms = self.build.synonyms
    self.engines = [synonyms.get(e, e) for e in self.engines]
    self.vehicles = [synonyms.get(e, e) for e in self.vehicles]
    self.manufacturers = [synonyms.get(e, e) for e in self.manufacturers]
    
    for t in self.crossreference_things(self.engines, 'engine'):
      if t.data.has_manufacturer(self.get_unique()):
        self.add_engine(t.data.get_unique())
    for t in self.crossreference_things(self.vehicles, 'vehicle'):
      if t.data.has_manufacturer(self.get_unique()):
        self.add_vehicle(t.data.get_unique())
      
class Manufacturer(Role):

  def __init__(self, build, term):
    Role.__init__(self, 'manufacturer', build, term)

  def role_generate_contents(self):
    self.generate_vehicles()
    self.generate_locations()
    self.generate_engines()
    
class Vehicle(Role):

  def __init__(self, build, term):
    Role.__init__(self, 'vehicle', build, term)

  def role_generate_contents(self):
    self.generate_manufacturers()
    self.generate_locations()
    self.generate_engines()
    self.generate_stages()
    
class Engine(Role):

  def __init__(self, build, term):
    Role.__init__(self, 'engine', build, term)

  def role_generate_contents(self):
    self.generate_manufacturers()
    self.generate_stages()
    self.generate_locations()
    
class Term(post.Post):

  def __init__(self, filename, build):
    self.term = None
    self.role = None

    self.data = None
    self.mfgs = []
    self.vehicles = []

    post.Post.__init__(self, filename, 'term', build)

  def parse_key(self, key, value):
    if post.Post.parse_key(self, key, value):
      return True
    elif key == 'role':
      self.set_role(value)
    else:
      if self.data:
        return self.data.parse_key(key, value)
      else:
        return False
    return True

  def set_role(self, role):
    role = role.strip()
    if role == 'vehicle':
      self.data = Vehicle(self.build, self)
    elif role == 'manufacturer':
      self.data = Manufacturer(self.build, self)
    elif role == 'engine':
      self.data = Engine(self.build, self)
    else:
      raise util.GenException('"' + role + '" is not one of ' + util.andify(possible_roles))
    
    self.role = role

  def key_is_required(self, key):
    if key in required_keys: return True
    return False

  def print_message(self):
    print('  ' + self.shortname)

  def modify_text(self, text):
    if self.data:
      return self.data.generate_html() + text
    return text

  def crossreference(self):
    if self.data:
      self.data.crossreference()
