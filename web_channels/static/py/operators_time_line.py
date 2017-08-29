import json
import time
import datetime

from browser import document as DOM
from browser import alert, console, html, timer, websocket, window

SCALE = 1
CANVAS = {} # {operator_id: Canvas_instance, }
NOANSWER = {}

class Noanswered:
    def __init__(self, data):
        NOANSWER[data['caller_id_number']] = self
        self.event_time = data['event_time'].split('.')[0]
        self.caller_id = data['caller_id_number']
        self.operator_id = data['callee_id_number']
        self.to_delete = False
        answer_wait = int(data['answer_wait'])
        noanswer_brick = html.DIV(Class="noanswered-brick",
                                  title='{}\n{}'.format(self.event_time, 
                                  '\n'.join([oi + ': ' + ('Занят' if c.busy else 'Свободен') for oi, c in CANVAS.items()])),
                                  style={'width': (answer_wait if answer_wait > 0 else 1), 'margin-right': 0,})
        # noanswer_brick.title += '\nОжидание'
        noanswer_canvas = html.DIV(Class="noanswered-canvas", Id="noanswered_canvas."+self.caller_id)
        noanswer_canvas <= noanswer_brick

        noanswer_wait = html.DIV(data['answer_wait'], Class="noanswered-wait")
        noanswer_phone = html.DIV(data['caller_id_number'], Class="noanswered-phone")
        noanswer_operator = html.DIV(data['callee_id_number'], Class="noanswered-operator")
        noanswer_info = html.DIV(Class="noanswered-info")
        noanswer_info <= noanswer_operator
        noanswer_info <= noanswer_wait
        noanswer_info <= noanswer_phone

        noanswer_row = html.DIV(Class="noanswered-row", Id=self.caller_id)

        noanswer_row <= noanswer_canvas
        noanswer_row <= noanswer_info

        DOM.getElementById('noanswered_calls') <= noanswer_row

        self.answer_wait = int(data['answer_wait'])
        DOM.getElementById('score_noanswered').text = str(int(DOM.getElementById('score_noanswered').text)+1)
        DOM.getElementById('score_noanswered.'+self.operator_id).text = str(int(DOM.getElementById('score_noanswered.'+self.operator_id).text)+1)

    # def __del__(self):
    #     # del NOANSWER[self.caller_id]
    #     print('Noanswered.__del__', self.caller_id)
    #     # canvas = DOM.getElementById("noanswered_canvas."+self.caller_id)
    #     DOM.getElementById('noanswered_calls').removeChild(DOM.getElementById(self.caller_id))

    @property
    def width(self):
        canvas = DOM.getElementById("noanswered_canvas."+self.caller_id)
        calls = canvas.getElementsByClassName("noanswered-brick")
        return sum([int(c.style.width.replace('px', ''))+int(c.style.marginRight.replace('px', '')) for c in calls])

    def __timer__(self):
        global SCALE
        canvas = DOM.getElementById("noanswered_canvas."+self.caller_id)
        calls = canvas.getElementsByClassName("noanswered-brick")
        if len(calls) > 0:
            if self.width+SCALE > canvas.clientWidth:
                new_call_width = int(calls[0].style.width.replace('px', '')) - SCALE
                new_call_margin = int(calls[0].style.marginRight.replace('px', '')) + SCALE
                if new_call_width > 0:
                    calls[0].style.width = str(new_call_width)+'px'
                    calls[0].style.marginRight = str(new_call_margin)+'px'
                else:
                    if 'blue' not in calls[0].style['background-color']:
                        DOM.getElementById('score_noanswered').innerHTML = str(int(DOM.getElementById('score_noanswered').innerHTML)-1)
                    canvas.removeChild(calls[0])
                    self.to_delete = (self.width == 0)

                    # DOM.getElementById('score_noanswered.'+self.operator_id).text = str(int(DOM.getElementById('score_noanswered.'+self.operator_id).text)-1)
            else:
                calls[0].style.marginRight = str(int(calls[0].style.marginRight.replace('px', '')) + SCALE) + 'px'
                # self.width += SCALE

