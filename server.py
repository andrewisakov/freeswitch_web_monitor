#!/usr/bin/python3
import tornado.ioloop, tornado.escape, logging, os.path, uuid
import tornado.web, tornado.websocket

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

define('port', default=8989, help="Выбрать порт", type=int)
define('debug', default=False, help="Отладка")

class MessageBuffer(object):
  def __init__(self):
    self.waiters = set()
    self.cache = []
    self.cache_size = 1024

  def wait_for_message(self, cursor=None):
    result_future = Future()
    if cursor:
      new_count = 0
      for msg in reversed(self.cach):
        if msg['id'] == cursor:
          break
        new_count += 1
      if new_count:
        result_future.set_result(self.cache[-new_count:])
        return result_future
    self.waiters.add(result_future)
    return result_future
  
  def cancel_wait(self, future):
    self.waiters.remove(future)
    future.set_result([])

  def new_messages(self, messages):
    logging.info('Отправка сообщения %r слушателям', len(self.waiters))
    for fututre in self.waiters:
      future.set_result(messages)
    self.waiters = set()
    self.cache.extend(messages)
    if len(self.cache) > self.cache_size:
      self.cache = self.cache[-self.cache_size:]

global_message_buffer = MessageBuffer()

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('index.html', messages=global_message_buffer.cache)

class EventNewHandler(tornado.web.RequestHandler):
  def post(self):
    message = { 'id': str(uuid.uuid4()), 'body': self.get_argument('body'), }
    message['html'] = tornado.escape.to_basestring(
      self.render_string('message.html', message=message))
    if self.get_argument('next', None):
      self.redirect(self.get_argument('next'))
    else:
      self.write(message)
    glibal_message_buffer.new_messages([message])

ws_clients = {}

class WSHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    ws_clients[self] = self
  def on_message(self, message):
    pass
  def on_close(self):
    del ws_clients[self]

def main():
  parse_command_line()
  app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ws", WSHandler,
    (r"/event/", EventNewHandler),
    #(r"/a/event/updates", EventUpdatesHandler), ],
    cookie_secret = 'ErBiVZv+5OZBxMk3w/Gt2iQzlNOljfdVLJMN8czhM6ETBDw/tVsdh2jZNPWPtTdgyq0=',
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path   = os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies  = True,
    debug         = options.debug,
  )
  app.listen(options.port)
  tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
  main()
  