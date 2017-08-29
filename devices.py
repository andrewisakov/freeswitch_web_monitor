#!/usr/bin/python2
# -*- coding: utf-8 -*-

import time, psycopg2
DB_HOST='192.168.222.20'
DB_NAME_FS='freeswitch'
DB_NAME_FSC='freeswitch_configurator'
DB_USER='freeswitch'
DB_PASS='freeswitch'

class Devices(object):
  def __init__(self):
    self.devices = {}
    self.phones = {}
    self.load_data()

  def get_phones(self):
    return self.phones

  def channel(self, phone):
    try:
      return self.phones[phone]
    except:
      return self.phones['0'+phone]

  def __repr__(self):
      return '%s' % self.devices

  def load_data(self):
    con = psycopg2.connect('postgresql://%s:%s@%s/%s?connect_timeout=10' % (DB_USER, DB_PASS, DB_HOST, DB_NAME_FSC))
    c = con.cursor()
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, c)
    c.execute('select d.id, d.address, d.login, d.login_realm, d.password, d.active, d.class_id, dc.name from devices d join device_classes dc on (dc.id=d.class_id) order by dc.name, d.address')
    for d in c.fetchall():
      device_data = {'id': d[0], 
                     'address': d[1],
                     'login': d[2],
                     'login_realm': d[3], 
                     'password': d[4], 
                     'active': d[5], 
                     'class_id': d[6], 
                     'class_name': d[7],
                    }
      self.append(device_data)
    c.close()
    con.close()

  def append(self, device_data):
    self.devices[device_data['id']] = Device(device_data)
    for c in self.devices[device_data['id']].channels:
      self.phones[self.devices[device_data['id']].channels[c].phone] = self.devices[device_data['id']].channels[c]
    #print (self.phones)
    
  def remove(self, device):
    try:
      self.devices[device.id].remove()
      del self.devices[device.id]
    except:
      pass

  def select(self, device_id):
    return self.devices[device_id]

class Device(object):
  def __init__(self, device_data):
    self.channels = {}
    self.device_data = device_data
    self.id = device_data['id']
    self.address = device_data['address']
    self.login = device_data['address']
    self.login_realm = device_data['login_realm']
    self.password = device_data['password']
    self.active = device_data['active']
    self.class_id = device_data['class_id']
    self.class_name = device_data['class_name']
    self.phones = {}
    self.load_data()

  def load_data(self):
    con = psycopg2.connect('postgresql://%s:%s@%s/%s?connect_timeout=10' % (DB_USER, DB_PASS, DB_HOST, DB_NAME_FSC))
    c = con.cursor()
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, c)
    SELECT  = 'select c.id, c.channel, c.device_id, c.login, c.password, c.sip_gateway_name, s.id, s.can_call, s.can_sms, s.phone, s.tagged, '
    SELECT += 's.did, s.operator_id, s.service_id, se.name as service_name '
    SELECT += 'from channels c '
    SELECT += 'left join sim_cards s on (s.channel_id=c.id) '
    SELECT += 'left join services se on (se.id = s.service_id) '
    SELECT += 'where device_id = %s' % self.id
    c.execute(SELECT)
    for ch in c.fetchall():
      channel_data = {'id': ch[0], 
                      'channel': ch[1], 
                      'device_id': ch[2], 
                      'login': ch[3], 
                      'password': ch[4], 
                      'sip_gateway_name': ch[5],
                      'sim_id': ch[6], 
                      'can_call': ch[7], 
                      'can_sms': ch[8],
                      'phone': ch[9],
                      'tagged': ch[10],
                      'did': ch[11],
                      'operator_id': ch[12],
                      'service_id': ch[13],
                      'service_name': ch[14],
                     }
      if channel_data['phone']:
        self.channel_add(channel_data)
    c.close()
    con.close()

  def __repr__(self):
    return ('%s %s %s: %s' % (self.id, self.address, self.class_name, self.channels))

  def params(self):
    return dict(device_id=self.id, address=self.address, class_name=self.class_name, channels=[self.channels[c].params() for c in self.channels])

  def channel_add(self, channel_data):
    if channel_data['can_call']:
      self.channels[channel_data['sip_gateway_name']]=(Channel(self, channel_data))
    else:
      self.channels['0'+channel_data['phone']]=(Channel(self, channel_data))

  def remove(self):
    for c in self.channels:
      self.channel_del(c)

  def channel_del(self, channel):
    try:
      del self.channels[channel.phone]
      del channel
    except:
      pass

class Channel(object):
  def __init__(self, device, channel_data):
    self.device = device
    #print (device)
    #print (channel_data)
    self.id_ = channel_data['id']
    self.channel = channel_data['channel']
    self.device_id = channel_data['device_id'] 
    self.login = channel_data['login']
    self.password = channel_data['password']
    self.sip_gateway_name = channel_data['sip_gateway_name']
    #self.device.channel_add(self)
    self.sim_id   = channel_data['sim_id']
    self.can_call = channel_data['can_call']
    self.can_sms  = channel_data['can_sms']
    self.phone    = channel_data['phone'] if channel_data['phone'] else ''
    self.tagged   = channel_data['tagged']
    self.did      = channel_data['did']
    self.operator_id = channel_data['operator_id']
    self.service_id  = channel_data['service_id']
    self.service_name = channel_data['service_name']

  def __repr__(self):
    return ('%s: %s' % (self.channel, self.params()))

  def set_state(self):
    pass
    
  def params(self):
    return dict(id=self.id_, channel=self.channel, device_id=self.device_id, login=self.login, password=self.password, sip_gateway_name=self.sip_gateway_name,
                sim_id=self.sim_id, can_call=self.can_call, can_sms=self.can_sms, phone=self.phone, tagged=self.tagged, did=self.did, operator_id=self.operator_id, service=self.service_name)

if __name__ == '__main__':
  devices = Devices()
  #print (devices)
  device_id = 3
  for channel in sorted(devices.devices[device_id].channels):
    print (channel, devices.devices[device_id].channels[channel])
  #print (dir())
  """
  for d in sorted(devices.devices):
    print (devices.devices[d].address)
    for c in sorted(devices.devices[d].channels):
      print ('\t', devices.devices[d].channels[c])
  for p in sorted(devices.get_phones()):
    print (p, devices.select_channel(p).params())
  """