class Canvas:
    def __init__(self, operator_id):
        CANVAS[operator_id] = self
        self.busy = False
        self.to_delete = False
        self.queue = []
        self.duration = 0
        self.operator_id = operator_id
        operator_row = html.DIV(Class="operator-row", Id=operator_id)
        operator_canvas = html.DIV(Class="operator-canvas", Id="canvas."+operator_id)
        operator_info = html.DIV(Class="operator-info", Id="operator."+operator_id)
        operator_name = html.DIV(operator_id, Class="operator-name")
        # operator_width = html.DIV(Class="operator-width", Id="width."+operator_id)
        answered_wait = html.DIV(Class="answered-wait", Id="answered_wait."+self.operator_id)
        answered_duration = html.DIV(Class="answered-duration", Id="answered_duration."+self.operator_id)
        answered_phone = html.DIV(Class="answered-phone", Id="answered_phone."+self.operator_id)
        operator_answered = html.DIV('0', Class="operator-score-answered",
                                     Id="score_answered." + operator_id)
        operator_noanswered = html.DIV('0', Class="operator-score-noanswered", 
                                       Id="score_noanswered." + operator_id)
        operator_info <= operator_name
        # operator_info <= operator_width
        operator_info <= operator_answered
        operator_info <= answered_wait
        operator_info <= answered_duration
        operator_info <= answered_phone
        operator_info <= operator_noanswered
        operator_row <= operator_canvas
        operator_row <= operator_info
        content = DOM.getElementById('content')
        content <= operator_row


    @property
    def width(self):
        canvas = DOM.getElementById('canvas.{}'.format(self.operator_id))
        calls = canvas.getElementsByClassName('call-brick')
        return sum([int(c.style.width.replace('px', ''))+int(c.style.marginRight.replace('px', '')) for c in calls])

    # def __del__(self): # Не реализовано в brython :( Но, если быть точным, не реализовано в JS :)
    #     print('Canvas.__del__', self.operator_id)
    #     DOM.getElementById('content').removeChild(DOM.getElementById(self.operator_id))

    def __timer__(self):
        # _started = time.time()
        global SCALE
        canvas = DOM.getElementById('canvas.{}'.format(self.operator_id))
        # if data['event_name'] == 'CHANNEL_CREATE'
        if self.width+SCALE > canvas.clientWidth:
            calls = canvas.getElementsByClassName('call-brick') # + canvas.getElementsByClassName('call-brick-outbound')
            if len(calls) > 0:
                call_width_future = int(calls[0].style.width.replace('px', ''))-SCALE
                # call_margin = int(calls[0].style.marginRight.replace('px', ''))
                if call_width_future <= 0:
                    # try:
                    #     background_color = calls[0].style['background-color']
                    # except:
                    #     background_color = 'green'
                    # self.width -= (call_width_future+call_margin+_scale)
                    # print ('{}.__timer__ {}'.format(self.operator_id, background_color))
                    if 'blue' not in calls[0].style['background-color']:
                        score_answered = DOM.getElementById('score_answered')
                        score_answered.innerHTML = str(int(score_answered.innerHTML)-1)
                        # if len(canvas.getElementsByClassName('call-brick')) > 0:
                        operator_score_answered = DOM.getElementById('score_answered.'+self.operator_id)
                        operator_score_answered.innerHTML = str(int(operator_score_answered.innerHTML)-1)
                    canvas.removeChild(calls[0])
                    self.to_delete = (self.width == 0)
                else:
                    calls[0].style.width = '{}px'.format(call_width_future)

        if self.queue:
            while self.queue:
                calls = canvas.getElementsByClassName('call-brick') #+canvas.getElementsByClassName('call-brick-outbound')
                ev = self.queue.pop(0)
                print(ev)

                if (ev['event_name'] == 'CHANNEL_CREATE') and ('title' in ev):
                    self.busy = True
                    new_call = html.DIV(Class='call-brick', style=ev['style'], title=ev['title'], )
                    canvas <= new_call

                elif (ev['event_name'] == 'CHANNEL_ANSWER'):
                    self.busy = True
                    if ('title' in ev): # Исходящий ответили
                        new_call = html.DIV(Class='call-brick', style=ev['style'], title=ev['title'])
                    else: # Входящий, ответили
                        new_call = html.DIV(Class='call-brick', style={'width': SCALE, 'margin': 0,},
                                            title='{} -> {}\n{}'.format(ev['caller_id_number'],
                                            ev['trunk_name'], ev['event_timestamp']))
                        answered_phone = DOM.getElementById('answered_phone.'+self.operator_id)
                        answered_phone.innerHTML = ev['caller_id_number']
                        answered_phone.title = ev['trunk_name']
                        answered_wait = DOM.getElementById('answered_wait.'+self.operator_id)
                        answered_wait.innerHTML = ev['answer_wait']
                        background_color = 'red' if int(ev['answer_wait']) > 5 else 'green'
                        answered_wait.style.backgroundColor = background_color
                        DOM.getElementById('answered_duration.'+self.operator_id).innerHTML = '0'
                        self.duration = 1
                    new_call.title += '\nОжидание: {}'.format(ev['answer_wait'])
                    canvas <= new_call

                elif (ev['event_name'] == 'CHANNEL_HANGUP_COMPLETE'):
                    self.busy = False
                    self.duration = 0
                    if len(calls) > 0:
                        call_margin = int(calls[-1].style.marginRight.replace('px', ''))
                        calls[-1].style.marginRight = str(call_margin+SCALE)+'px'
                        calls[-1].title += '\n{} сек'.format(ev['event_timestamp'])

                        if ev['hangup_cause'] in ('NORMAL_CLEARING', 'NETWORK_OUT_OF_ORDER'):
                            if 'blue' not in calls[-1].style['background-color']:
                                score_answered = DOM.getElementById('score_answered')
                                score_answered.innerHTML = str(int(score_answered.innerHTML)+1)
                                score_answered = DOM.getElementById('score_answered.'+self.operator_id)
                                score_answered.innerHTML = str(int(score_answered.innerHTML)+1)
                            calls[-1].title += '\nДлительность: {} сек'.format(ev['duration'])

                        # if ev['hangup_cause'] == 'NO_ANSWER':
                        #     DOM.getElementById('score_noanswered').text = str(int(DOM.getElementById('score_noanswered').text)+1)
                        #     DOM.getElementById('score_noanswered.'+self.operator_id).text = str(int(DOM.getElementById('score_noanswered.'+self.operator_id).text)+1)
                        #     # DOM.getElementById('noanswered-calls')

        else:
            calls = canvas.getElementsByClassName('call-brick')
            if len(calls) > 0:
                call_margin = int(calls[-1].style.marginRight.replace('px', ''))
                call_width = int(calls[-1].style.width.replace('px', ''))
                if call_margin > 0:
                    calls[-1].style.marginRight = '{}px'.format(call_margin+SCALE)
                else:
                    calls[-1].style.width = '{}px'.format(call_width+SCALE)
                    # print('Сдвиг calls[-1].style.backgroundColor=«{}»'.format(calls[-1].style.backgroundColor))
                    if self.duration > 0:
                        DOM.getElementById('answered_duration.'+self.operator_id).innerHTML = '{}'.format(self.duration)
                        self.duration += 1


    def add_event(self, data):
        self.queue.append(data)


