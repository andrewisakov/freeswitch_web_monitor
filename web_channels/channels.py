#!/usr/bin/python3
import time, psycopg2
__DB_HOST__='192.168.222.20:5432'
__DB_NAME_FS__='freeswitch'
__DB_NAME_FSC__='freeswitch_configurator'
__DB_USER__='freeswitch'
__DB_PASS__='freeswitch'
__channels__ = {}
__devices__ = {}
__db__ = psycopg2.connect('postgresql://%s:%s@%s/%s?connect_timeout=10' % (__DB_USER__, __DB_PASS__, __DB_HOST__, __DB_NAME_FSC__))

"""
 {'inbound_phone': 
   ('line_id': 
     {'caller_id_number': inbound/outbound, answer_wait/-1, 
   ),
 }
"""
channels = {} 
def Agents():
  SELECT  = 'select ug.description, ug.name, u.name '
  SELECT += 'from users u '
  SELECT += 'join user_groups ug on (ug.id = u.group_id) '
  SELECT += 'order by ug.description, u.name'
  c = __db__.cursor()
  c.execute(SELECT)
  agents = {}
  for a in c.fetchall():
    if not (a[0] in agents):
      agents[a[0]] = tuple()
    agents[a[0]] += ((a[2], a[1],),)
  c.close()
  #print (agents)
  return agents

class Channel(object):
  def __init__(self, uuid, channels, ws_queue):
    self.uuid = uuid
    self.channels = channels.channels
    self.callers  = channels.callers
    self.__states__   = dict() # {Event-Sequence: event}
    self.ws_queue = ws_queue
    self.channels[uuid] = self
    self.bridge = None
    self.events = dict(CHANNEL_CREATE=self.channel_update,
                       CHANNEL_ANSWER=self.channel_answer,
                       CHANNEL_HANGUP_COMPLETE=self.channel_hangup_complete,
                       CHANNEL_EXECUTE=self.channel_execute,
                       CHANNEL_EXECUTE_COMPLETE=self.channel_execute_complete,
                       CHANNEL_BRIDGE=self.channel_bridge,
                       CHANNEL_UNBRIDGE=self.channel_unbridge,
                       CHANNEL_ORIGINATE=self.channel_originate,
                       RECORD_STOP=self.record_stop,
                       RECORD_START=self.record_start,
                       CALL_UPDATE=self.channel_update,
                       DTMF=self.dtmf)


  def __del__(self):
    #del self.callers[] # Удалить ловушку
    pass

  def __call__(self, event=None):
    if event:
      self.set_state(event)
    else:
      return self.__states__

  def __normalize__(self, phone):
    return phone[-10:][0]

  def channel_answer(self, event):
    pass

  def channel_create(self, event):
    if event['Call-Direction'] == 'incoming':
      if not (event['Caller-Caller-ID-Name'] in ('0000000000', '6700')): #
        self.callers[event['Caller-Caller-ID-Number']] = self # Выставить ловушку
    else:
      # Получить параметры ловушки
      trap = {'device': self.callers[event['Caller-Caller-ID-Number']].__device__.id,
              'channel': self.callers[event['Caller-Caller-ID-Number']].id}
  
  def channel_hangup_complete(self, event):
    pass

  def channel_execute(self, event):
    pass

  def channel_execute_complete(self, event):
    pass

  def channel_bridge(self, event):
    self.bridge = self.channels[event['Bridge-B-Unique-ID']]

  def channel_unbridge(self, event):
    self.bridge = None

  def channel_originate(self, event):
    pass

  def record_stop(self, event):
    pass

  def record_start(self, event):
    pass

  def call_update(self, event):
    pass

  def dtfm(self, event):
    pass

  def set_state(self, event):
    event['Event-Sequence'] = int(event['Event-Sequence'])
    #self.states[event['Event-Sequence']] = event

    # Нормализовать номера
    if 'Caller-Caller-ID-Name' in event:
      event['Caller-Caller-ID-Name'] = self.__normalize__(event['Caller-Caller-ID-Name'])
    if 'Caller-Callee-ID-Name' in event:
      event['Caller-Callee-ID-Name'] = self.__normalize__(event['Caller-Caller-ID-Name'])

    try:
      self.events[event['Event-Name']](event)
      if 'variable_sip_gateway_name' in event: # Наличие папраметров sip_gateway (Наружу)
        pass
      # Сформировать html блок
      http_text  = '<div id="" class"">' % (event['Event-Sequence'], )
      self.ws_queue.put(http_text)
    except Exception as e:
      pass

  def get_state(self):
    return self.states[sorted(self.states)[-1:][0]] # Вернуть текущий статус

class Channels(object):
  def __init__(self, ws_queue):
    self.channels = {}
    self.bridges  = {}
    self.ws_queue = ws_queue
    self.callers = {} # Ловушки {'Caller-Caller-ID-Number'[-10][0]: channel-uuid, }

  def append(self, uuid):
    self.channels[uuid] = Channel(uuid, self.channels, self.ws_queue)
    return self.channels[uuid]

  def remove(self, uuid):
    del self.channels[uuid]

  def __call__(self, data=None):
    if len (data) > 10: # uuid?
      if data in self.channels:
        return self.channels[uuid]
      else:
        return self.append(uuid)
    else: # Телефон
      if data in self.callers:
        return self.callers[data]
      else:
        return None

