#!/usr/bin/python2
# -*- coding: utf-8 -*-

import datetime, time, socket, threading, ESL, Queue, json, urllib
import plugins
import channels
from multiprocessing import Process, Queue as mpQueue
#from collections import deque as queue

ESL_SERVER = ('192.168.222.20', 8021)
ESL_PASSWD = 'ClueCon'
SO_SOCKETS = 1024
SO_BUFFER = 1024
caller_queue = {}
events = plugins.routes
time_delta = None

def EventWork(mpq, thq):
  while 1:
    try:
      event = mpq.get()
      shift_time = event[1] # Время внутри FS убегает...
      event = json.loads(urllib.unquote(event[0]).decode('utf-8'))
      event_ = {}
      """
      if event[u'Event-Name'] == 'CHANNEL_CREATE':
        for e in sorted(event):
          print '%s: %s' % (e, event[e])
      """
      if event[u'Event-Name'] in plugins.routes:
        event_fields = set(sorted(event)) & plugins.fields[event[u'Event-Name']]
        #print (event[u'Event-Name'], sorted(event_fields))
        for k in event_fields:
          if 'TIME' in k.upper():
            try:
              ev_time = int(event[k])
              if ev_time > 0:
                msec = int(event[k][-6:])
                event[k] = str(datetime.datetime.strptime(datetime.datetime.fromtimestamp(int(event[k][:-6])).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')+datetime.timedelta(microseconds=msec)-shift_time)
            except Exception, e:
              pass
          event_[k] = event[k]
        thq.put(event_)
      else:
        pass
        #event_ = event.copy()

    except Exception, e:
      print '\nEventWork exception:%s\n' % e
      print '\nEventWork exception:%s\n' % '\n'.join(['%s: %s' % (ev, event[ev]) for ev in sorted(event)])
      pass

def esl_work(mpq):
  print 'esl_work: started...'
  con = ESL.ESLconnection(ESL_SERVER[0], ESL_SERVER[1], ESL_PASSWD)
  if con.connected:
    c = con.api('strftime')
    #print c.serialize()
    c = datetime.datetime.strptime(c.serialize().split('\n')[-1:][0], '%Y-%m-%d %H:%M:%S')
    #print c, datetime.datetime.now()
    c -= datetime.datetime.now()
    con.events('json', 'all')
    n = 0
    #print 'Started on %s' % self.event
    while 1:
      ev = con.recvEvent()
      if ev:
        #print 'esl_work: %s' % ev
        mpq.put([ev.serialize('json'), c])
        #threading.Thread(target=EventWork, args=(ev, self.queue_, n, c)).start()
      n += 1


def main():
  thq = Queue.Queue()
  mpq = mpQueue()
  channels.events_queue(thq, ).start()
  threading.Thread(target=EventWork, args=(mpq, thq)).start()
  Process(target=esl_work, args=(mpq,)).start()

if __name__ == '__main__':
  main()
