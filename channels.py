#!/usr/bin/python2
# -*- coding: utf-8 -*-

import datetime, time, threading, plugins, Queue, requests, json
#from collections import deque as queue

CHANNEL_LIVE_TIME = 300
BRIDGE_LIVE_TIME  = 600
channels = {}
bridges  = {}
timestamp = datetime.datetime.now

class bridge(threading.Thread):
  def __init__(self, data):
    threading.Thread.__init__(self)
    self.AUID = data['Bridge-A-Unique-ID']
    self.BUID = data['Bridge-B-Unique-ID']
    self.name = '%s:%s' % (self.AUID, self.BUID)
    self.in_queue = Queue.Queue()
    self.in_queue.put(data)
    self.active = True

  def put(self, data):
    self.in_queue.put(data)

  def run(self):
    while self.active:
      try:
        event = self.in_queue.get(timeout=BRIDGE_LIVE_TIME)
        try:
          if   event['Event-Name'] == 'CHANNEL_BRIDGE':
            #channels[event['Bridge-A-Unique-ID']].set_bridge(self)
            #channels[event['Bridge-B-Unique-ID']].set_bridge(self)
            print ('bridge %s %s %s %s -> %s' % (self.name, event['Event-Name'], timestamp(), self.AUID, self.BUID))
          elif event['Event-Name'] == 'CHANNEL_UNBRIDGE':
            #channels[event['Bridge-A-Unique-ID']].set_unbridge()
            #channels[event['Bridge-B-Unique-ID']].set_unbridge()
            print ('bridge %s %s %s %s -> %s' % (self.name, event['Event-Name'], timestamp(), self.AUID, self.BUID))
            break
        except Exception as e:
          print ('%s: %s' % (self.name, e))
      except Exception, e:
        self.active = False
    del bridges[self.name]

class channel(threading.Thread):
  def __init__(self, data):
    threading.Thread.__init__(self)
    self.name = data['Caller-Unique-ID']
    self.in_queue = Queue.Queue()
    self.in_queue.put(data)
    self.bridge = None
    self.answered = None # DateTime
    self.created = datetime.datetime.now()
    self.times = {'create': None, 'answer': None, 'hungup': None, 'bridge': None, 'unbridge': None}
    self.active = True

  def put(self, data):
    self.in_queue.put(data)

  def print_event(self, event, mask=''):
    return '\n'.join(['%s:%s' % (k, event[k]) for k in sorted(event) if mask.upper() in k.upper() ])+'\n'

  def request_(self, event, fo): # Запрос к https://__port:__port
    r = requests.post('http://127.0.0.1:18001/event', data={'event': json.dumps(event)})
    fo.write('channel request: %s %s\n' % (event[u'Event-Name'], r.reason))
    return r

  def run(self):
    channels[self.name] = self
    #print ('channel %s created...' % self.name)
    with open('events/' + self.name, 'a') as fo:
      while self.active:
        try:
          event = self.in_queue.get(timeout=CHANNEL_LIVE_TIME)
          #print ('channel %s: «%s» %s' % (self.name, event['Event-Name'], self.print_event(event, 'Event-Date-Timestamp')))
          #fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
          if (event['Event-Name'] == 'CHANNEL_HANGUP_COMPLETE'): 
            self.times['hungup'] = datetime.datetime.now()
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
            break
          if   (event['Event-Name'] == 'CHANNEL_ANSWER'):
            self.times['answer'] = datetime.datetime.now()
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_ORIGINATE'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_UUID'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_BRIDGE'):
            self.times['bridge'] = datetime.datetime.now()
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_UNBRIDGE'):
            self.times['unbridge'] = datetime.datetime.now()
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'CALL_UPDATE'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'DTMF'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'RECORD_START'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'RECORD_STOP'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'PLAYBACK_START'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'PLAYBACK_STOP'):
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_EXECUTE'):
            if ('.wav' in event['Application-Data']):
              fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
              self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_EXECUTE_COMPLETE'):
            if event['Application-Response'] != '_none_':
              fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
              self.request_(event, fo)
          elif (event['Event-Name'] == 'CHANNEL_CREATE'):
            self.times['create'] = datetime.datetime.now()
            fo.write('%s:\n%s\n' % (event['Event-Name'], self.print_event(event)))
            self.request_(event, fo)
        except Exception, e:
          #self.active = False
          print ('channel %s\nexception: %s' % (self.name, e))
          fo.write ('%s exception %s:\n%s\n' % (self.name, e, event))
      #print ('channel %s completed...\n%s\n' % (self.name, self.times))
      fo.write ('%s completed...\n%s\n' % (self.name, self.times))
    del channels[self.name]


class events_queue(threading.Thread):
  def __init__(self, queue_in):
    threading.Thread.__init__(self)
    self.qin = queue_in
    self.name = 'events_queue'

  def run(self):
    print ('%s: запущен...' % self.name)
    while 1:
      try:
        event = self.qin.get()
        #print 'events_queue: %s ' % event
        threading.Thread(target=plugins.routes[event['Event-Name']], args=(event, channels, bridges)).start()
      except Exception, e:
        print ('channels.%s exception %s' % (self.name, e))
