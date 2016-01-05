
import post

import util

required_keys = ['role', 'title', 'author']
possible_roles = ['manufacturer', 'vehicle', 'spacecraft', 'location', 'component']

class Term(post.Post):

  def __init__(self, filename, build):
    post.Post.__init__(self, filename, 'term', build)

    self.term = None
    self.role = None

  def parse_key(self, key, value):
    if post.Post.parse_key(self, key, value):
      return True
    elif key == 'role':
      self.set_role(value)
    else:
      return False
    return True

  def set_role(self, role):
    role = role.strip()
    if role not in possible_roles:
      raise util.GenException('"' + role + '" is not one of ' + util.andify(possible_roles))
    self.role = role

  def key_is_required(self, key):
    if key in required_keys: return True
    return False

  def print_message(self):
    print('  ' + self.shortname)
