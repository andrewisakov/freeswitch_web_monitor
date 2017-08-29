#!/usr/bin/python2
# -*- coding: utf-8 -*-
import ESL, threading, Queue, cPickle as pickle, xmltodict, urllib, json, datetime, socket
events = {
#'CHANNEL_CALLSTATE': (),
'CHANNEL_CREATE': ('Caller-Destination-Number',
                   'Answer-State',
                   'Caller-Caller-ID-Name',
                   'Event-Date-Timestamp',
                   'Event-Name',
                   'Event-Date-Local',
                   'Caller-Unique-ID',
                   'Call-Direction',
                   'Caller-Caller-ID-Number',
                   'Caller-Destination-Number',
                   'Caller-Network-Addr,'),
#'CHANNEL_DESTROY': (),
#'CHANNEL_STATE': (),
'CHANNEL_ANSWER': ('Answer-State', 
                   'Call-Direction',
                   'Caller-Caller-ID-Name',
                   'Event-Date-Timestamp',
                   'Caller-Caller-ID-Number',
                   'Caller-Callee-ID-Number',
                   'Caller-Unique-ID',
                   'Caller-Destination-Number',
                   'Event-Name',
                   'Event-Date-Local',
                   'Caller-Network-Addr',
                   ),
#'CHANNEL_HANGUP': (),
'CHANNEL_HANGUP_COMPLETE': ('Answer-State',
                            'Call-Direction',
                            'Caller-Caller-ID-Name',
                            'Event-Date-Timestamp',
                            'Event-Name',
                            'Caller-Callee-ID-Number',
                            'Caller-Caller-ID-Number',
                            'Caller-Unique-ID',
                            'Event-Date-Local',
                            'Hangup-Cause',
                            'Caller-Network-Addr'),
'CHANNEL_EXECUTE': (),
'CHANNEL_EXECUTE_COMPLETE': ('Event-Name',
                             'Caller-Callee-ID-Number',
                             'Caller-Caller-ID-Number',
                             'Caller-Unique-ID',
                             'Caller-Caller-ID-Name',
                             'Event-Date-Timestamp',
                             'Caller-Network-Addr',
                             'Event-Date-Local',
                             'Application',
                             'Application-Data',
                             'Application-Response',
                             'Application-UUID',
                             'Answer-State',
                             'Call-Direction',
                             
                             ),
'CHANNEL_BRIDGE': ('Event-Name',
                   'Answer-State',
                   'Bridge-A-Unique-ID',
                   'Bridge-B-Unique-ID',
                   'Caller-Callee-ID-Number',
                   'Caller-Caller-ID-Name',
                   'Event-Date-Timestamp',
                   'Caller-Caller-ID-Number',
                   'Caller-Unique-ID',
                   'Event-Date-Local',
                   'Other-Leg-Callee-ID-Number',
                   'Other-Leg-Caller-ID-Number',
                   'Caller-Network-Addr',
                   ),
'CHANNEL_UNBRIDGE': ('Answer-State', 
                     'Event-Name',
                     'Bridge-A-Unique-ID', 
                     'Bridge-B-Unique-ID', 
                     'Caller-Callee-ID-Number', 
                     'Caller-Caller-ID-Number', 
                     'Caller-Caller-ID-Name',
                     'Event-Date-Timestamp',
                     'Caller-Direction',
                     'Caller-Destination-Number',
                     'Caller-Network-Addr',
                     'Caller-Unique-ID',
                     'Event-Date-Local',
                     'Hangup-Cause'),
#'CHANNEL_PROGRESS': (),
#'CHANNEL_PROGRESS_MEDIA': (),
#'CHANNEL_OUTGOING': (),
#'CHANNEL_PARK': (),
#'CHANNEL_UNPARK': (),
#'CHANNEL_APPLICATION': (),
#'CHANNEL_HOLD': (),
#'CHANNEL_UNHOLD': (),
'CHANNEL_ORIGINATE': (),
'CHANNEL_UUID': (),

}

qq = Queue.Queue()

def send_event(event):
  #event = urllib.unquote(event.serialize())
  data = pickle.dumps(event) #.encode('utf-8')
  #print (data)
  success = False
  n = 10
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect(('192.168.222.219', 7755))
    try:
      s.sendall(data)
      success = True
    except Exception, e:
      print 'send_event send exception: %s ' % e
  except Exception, e:
    print 'send_event connect exception: %s ' % e
  finally:
    s.close()


class QueueWork(threading.Thread):
  def __init__(self, queue_in):
    threading.Thread.__init__(self)
    self.queue_in = qq

  def run(self):
    n = 1000
    #evo = open('fs_events.txt', 'w')
    while 1:
      try:
        event = self.queue_in.get(timeout=30)
        print event[u'Event-Name'], n
        if event[u'Event-Name'] in events:
          #print event
          threading.Thread(target=send_event, args=(event,)).start()
        #evo.write(event[u'Event-Name'])
        #evo.write('\n')
        #for k in sorted(event.keys()):
          #evo.write('%s; %s\n' % (k, event[k]))
          #print '\t%s: %s' % (k, event[k])
        #evo.write('\n')
      except Exception, e:
        print 'QueueWork: %s' % e
        n = 1
      n -= 1
    #evo.close()

def EventWork(event, queue_in, n):
  try:
    event = urllib.unquote(event.serialize()).decode().split('\n')
    ev = {}
    for evl in event:
      if evl:
        #print el
        evd = evl.split(': ')
        #print evd, 
        if (len(evd) > 1):
          ev[evd[0]] = evd[1]
          #last_key = evd[0]
    #print (ev)
    msec = int(ev[u'Event-Date-Timestamp'][-6:])
    #ev[u'Event-Date-Timestamp'] = datetime.datetime.fromtimestamp(int(ev[u'Event-Date-Timestamp'][:-6])).strftime('%Y-%m-%d %H:%M:%S') + '.' + ev[u'Event-Date-Timestamp'][-6:]
    ev[u'Event-Date-Timestamp'] = '%s' % datetime.datetime.now()
    if ev[u'Event-Name'] in events:
      #queue_in.put({ k: ev[k] for k in ev if k in events[ev[u'Event-Name']] })
      queue_in.put({ k: ev[k] for k in ev if '-' in k })
  except Exception, e:
    print 'EventWork: %s, %s, %s' % (e, event, n)
    pass

def esl_work(event, qq):
  con = ESL.ESLconnection('192.168.222.20', '8021', 'ClueCon')
  if con.connected:
    con.events('plain', event)

    n = 0
    print 'Started on %s' % event
    while 1:
      ev = con.recvEvent()
      if ev:
        threading.Thread(target=EventWork, args=(ev, qq, n)).start()
      n += 1

if __name__ == '__main__':
  qw = QueueWork(qq)
  qw.start()
  for e in events:
    threading.Thread(target=esl_work, args=(e, qq)).start()
  