def channel_create(data):
    if ('caller_id_number' in data) and ('callee_id_number' in data):
        print('channel_create', data)
        global CANVAS
        if data['direction'] == 'outbound':

            if len(data['caller_id_number']) == 4: # Звонок оператора
                data['title'] = 'Вызов: {}\n'.format(data['callee_id_number'])
                data['title'] += 'Дата/Время: {}\n'.format(data['event_time'].split('.')[0])
                data['title'] += 'Шлюз: {}\n'.format(data['gateway_name'])
                # data['class'] = 'call-brick'
                data['style'] = {'backgroundColor': 'darkblue', 'width': 1, 'margin-right': 0,}
                data['caller_id_number'], data['callee_id_number'] = data['callee_id_number'], data['caller_id_number']
                # print('channel_create 2', data)


            if len(data['callee_id_number']) == 4:
                if data['callee_id_number'] not in CANVAS:
                    Canvas(data['callee_id_number'])
                if 'title' in data: # Исходящий, рисуем время ожидания
                    CANVAS[data['callee_id_number']].add_event(data)

        # else:
        #     print('channel_create.inbound', data)
        #     if (len(data['caller_id_number']) == 4):
        #         data['caller_id_number'], data['callee_id_number'] = data['callee_id_number'], data['caller_id_number']
        #     if len(data['callee_id_number']) == 4:
        #         if data['callee_id_number'] not in CANVAS:
        #             Canvas(data['callee_id_number'])
        #             CANVAS[data['callee_id_number']].add_event(data)


