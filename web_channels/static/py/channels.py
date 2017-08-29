from browser import document as doc, websocket, console, window, html, alert
import json


def set_counters(data):
    counters = doc.getElementById('%s.0' % data['trunk_name'])
    counters = counters.getElementsByClassName('counters')[0]  # Счётчики
    # print ('set_counters: %s' % counters)
    cn = data['counters']
    html_ = '<div class="total">%s</div>' % cn['total']
    html_ += '<div class="answered">%s</div>' % cn['answered']
    html_ += '<div class="rejected">%s</div>' % cn['rejected']
    counters.innerHTML = html_


def channel_create(data):  # Создание звонка
    # print (data['event_name'], data)
    set_counters(data)
    call_trace = doc.getElementById('%s.%s' % (data['trunk_name'], data['virtual_line']))
    call_trace = call_trace.getElementsByClassName('call-trace')[0]  # Линия
    if data['direction'] == 'inbound':
        html_ = '<div class="caller-id-number" style="width:%s;">%s</div>' % (
            data['caller_width'], data['caller_id_number'])
    else:
        if 'caller_id_number' in data:  # Подбор оператора
            html_ = '<div class="caller-id-number" style="color:darkgray;width:%s;">%s</div>' % (
                data['caller_width'], data['caller_id_number'])
            html_ += '<div class="callee-id-number" style="color:black;background:darkgray;width:%s;">%s</div>' % (data[
                                                                                                                                             'callee_width'], data['callee_id_number'])
        else:  # Отзвон
            html_ = '<div class="callee-id-number" style="color:darkgray;background:white;width:%s;">%s</div>' % (
                data['callee_width'], data['callee_id_number'])
    html_ += '<div class="event-datetime">%s</div>' % data['event_timestamp']
    call_trace.innerHTML = html_


def channel_answer(data):  # Ответ
    # print (data['event_name'], data)
    set_counters(data)
    call_trace = doc.getElementById('%s.%s' % (data['trunk_name'], data[
                                    'virtual_line'])).getElementsByClassName('call-trace')[0]  # Линия
    #print ('channel_answer 0', data['event_name'], data, call_trace.innerHTML)
    #html_ = ''
    if data['direction'] == 'inbound':
        html_ = '<div class="caller-id-number">%s</div>' % data['caller_id_number']
    else:
        html_ = ''
        if 'caller_id_number' in data:
            html_ = '<div class="caller-id-number" style="color:green;width:%s;">%s</div>' % (
                data['caller_width'], data['caller_id_number'])
        html_ += '<div class="callee-id-number" style="color:green;background:#ddffdd;width:%s;font-size=9px;">%s</div>' % (
            data['callee_width'], data['callee_id_number'])
        html_ += '<div class="callee-timer" style="padding-top:2px;text-align:right;color:white;background:green;width:12px;font-size:9px;height:12px;">%s</div>' % data[
            'answer_wait']
    html_ += '<div class="event-datetime">%s</div>' % data['event_timestamp']
    call_trace.innerHTML = html_


def channel_hangup_complete(data):
    #print (data['event_name'], data)
    set_counters(data)
    call_trace = doc.getElementById('%s.%s' % (data['trunk_name'], data[
                                    'virtual_line'])).getElementsByClassName('call-trace')[0]  # Линия
    if data['direction'] == 'outbound':
        html_ = ''
        if 'caller_id_number' in data:  # Это был не отзвон
            html_ = '<div class="caller-id-number" style="color:green;width:%s;">%s</div>' % (
                data['caller_width'], data['caller_id_number'])
        if data['duration'] > 0:  # Отвчен
            html_ += '<div class="callee-id-number" style="color:green;background:#ddffdd;width:%s;font-size:9px;">%s</div>' % (
                data['callee_width'], data['callee_id_number'])
            html_ += '<div class="callee-timer" style="padding-top:2px;text-align:right;color:white;background:green;width:28px;font-size:9px;">%s+%s</div>' % (data[
                                                                                                                                  'answer_wait'], data['duration'])
        else:
            html_ += '<div class="callee-id-number" style="color:red;background:#ffdddd;width:%s;font-size=9px;">%s</div>' % (
                data['callee_width'], data['callee_id_number'])
            html_ += '<div class="callee-timer" style="padding-top:2px;text-align:right;color:white;background:red;width:12px;font-size:9px;">%s</div>' % data[
                'answer_wait']
    if data['hangup_cause'] == 'NO_USER_RESPONSE':
        html_ += '<div class="hangup-cause">%s</div>' % data['hangup_cause']
    # Результат отметить тут
    html_ += '<div class="event-datetime">%s</div>' % data['event_timestamp']
    call_trace.innerHTML = html_