class Devices(object):
  def __init__(self):
    self.devices = {}
    self.channels = {} # Быстрый доступ по номеру телефона
    self.sip_gateways = {} # Быстрый доступ по sip_gayeway
    self.__load__()

  def __call__(self, device_id=None):
    if device_id:
      if (device_id in self.devices):
        return self.devices[device_id]
      else:
        return None
    else:
      return self.devices

  def refresh(self):
    self.__load__()

  def __repr__(self):
    return '<Devices: %s' % self.devices
    
  def __load__(self):
    c = __db__.cursor()
    c.execute('select d.id, d.address, d.login, d.login_realm, d.password, d.active, d.class_id, dc.name from devices d join device_classes dc on (dc.id=d.class_id) where d.active=1 order by dc.name, d.address')
    for d in c.fetchall():
      self.append({'id': d[0], 'address': d[1], 'login': d[2], 'login_realm': d[3], 'password': d[4], 'active': d[5], 'class_id': d[6], 'class_name': d[7],})
    c.close()

  def append(self, data):
    device = Device(self, data)
    self.channels.update({ '0'+device.channels[c].phone: device.channels[c] for c in device.channels if device.channels[c].phone })
    self.sip_gateways.update({ device.channels[c].sip_gateway_name: device.channels[c] for c in device.channels if device.channels[c].sip_gateway_name })
    self.devices[data['id']] = device

  def get_device(self, device_id):
    if device_id in self.devices:
      return self.devices[device_id].channels

  def remove(self, device_id):
    del self.devices[device_id]

  def select_channel(self, phone):
    if phone in self.sip_gateways:
      return self.sip_gateways[phone]
    if phone in self.channels:
      return self.channels[phone]
    return None

  def select_class(self, class_id):
    return (self.devices[d] for d in self.devices if self.devices[d].class_id == class_id)


class Device(object):
  def __init__(self, devices, data):
    self.__devices__ = devices
    self.channels = {}
    self.id = data['id']
    self.data = data
    self.class_id = data['class_id']
    self.class_name = data['class_name']
    self.address = data['address']
    self.__load__()

  def __call__(self, channel=None):
    if channel:
      if (channel in self.channels):
        return self.channels[channel]
      else:
        return None
    else:
      return self.channels

  def __del__(self):
    del self.channels
    #print ('Device %s removed...' % self.id)
    pass

  def __repr__(self):
    return '<Device %s: %s>' % (self.id, self.channels)

  def __load__(self):
    c = __db__.cursor()
    SELECT  = 'select c.id, c.channel, c.device_id, c.login, c.password, c.sip_gateway_name, s.id, s.can_call, s.can_sms, s.phone, s.tagged, '
    SELECT += 's.did, s.operator_id, s.service_id, se.name as service_name, se.css_color, se.css_background, c.max_lines '
    SELECT += 'from channels c '
    SELECT += 'left join sim_cards s on (s.channel_id=c.id) '
    SELECT += 'left join services se on (se.id = s.service_id) '
    SELECT += 'where (c.device_id = %s) and (s.id > 0)' % self.id
    c.execute(SELECT)
    for ch in c.fetchall():
      channel_data = {'id'          : ch[0],
                      'channel'     : ch[1],
                      'device_id'   : ch[2],
                      'login'       : ch[3],
                      'password'    : ch[4],
                      'sip_gateway_name': ch[5],
                      'sim_id'      : ch[6],
                      'can_call'    : ch[7],
                      'can_sms'     : ch[8],
                      'phone'       : ch[9],
                      'tagged'      : ch[10],
                      'did'         : ch[11],
                      'operator_id' : ch[12],
                      'service_id'  : ch[13],
                      'service_name': ch[14],
                      'css_color'   : ch[15],
                      'css_background': ch[16],
                      'max_lines': ch[17],
                     }
      self.add_channel(channel_data)

  def add_channel(self, data):
    self.channels[data['channel']] = DeviceChannel(self, data)

  def del_channel(self, channel_id):
    del self.channels[channel_id]

class DeviceChannel(object):
  def __init__(self, device, data):
    self.state = 0
    self.id = data['id']
    self.channel = data['channel']
    self.sim_id = data['sim_id']
    self.phone = data['phone']
    self.service_id = data['service_id']
    self.sip_gateway_name = data['sip_gateway_name']
    self.device_id = data['device_id']
    self.password = data['password']
    self.service_name = data['service_name']
    self.login = data['login']
    self.can_call = data['can_call'] if data['can_call'] else False
    self.can_sms = data['can_sms'] if data['can_sms'] else False
    self.operator_id = data['operator_id']
    self.tagged = data['tagged']
    self.css_color = data['css_color']
    self.css_background = data['css_background']
    self.max_lines = data['max_lines']
    self.__device__ = device
    #print ('Channel %s:%s created...' % (device, data))

  def __repr__(self):
    return '<Channel %s: %s %s>' % (self.id, (self.channel, self.phone), self.__device__.data)

  def set_state(self, data):
    self.event = data['Event-Name']
    self.uuid = data['Channel-Call-UUID']

  def get_state(self):
    return self.state

  def __del__(self):
    #print ('Channel %s removed...' % self.id)
    pass

if __name__ == '__main__':
  devices = Devices()
  #print (devices.devices)
  #print (devices.devices[1])
  #for d in devices.select_class(1): print (d)
  #for d in devices.select_class(2): print (d)
  #for d in devices.select_class(3): print (d)
  #print (devices.sip_gateways)
  #print (devices.select_channel('230021'))
  #print (devices.select_channel('0299999'))
  #print (devices.select_channel('sim_725'))
  print (devices(1)(5066))
  input('4___')
