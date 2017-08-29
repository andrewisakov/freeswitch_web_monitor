#!/usr/bin/python3
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.options import define, options
from tornado.queues import Queue
from tornado.locks import Semaphore
import os
import json
import trunks
# from datetime import datetime
from tornado.concurrent import run_on_executor
import concurrent.futures
import channels as channels_
import datetime
import channel_events
import psycopg2 as pg2


define("port", default=18001, help="run on the given port", type=int)
smf = Semaphore()
clients = []
ws_queue = Queue()
events_queue = Queue()
devices = channels_.Devices()
channels = channels_.Channels(ws_queue)

"""
 {'channel_number': {'caller_id_number': 
                       {'<line>/0': {''
                                    }
                     'answered': 0,
                     'rejected': 0,
                     'incoming': 0,
                     'period': (from_datetime, last_datetime) }
"""

settings = {
    "cookie_secret": "r3S5j6jsRE9PQMHLkSnrRi9Dpiga/CArRRIBt/ahA/18zlovBJUku7A+6S2F+WZu0Mc=",
    "login_url": "/login",
    "xsrf_cookies": True,
    'debug': True,
    'autoreload': True,
    'compiled_template_cache': False,
    'serve_traceback': True,
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'archive_path': os.path.join(os.path.dirname(__file__), 'static'),
}


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self, executor):
        self.executor = executor
        # self.db = pg2.connect('host=127.0.0.1 port=15432 dbname=freeswitch_trunks user=freeswitch password=freeswitch')

    # def on_finish(self):
    #     self.db.close()


class TrunksHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        pass


class EventHandler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def _save_event(self, data):
        # print('EventHandler._save_data: %s' % data)
        with pg2.connect('host=192.168.222.20 port=5432 dbname=freeswitch_trunks user=freeswitch password=freeswitch') as db:
            insert_ = (data['virtual_line'], data['event_name'], data['direction'], data['uuid'], data['event_time'], data['channel_id'],)
            INSERT = 'insert into line_events (virtual_line, event_name, direction, uuid, event_time, channel_id'
            values_ = '%s, %s, %s, %s, %s, %s'
            for v in ['destination', 'caller_id_number', 'callee_id_number', 'gateway_name', 'hangup_cause', 'application_data', 'application_response']:
                if v in data:
                    values_ += ', %s'
                    INSERT += ', %s' % v
                    insert_+= (data[v],)
            INSERT += ') values (%s)' % values_
            try:
                # print (INSERT, insert_)
                c = db.cursor()
                c.execute(INSERT, insert_)
                db.commit()
                c.close()
            except Exception as e:
                print ('EventHandler._save_event(%s) exception %s' % (data, e))
        gen.Return(None)

    """
  CALL_REJECTED
  NETWORK_OUT_OF_ORDER
  NO_ANSWER
  NORMAL_CLEARING
  NORMAL_TEMPORARY_FAILURE
  NORMAL_UNSPECIFIED
  NO_USER_RESPONSE
  ORIGINATOR_CANCEL
  USER_BUSY
  """

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        event = json.loads(self.get_argument('event'))
        self.set_status(200, 'OK')
        send_sockets = True
        if event['Event-Name'] in channel_events.events:
            # print ('form freeswitch', event)
            event = yield channel_events.events[event['Event-Name']](event)
            # print ('to websocket', event)
            if event and send_sockets:
                for w in clients:
                    try:
                        w.write_message(json.dumps(event))
                    except:
                        pass

            if event:
                # print ('EventHandler.post before _save_event: %s' % event)
                event['direction'] = {'inbound': 0, 'outbound': 1}[event['direction']]
                try:
                    yield self._save_event(event)
                except Exception as e:
                    print ('EventHandler.post exception 2 %s' % e)

class DevicesHandler(BaseHandler):

    def get(self):
        global devices
        devices_ = channels_.Devices()
        devices = devices_
        #print (devices.channels)
        self.render("html/devices.html",
                    title='Обзор по устройствам', devices=devices)

class TimeLineHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        self.render("html/operators_time.html", title="Машина Времени", )


class ChannelsHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        yield trunks._read_trunks()
        # for trg in trunks.trunks_groups:
        #     for tr in trunks.trunks_groups[trg]:
        #         print (trg, trunks.trunks[tr])
        # print (trunks.trunks)
        # print (trunks.trunks_groups)
        self.render("html/channels.html", title="Каналы", trunks=trunks.trunks, trunks_groups=trunks.trunks_groups)


class MainHandler(BaseHandler):

    def get(self):
        self.redirect("/channels_view")


class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        clients.append(self)
        print('client %s connected...' % self)
        #self.write_message(json.dumps({'data': 'data_1'}))
        #print (self)

    def on_message(self, message):
        print('%s: %s' % (self, message))

    def close(self):
        print('client %s disconnected...' % self)
        del clients[self]


class ChannelSelectHandler(BaseHandler):
    #@tornado.web.asynchronous

    @gen.coroutine
    def get(self, phone):
        channel = devices.select_channel(phone)
        print(channel)
        self.write('%s:%s' % (channel.__device__.id, channel.id))
        # self.write("channel")


def main():
    global trunks
    global devices
    tornado.options.parse_command_line()
    executor = concurrent.futures.ThreadPoolExecutor()
    application = tornado.web.Application([
        (r'/static/(.*)', tornado.web.StaticFileHandler,
         dict(path=settings['static_path'])),
        (r"/", MainHandler, dict(executor=executor)),
        (r"/channels_view", ChannelsHandler, dict(executor=executor)),
        (r"/devices_view", DevicesHandler, dict(executor=executor)),
        (r"/event", EventHandler, dict(executor=executor)),
        (r"/ws", WSHandler,),
        (r'/tunks', TrunksHandler, dict(executor=executor)),
        (r"/channel/([^/]+)", ChannelSelectHandler, dict(executor=executor)),
        (r'/time_line', TimeLineHandler, dict(executor=executor)),
    ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    # Загрузить данные
    """
    with open('channel_events.json', 'a') as j:
      channel_events = json.load(j, object_hook=datetime_loads)
    if (channel_events['actual'] > datetime.datetime.now()): # Протухло...
      channel_events = {}
    with open('inbounds.json', 'a') as j:
      inbounds = json.load(j, object_hook=datetime_loads)
    if inbounds['actual'] > datetime.datetime.now(): # Протухло...
      inbounds = {}
    """
    main()