def channel_execute_complete(data):
    print(data['event_name'], data)
    if data['application_data'][0]:
        call_trace = doc.getElementById('%s.%s' % (data['trunk_name'], data[
                                        'virtual_line'])).getElementsByClassName('call-trace')[0]  # Линия
        html_ = call_trace.innerHTML
        if 'application-data' in html_:
            html_ = html_.split('<div class="application-data"')[0]
        app_style = 'color:green;' if data[
            'application_data'] == 'FILE PLAYED' else 'color:red;'
        html_ += '<div class="application-data" style="%s">%s</div>' % (
            app_style, data['application_data'][0])
        html_ += '<div class="event-datetime">%s</div>' % data['event_timestamp']
        call_trace.innerHTML = html_


def channel_execute(data):
    #print (data['event_name'], data)
    if data['application_data'][0]:
        call_trace = doc.getElementById('%s.%s' % (data['trunk_name'], data[
                                        'virtual_line'])).getElementsByClassName('call-trace')[0]  # Линия
        html_ = call_trace.innerHTML
        if 'application-data' in html_:
            html_ = html_.split('<div class="application-data"')[0]
        if 'application_response' in data:
            app_style = 'color:green;' if data[
                'application_response'] == 'FILE PLAYED' else 'color:red;'
        else:
            app_style = ''
        html_ += '<div class="application-data" style="%s">%s</div>' % (
            app_style, data['application_data'][0])
        html_ += '<div class="event-datetime">%s</div>' % data['event_timestamp']
        call_trace.innerHTML = html_


def channel_bridge(data):
    print(data['event_name'], data)


def channel_unbridge(data):
    print(data['event_name'], data)


def channel_originate(data):
    print(data['event_name'], data)


def record_start(data):
    print(data['event_name'], data)


def record_stop(data):
    print(data['event_name'], data)


def dtmf(data):
    print(data['event_name'], data)

events = {'CHANNEL_CREATE': channel_create,
          'CHANNEL_ANSWER': channel_answer,
          'CHANNEL_HANGUP_COMPLETE': channel_hangup_complete,
          'CHANNEL_EXECUTE_COMPLETE': channel_execute,
          'CHANNEL_EXECUTE': channel_execute,
        #   #           'CHANNEL_BRIDGE'          : channel_bridge,
        #   #           'CHANNEL_UNBRIDGE'        : channel_unbridge,
        #   #           'CHANNEL_ORIGINATE'       : channel_originate,
        #   #           'RECORD_START'            : record_start,
        #   #           'RECORD_STOP'             : record_stop,
        #   #           'DTMF'                    : dtmf,
          }


def send(data):
    console.log('sending %s' % data)
    ws.send(data)


def on_open(ev):
    console.log("Сокет подключен...")


def on_message(ev):
    try:
        data = json.loads(ev.data)
        if data['event_name'] in events:
            # data['direction'] = ['inbound', 'outbound', 'sms'][data['direction']]
            events[data['event_name']](data)
    except Exception as e:
        print('on_message exception', e, ev.data)


def on_close(ev):
    console.log("Сокет отвалился...")
    #alert("Сокет отвалился...")
    _open()


def on_error(ev):
    console.log("Ошибка %s на сокете..." % ev)

ws = None


def _open(ev=None):
    if not websocket.supported:
        alert("WebSockets not supported...")
        return
    global ws
    l = window.location
    server_uri = "wss://" if l.protocol == "https:" else "ws://" + \
        l.hostname + ":" + l.port + "/ws"
    ws = websocket.WebSocket(server_uri)
    ws.bind('open', on_open)
    ws.bind('message', on_message)
    ws.bind('close', on_close)
    ws.bind('error', on_error)

_open()