def channel_answer(data):
    print('channel_answer', data)
    global CANVAS
    if (data['direction'] == 'outbound') and ('callee_id_number' in data) and ('caller_id_number' in data):
        if (len(data['caller_id_number']) == 4):
            data['title'] = 'Разговор: {}\n'.format(data['callee_id_number'])
            data['title'] += 'Дата/Время: {}\n'.format(data['event_time'].split('.')[0])
            data['title'] += 'Шлюз: {}\n'.format(data['gateway_name'])
            # data['class'] = 'call-brick'
            data['style'] = {'backgroundColor': 'blue', 'width': 1, 'margin-right': 0, }
            data['caller_id_number'], data['callee_id_number'] = data['callee_id_number'], data['caller_id_number']

        if (len(data['callee_id_number']) == 4):
            if (data['callee_id_number'] not in CANVAS):
                Canvas(data['callee_id_number'])
            CANVAS[data['callee_id_number']].add_event(data)


def channel_hangup_complete(data):
    # print('channel_hangup_complete', data)
    global CANVAS
    if (data['direction'] == 'outbound') and ('callee_id_number' in data) and ('caller_id_number' in data):
        if (len(data['caller_id_number']) == 4):
            data['caller_id_number'], data['callee_id_number'] = data['callee_id_number'], data['caller_id_number']

        if len(data['callee_id_number']) == 4:
            if data['hangup_cause'] in ('NO_ANSWER',): # 'NETWORK_OUT_OF_ORDER'):
                if (data['duration'] == -1):
                    Noanswered(data)
                else:
                    print('channel_hangup_complete.outbound DURATION_ERROR', data)
            else:
                # print('channel_hangup_complete: len(callee_id_number) != 4', data)
                if len(data['callee_id_number']) == 4:
                    if (data['callee_id_number'] not in CANVAS):
                        Canvas(data['callee_id_number'])
                    CANVAS[data['callee_id_number']].add_event(data)
        else: # Исходящий
            # print('channel_hangup_complete: len(callee_id_number) != 4', data)
            pass
    else:
        print('channel_hangup_complete.inbound', data)
        if (data['direction'] == 'inbound') and ('callee_id_number' in data) and ('caller_id_number' in data):
            # answered_elements = [answered.id for answered in DOM.getElementsByClassName('answered-phone') if answered.innerHTML == data['caller_id_number']]
            for operator_id in [answered.id.split('.')[1] for answered in DOM.getElementsByClassName('answered-phone') if answered.innerHTML == data['caller_id_number']]:
                # operator_id = el.id.split('.')[1]
                if operator_id in CANVAS:
                    canvas = DOM.getElementById('canvas.'+operator_id)
                    calls = canvas.getElementsByClassName('call-brick') if canvas else []
                    if (len(calls) > 0) and (int(calls[-1].style.marginRight.replace('px', '')) == 0):
                        CANVAS[operator_id].add_event(data)
                        break


events = {'CHANNEL_CREATE': channel_create,
          'CHANNEL_ANSWER': channel_answer,
          'CHANNEL_HANGUP_COMPLETE': channel_hangup_complete,
        #   'CHANNEL_EXECUTE_COMPLETE': channel_execute,
        #   'CHANNEL_EXECUTE': channel_execute,
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


def __timer__():
    global CANVAS
    global NOANSWER

    _started = time.time() # Хоть как-то минимизируем дрифт... Плохо всё...
    # print (CANVAS)
    # print (NOANSWER)

    for operator_id, canvas in CANVAS.items():
        # calls = DOM.getElementById(operator_id).getElementsByClassName('call-brick')
        if canvas.to_delete:
            DOM.getElementById('content').removeChild(DOM.getElementById(operator_id))
            del CANVAS[operator_id]
        else:
            canvas.__timer__()

    for caller_id, canvas in NOANSWER.items():
        # calls = DOM.getElementById(caller_id).getElementsByClassName('noanswered-brick')
        if canvas.to_delete:
            DOM.getElementById('noanswered_calls').removeChild(DOM.getElementById(caller_id))
            del NOANSWER[caller_id]
        else:
            canvas.__timer__()

    timer.set_timeout(__timer__, 1000-(time.time()-_started)*1000)
    # print('__timer__', 1000-(time.time()-_started)*1000)

_open()
#timer.set_timeout(tik_tak, 1000)
__timer__()
