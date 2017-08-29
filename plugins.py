#!/usr/bin/python2
# -*- coding: utf-8 -*-

import datetime, time, threading, requests, json
EVENT_URL = 'http://127.0.0.1:18001/event'
def request_(event):
  try:
    #event['_xsrf'] = 'r3S5j6jsRE9PQMHLkSnrRi9Dpiga/CArRRIBt/ahA/18zlovBJUku7A+6S2F+WZu0Mc='
    r = requests.post(EVENT_URL, 
                      data={'event': json.dumps(event)},
                      #headers={'Content-Type': 'application/json'},
                     )
    return r.reason
  except Exception as e:
    print ('plugins.request_ exception: %s' % e)
    return 'ERROR'

def channel_create(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def channel_answer(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def channel_hangup_complete(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def channel_execute(event, channels_, bridges_):
  if ('.wav' in event['Application-Data']):
    r = request_(event) 
    if r != 'OK':
      print (event[u'Event-Name'], r)

def channel_execute_complete(event, channels_, bridges_):
  if event['Application-Response'] != '_none_':
    r = request_(event) 
    if r != 'OK':
      print (event[u'Event-Name'], r)

def channel_bridge(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def channel_unbridge(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def channel_originate(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def channel_uuid(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def client_connected(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def client_disconnected(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def call_update(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def record_start(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def record_stop(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def playback_start(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def playback_stop(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def general(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def dtmf(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def notify(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

def custom(event, channels_, bridges_):
  r = request_(event) 
  if r != 'OK':
    print (event[u'Event-Name'], r)

routes =    { u'CHANNEL_CREATE': channel_create,
              u'CHANNEL_ANSWER': channel_answer,
              u'CHANNEL_HANGUP_COMPLETE': channel_hangup_complete,
              u'CHANNEL_EXECUTE_COMPLETE': channel_execute_complete,
              u'CHANNEL_EXECUTE': channel_execute,
              u'CHANNEL_BRIDGE': channel_bridge,
              u'CHANNEL_UNBRIDGE': channel_unbridge,
              u'CHANNEL_ORIGINATE': channel_originate,
              u'CLIENT_CONNECTED': client_connected,
              u'CLIENT_DISCONNECTED': client_disconnected,
              #u'CALL_UPDATE': call_update,
              u'RECORD_START': record_start,
              u'RECORD_STOP': record_stop,
              u'GENERAL': general,
              u'DTMF': dtmf,
              #u'PLAYBACK_START': playback_start,
              #u'PLAYBACK_STOP': playback_stop,
              #u'CHANNEL_UUID': channel_uuid,
              u'NOTIFY': notify,
              #u'CUSTOM': custom,
              }
fields =     {u'CHANNEL_CREATE': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 #u'Unique-ID',
                                 u'Channel-Call-State',
                                 u'Channel-Call-UUID',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                                 ]),
              u'DTMF':          set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Unique-ID',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4',
                                 u'DTMF-Digit',
                                 u'DTMF-Duration',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                                 ]),
              u'CHANNEL_ANSWER': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 #u'Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4',
                                 #u'Channel-Call-UUID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                                 ]),
              u'CHANNEL_HANGUP_COMPLETE': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 #u'Caller-Channel-Bridged-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4',
                                 u'Hangup-Cause',
                                 #u'Channel-Call-UUID',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                                 ]),
              u'CHANNEL_EXECUTE_COMPLETE': set([
                                 u'Answer-State',
                                 u'Application-Data',
                                 u'Application-Response',
                                 u'Call-Direction',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 #u'Channel-Call-UUID',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                              ]),
              u'CHANNEL_EXECUTE': set([
                                 u'Answer-State',
                                 u'Application-Data',
                                 u'Call-Direction',
                                 u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 #u'Channel-Call-UUID',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                              ]),
              u'CHANNEL_BRIDGE': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Channel-Bridged-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4',
                                 u'Bridge-A-Unique-ID',
                                 u'Bridge-B-Unique-ID',
                                 u'Caller-RDNIS',
                                 #u'Channel-Call-UUID',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                             ]),
              u'CHANNEL_UNBRIDGE': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Channel-Bridged-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4',
                                 u'Bridge-A-Unique-ID',
                                 u'Bridge-B-Unique-ID',
                                 u'Caller-RDNIS',
                                 u'Hangup-Cause',
                                 #u'Channel-Call-UUID',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                                 ]),
              u'CHANNEL_ORIGINATE': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4',
                                 #u'Channel-Call-UUID',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
                                 ]),
              u'CHANNEL_UUID': set([]),
              u'CLIENT_CONNECTED': set([
              ]),
              u'CLIENT_DISCONNECTED': set([
              ]),
              u'CALL_UPDATE': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 u'Channel-Call-UUID',
                                 u'Bridged-To',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
              ]),
              u'RECORD_START': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 #u'Channel-Call-UUID',
                                 u'Record-File-Path',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
              ]),
              u'RECORD_STOP': set([
                                 u'Answer-State',
                                 u'Call-Direction',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Destination-Number',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 #u'Channel-Call-UUID',
                                 u'Record-File-Path',
                                 u'Hangup-Cause'
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
              ]),
              u'PLAYBACK_START': set([
                                 u'Answer-State',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Caller-RDNIS',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 u'Playback-File-Path',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
              ]),
              u'PLAYBACK_STOP': set([
                                 u'Answer-State',
                                 #u'Caller-Caller-ID-Name',
                                 u'Caller-Caller-ID-Number',
                                 #u'Caller-Callee-ID-Name',
                                 u'Caller-Callee-ID-Number',
                                 #u'Caller-Channel-Created-Time',
                                 #u'Caller-Channel-Answered-Time',
                                 u'Caller-Network-Addr',
                                 u'Caller-Unique-ID',
                                 u'Caller-RDNIS',
                                 u'Channel-Call-State',
                                 u'Event-Date-Timestamp',
                                 u'Event-Name',
                                 u'Event-Sequence',
                                 #u'FreeSWITCH-IPv4'
                                 u'Playback-File-Path',
                                 u'Playback-Status',
                                 #u'Unique-ID',
                                 #u'variable_sip_from_host',
                                 u'variable_sip_gateway_name',
              ]),
              u'GENERAL': set([]),
              u'NOTIFY': set([]),
              u'CUSTOM': set([])
              }

