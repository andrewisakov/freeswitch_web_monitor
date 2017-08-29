import pickle, random, datetime
from tornado.locks import Semaphore

trunks = Trunk()

class Trunk:
    _trunls = trunks
    def __init__(self, trunk_id, name, max_lines, tag, direction):
	self.id        = trunk_id
	self.name      = name
	self.max_lines = trun
	self.tag       = tag
	self.direction = direction
	self.lines     = { l: {} for l in range(0, max_lines) }
	self.semaphore = Semaphore(1)
	self.callers   = {}
	self.counters  = 
    
    def get_line(self, caller_id_number):
	with (yield self.semaphore):
	    if caller_id_number in self.callers
class Trunks:
  def __init__(self, debug=0):
    self.debug = debug
    try:
      self.data = pickle.load(open('trunks.pickle', 'rb'))
      if self.debug:
        print ('Trunks.__init__: %s Загружено...' % self.data)
    except Exception as e:
      self.data = {}
      if self.debug:
        print ('Trunks.__init__ exception %s' % e)

  def __repr__(self):
    return  ('\n'.join(['«%s»=%s' % (k, (self.data[k] if self.debug else self.data[k][0])) for k in sorted(self.data)]))

  def __getitem__(self, key):
    if key in self.data:
      if self.debug:
        print ('Trunks.__getitem__: «%s»=%s' % (key, self.data[key]))
      return self.data[key][0] if self.debug==0 else self.data[key]
    else:
      if self.debug:
        print ('Trunks.__getitem__: «%s» не существует' % key)
      return None

  def __setitem__(self, key, value):
    if self.debug:
      print ('Trunks.__setitem__: «%s»=%s' % (key, value))
    self.data[key] = (value, datetime.datetime.now()+datetime.timedelta(minutes=5))
    self._save()

  def __delitem__(self, key):
    if key in self.data:
      if self.debug:
        print ('Trunks.__delitem__: «%s»=%s' % (key, self.data[key]))
      del self.data[key]
    else:
      if self.debug:
        print ('Trunks.__delitem__: «%s» не существует' % key)
    self._save()

  def _save(self):
    pickle.dump(self.data, open('trunks.pickle', 'wb'))
    if self.debug:
      print ('Trunks._save...')

trunks = Trunks(debug=0)
"""
trunks['a'] = 1
trunks['b'] = 1
"""
trunks['c'] = 1
"""
trunks['d'] = 1
trunks['e'] = 1
trunks['f'] = 1
trunks['j'] = 1
trunks['h'] = 1
"""

print ('«f»=', trunks['f'])
del trunks['c']
print (trunks)
