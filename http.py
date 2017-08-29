#!/usr/bin/python2
# -*- coding: utf-8 -*-
import web, devices as devices_, esl

urls = (
    '/devices', 'list_devices',
    '/device/(.*)', 'get_device',
    '/channel/(.*)', 'get_channel',
)

app = web.application(urls, globals())
devices = devices_.Devices()

class list_devices:
  def GET(self):
    global devices 
    devices = devices_.Devices()
    #print devices.devices
    output = ''
    for device in devices.devices:
      #print device
      output += str(devices.devices[device].params()) + '\n\n' # + ': ' + devices.devices[device].channels
    output += ']';
    return output
    #del devices

class get_device:
  def GET(self, device_id):
    global devices
    devices = devices_.Devices()
    channels = devices.select(int(device_id)).params()
    return str(channels)

class get_channel:
  def GET(self, phone):
    global devices
    devices = devices_.Devices()
    return str(devices.channel(phone).params())

if __name__ == "__main__":
    esl.main()
    app.run()
