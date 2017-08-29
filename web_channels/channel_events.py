import trunks
import datetime
import time
from tornado import gen


@gen.coroutine
def channel_create(data):
    #print ('channel_create %s' % data)
    event = {}
    caller_id_number = data['Caller-Caller-ID-Number'][-10:]
    destination_number = data[
        'Caller-Destination-Number'][-10:]  # Внешний абонент
    destination_number = destination_number[
        1:] if destination_number[:1] == '22' else destination_number
    oper_time = data['Event-Date-Timestamp']
    max_lines = 10 if destination_number[:2] == '23' else 1
    if data['Call-Direction'] == 'inbound':
        # destination_number - Шлюз
        # caller_id_number - Абонент
        trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(destination_number=destination_number,
                                                                                  caller_id_number=caller_id_number,
                                                                                  max_lines=max_lines,
                                                                                  oper_time=oper_time)
        if trunk:
            event.update(trunk_name=trunk_name,  # Канал
                         caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(
                             caller_id_number) < 10 else '58px',
                         caller_id_number=caller_id_number,)  # Абонент
    else:  # outbound
        #print ('channel_create', data)
        if 'variable_sip_gateway_name' in data:  # Наружу
            callee_id_number = destination_number
            destination_number = data['variable_sip_gateway_name']
            if caller_id_number == '0000000000':  # Отзвон
                # callee_id_number - внешний абонент
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(destination_number=destination_number,  # Шлюз
                                                                                          caller_id_number=callee_id_number,  # Абонент
                                                                                          oper_time=data['Event-Date-Timestamp'])
                if trunk:
                    #print ('channel_create', trunk, trunk_name, trunk_counters)
                    event.update(trunk_name=trunk_name,  # Канал
                                 callee_width='24px' if len(callee_id_number) < 6 else '32px' if len(
                                     callee_id_number) < 10 else '58px',
                                 callee_id_number=callee_id_number,)  # Абонент
            else:  # Оператор caller_id_number звонит наружу
                print ('channel_create outbound', data)
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(destination_number=destination_number,  # Шлюз
                                                                                          caller_id_number=callee_id_number,  # Абонент
                                                                                          oper_time=data['Event-Date-Timestamp'])
                print ('channel_create outbound', trunk, trunk_name, trunk_counters, channel_id)
                if trunk:
                    event.update(trunk_name=trunk_name,  # Канал
                                 caller_id_number=caller_id_number,
                                 callee_width='24px' if len(callee_id_number) < 6 else '32px' if len(
                                     callee_id_number) < 10 else '58px',
                                 callee_id_number=callee_id_number,)  # Абонент

            # caller_id_number - Оператор
        else:  # Подбор оператора
            # caller_id_number - Абонент
            # destination_number - Оператор
            trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                                      oper_time=data['Event-Date-Timestamp'],)
            if trunk:
                event.update(caller_id_number=caller_id_number,  # Абонент
                             trunk_name=trunk_name,  # Шлюз
                             caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(
                                 caller_id_number) < 10 else '58px',
                             callee_width='24px' if len(destination_number) < 6 else '32px' if len(
                                 destination_id_number) < 10 else '58px',
                             callee_id_number=destination_number,)  # Оператор
    if trunk:
        #print (trunk, trunk_name, trunk_counters)
        #print (event)
        d, t = ('%s' % data['Event-Date-Timestamp']).split('.')[0].split(' ')
        date_time = '%s %s' % (t, '/'.join(d.split('-')[1:]))
        event.update(event_timestamp=date_time,
                     event_time=data['Event-Date-Timestamp'],
                     direction=data['Call-Direction'],
                     counters=trunk_counters,
                     virtual_line=trunk['line'],
                     channel_id=channel_id,
                     uuid=data['Caller-Unique-ID'],
                     destination=destination_number,
                     event_name=data['Event-Name'])
        if 'variable_sip_gateway_name' in data:
            event.update(gateway_name=data['variable_sip_gateway_name'])

    raise gen.Return(event)


@gen.coroutine
def channel_answer(data):
    #print ('channel_answer', data)
    event = {}
    destination_number = data['Caller-Destination-Number'][-10:]
    caller_id_number = data['Caller-Caller-ID-Number'][-10:]
    if data['Call-Direction'] == 'inbound':  # Имеет значение только для входящих на шлюзе
        trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                                  oper_time=data['Event-Date-Timestamp'])
        if trunk:
            event.update(trunk_name=trunk_name,
                         caller_id_number=caller_id_number)
    else:
        if 'variable_sip_gateway_name' in data:
            callee_id_number = data['Caller-Destination-Number'][-10:]
            caller_id_number = data['variable_sip_gateway_name']
            if data['Caller-Caller-ID-Number'] == '0000000000': # Отзвон
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=callee_id_number,
                                                                                          oper_time=data[
                                                                                              'Event-Date-Timestamp'],
                                                                                          answer=1)
                if trunk:
                    event.update(trunk_name=trunk_name,  # Шлюз
                                 callee_id_number=callee_id_number,  # Абонент
                                 callee_width='24px' if len(callee_id_number) < 6 else '32px' if len(callee_id_number) < 10 else '58px',)
            else:  # Оператор звонит наружу
                print('channel_answer', data)
                # print('channel_answer', trunks.trunks)
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=callee_id_number,
                                                                                          oper_time=data[
                                                                                              'Event-Date-Timestamp'],
                                                                                          answer=1)
                print('channel_answer', trunk, trunk_name, trunk_counters, channel_id)
                if trunk:
                    event.update(trunk_name=trunk_name,  # Шлюз
                                 callee_id_number=callee_id_number,  # Абонент
                                 callee_width='24px' if len(callee_id_number) < 6 else '32px' if len(
                                     callee_id_number) < 10 else '58px',
                                 #  caller_id_number=caller_id_number,  # Оператор
                                 caller_id_number=data['Caller-Caller-ID-Number'][-10:],
                                 caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(caller_id_number) < 10 else '58px',)
        else:  # Ответ оператора
            trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                                      oper_time=data[
                                                                                          'Event-Date-Timestamp'],
                                                                                      answer=1)
            if trunk:
                #print ('channel_answer', trunk, trunk_name, trunk_counters)
                event.update(trunk_name=trunk_name,
                             callee_id_number=destination_number,
                             callee_width='24px' if len(destination_number) < 6 else '32px' if len(
                                 destination_number) < 10 else '58px',
                             caller_id_number=caller_id_number,
                             caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(caller_id_number) < 10 else '58px',)

    if trunk:
        if 'answer' in trunk:
            answer_wait = trunk['answer'] - trunk['create']
            answer_wait = round(answer_wait.seconds +
                                int(answer_wait.microseconds / 1000) / 1000)
        else:
            answer_wait = -1
        d, t = ('%s' % data['Event-Date-Timestamp']).split('.')[0].split(' ')
        date_time = '%s %s' % (t, '/'.join(d.split('-')[1:]))
        event.update(event_timestamp=date_time,
                     event_time=data['Event-Date-Timestamp'],
                     direction=data['Call-Direction'],
                     counters=trunk_counters,
                     virtual_line=trunk['line'],
                     answer_wait=answer_wait,
                     channel_id=channel_id,
                     uuid=data['Caller-Unique-ID'],
                     event_name=data['Event-Name'])
        if 'variable_sip_gateway_name' in data:
            event.update(gateway_name=data['variable_sip_gateway_name'])

    raise gen.Return(event)


@gen.coroutine
def channel_hangup_complete(data):
    event = {}
    # print('channel_hangup_data', data)
    destination_number = data['Caller-Destination-Number'][-10:]
    caller_id_number = data['Caller-Caller-ID-Number'][-10:]
    hangup_cause = data['Hangup-Cause']
    if data['Call-Direction'] == 'outbound':
        # print('channel_hangup_data', data)
        callee_id_number = data['Caller-Callee-ID-Number'][-10:]
        if 'variable_sip_gateway_name' in data:  # Наружу звонили
            if destination_number == '6700':  # Отзвон, Был отвечен
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                                          hangup=1,
                                                                                          oper_time=data['Event-Date-Timestamp'])
                if trunk:
                    event.update(trunk_name=trunk_name,
                                 callee_id_number=caller_id_number,
                                 callee_width='24px' if len(caller_id_number) < 6 else '32px' if len(caller_id_number) < 10 else '58px',)
            elif caller_id_number == '0' * 10:   # Отзвон, Не был отвечен
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=callee_id_number,
                                                                                          hangup=1,
                                                                                          oper_time=data['Event-Date-Timestamp'])
                if trunk:
                    event.update(trunk_name=trunk_name,
                                 callee_id_number=callee_id_number,
                                 callee_width='24px' if len(callee_id_number) < 6 else '32px' if len(callee_id_number) < 10 else '58px',)
                if hangup_cause == 'NO_USER_RESPONSE':  # Нет такого номера!
                    pass
                    # hangup_cause, callee_id_number - поставить запрет
                    # укорачивания
            else:  # Был Перевод звонка, Исходящий от оператора
                callee_id_number = data['Caller-Callee-ID-Number'][-10:]
                print('channel_hangup_complete', data)
                # print('channel_answer', trunks.trunks)
                trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=callee_id_number,
                                                                                          hangup=1,
                                                                                          oper_time=data['Event-Date-Timestamp'],)
                print('channel_hangup_complete', trunk, trunk_name, trunk_counters, channel_id)
                if trunk:
                    event.update(trunk_name=trunk_name,
                                 caller_id_number=caller_id_number,
                                 caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(
                                     caller_id_number) < 10 else '58px',
                                 callee_id_number=callee_id_number,
                                 callee_width='24px' if len(callee_id_number) < 6 else '32px' if len(callee_id_number) < 10 else '58px',)

        else:  # Оператор положил трубку
            trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                                      hangup=1,
                                                                                      oper_time=data['Event-Date-Timestamp'])
            if trunk:
                event.update(trunk_name=trunk_name,
                             callee_id_number=destination_number,
                             destination=trunk_name,
                             callee_width='24px' if len(destination_number) < 6 else '32px' if len(
                                 destination_number) < 10 else '58px',
                             caller_id_number=caller_id_number,
                             caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(
                                 caller_id_number) < 10 else '58px',)

    else: # Неотвеченный Входящий
        # print ('channel_hangup_data', data)
        trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                                    hangup=1,
                                                                                    oper_time=data['Event-Date-Timestamp'])
        if trunk:
            event.update(trunk_name=trunk_name,
                        destination=data['Caller-Destination-Number'][-10:],
                        callee_id_number='',
                        callee_width='24px' if len(destination_number) < 6 else '32px' if len(
                            destination_number) < 10 else '58px',
                        caller_id_number=caller_id_number,
                        caller_width='24px' if len(caller_id_number) < 6 else '32px' if len(
                            caller_id_number) < 10 else '58px',)

        # print ('channel_hangup_data', data)
        # print ('channel_hangup_complete:', event)

    if trunk:
            #print ('caller_hangup_complete', trunk, trunk_name, trunk_counters)
        if 'answer' in trunk:  # Отвечен был?
            answer_wait = trunk['answer'] - trunk['create']
            answer_wait = round(answer_wait.seconds +
                                int(answer_wait.microseconds / 1000) / 1000)
            duration = trunk['hangup'] - trunk['answer']
            duration = round(duration.seconds +
                                int(duration.microseconds / 1000) / 1000)
        else:
            duration = -1
            answer_wait = trunk['hangup'] - trunk['create']
            answer_wait = round(answer_wait.seconds +
                                int(answer_wait.microseconds / 1000) / 1000)
        d, t = ('%s' % data['Event-Date-Timestamp']
                ).split('.')[0].split(' ')
        date_time = '%s %s' % (t, '/'.join(d.split('-')[1:]))
        event.update(event_timestamp=date_time,
                        event_time=data['Event-Date-Timestamp'],
                        direction=data['Call-Direction'],
                        counters=trunk_counters,
                        virtual_line=trunk['line'],
                        channel_id=channel_id,
                        event_name=data['Event-Name'],
                        duration=duration,
                        hangup_cause=hangup_cause,
                        uuid=data['Caller-Unique-ID'],
                        answer_wait=answer_wait,)
        if 'variable_sip_gateway_name' in data:
            event.update(gateway_name=data['variable_sip_gateway_name'])
    raise gen.Return(event)


@gen.coroutine
def channel_execute(data):
    event = {}
    caller_id_number = data['Caller-Caller-ID-Number'][-10:]
    application_data = data['Application-Data']
    trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                              oper_time=data['Event-Date-Timestamp'])
    if trunk:
        d, t = ('%s' % data['Event-Date-Timestamp']).split('.')[0].split(' ')
        date_time = '%s %s' % (t, '/'.join(d.split('-')[1:]))
        event.update(trunk_name=trunk_name,
                     callee_id_name=caller_id_number,
                     direction=data['Call-Direction'],
                     application_data=application_data.split('/')[-1:][0],
                     counters=trunk_counters,
                     event_name=data['Event-Name'],
                     uuid=data['Caller-Unique-ID'],
                     virtual_line=trunk['line'],
                     channel_id=channel_id,
                     event_timestamp=date_time,
                     event_time=data['Event-Date-Timestamp'],)
        if 'variable_sip_gateway_name' in data:
            event.update(gateway_name=data['variable_sip_gateway_name'])

    raise gen.Return(event)


@gen.coroutine
def channel_execute_complete(data):
    event = {}
    caller_id_number = data['Caller-Caller-ID-Number'][-10:]
    application_response = data['Application-Response']
    application_data = data['Application-Data']
    trunk, trunk_name, trunk_counters, channel_id = yield trunks.select_trunk(caller_id_number=caller_id_number,
                                                                              oper_time=data['Event-Date-Timestamp'])
    if trunk:
        d, t = ('%s' % data['Event-Date-Timestamp']).split('.')[0].split(' ')
        date_time = '%s %s' % (t, '/'.join(d.split('-')[1:]))
        event.update(trunk_name=trunk_name,
                     callee_id_name=caller_id_number,
                     caller_id_number=caller_id_number,
                     application_data=application_data.split('/')[-1:][0],
                     direction=data['Call-Direction'],
                     event_name=data['Event-Name'],
                     application_response=application_response,
                     virtual_line=trunk['line'],
                     channel_id=channel_id,
                     uuid=data['Caller-Unique-ID'],
                     counters=trunk_counters,
                     event_timestamp=date_time,
                     event_time=data['Event-Date-Timestamp'],)
        if 'variable_sip_gateway_name' in data:
            event.update(gateway_name=data['variable_sip_gateway_name'])

    raise gen.Return(event)

@gen.coroutine
def dtmf(data):
    event = {}
    print ('dtmf: %s' % data)
    raise gen.Return(event)


events = dict(CHANNEL_CREATE=channel_create,
              CHANNEL_ANSWER=channel_answer,
              CHANNEL_EXECUTE=channel_execute,
              DTMF=dtmf,
              CHANNEL_EXECUTE_COMPLETE=channel_execute_complete,
              CHANNEL_HANGUP_COMPLETE=channel_hangup_complete,
              )


@gen.coroutine
def main():  # Отладка исходящих
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '+79278831370',
            'Caller-Caller-ID-Number': '1117',
            'Event-Name': 'CHANNEL_CREATE',
            'variable_sip_gateway_name': 'sim_771',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print(r)
    """
    time.sleep(5)
    data = {'Call-Direction': 'outbound', 
            'Caller-Destination-Number': '+79278831370', 
            'Caller-Caller-ID-Number': '1117', 
            'Event-Name': 'CHANNEL_ANSWER',
            'variable_sip_gateway_name': 'sim_771',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_answer(data)
    print (r)
    """
    time.sleep(5)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '+79278831370',
            'Caller-Caller-ID-Number': '1117',
            'Event-Name': 'CHANNEL_HANGUP_COMPLETE',
            'variable_sip_gateway_name': 'sim_771',
            'Hangup-Cause': 'NORMAL_CLEARING',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_hangup_complete(data)
    print(r)


@gen.coroutine
def main2():  # Отладка отзвонов
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '+79278831370',
            'Caller-Caller-ID-Number': '0' * 10,
            'Event-Name': 'CHANNEL_CREATE',
            'variable_sip_gateway_name': 'sim_771',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print(r)
    time.sleep(5)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '+79278831370',
            'Caller-Caller-ID-Number': '0' * 10,
            'Event-Name': 'CHANNEL_ANSWER',
            'variable_sip_gateway_name': 'sim_771',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_answer(data)
    print(r)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '6700',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_EXECUTE',
            'variable_sip_gateway_name': 'sim_771',
            'Application-Data': 'file-name.wav',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_execute(data)
    print(r)
    time.sleep(3)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '6700',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_EXECUTE_COMPLETE',
            'variable_sip_gateway_name': 'sim_771',
            'Application-Data': 'file-name.wav',
            'Application-Response': 'FILE PLAYED',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_execute_complete(data)
    print(r)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '+79278831370',
            'Caller-Caller-ID-Number': '0' * 10,
            'Event-Name': 'CHANNEL_HANGUP_COMPLETE',
            'variable_sip_gateway_name': 'sim_771',
            'Hangup-Cause': 'NORMAL_CLEARING',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_hangup_complete(data)
    print(r)


@gen.coroutine
def main1():  # Отладка входящих и ответов на них
    data = {'Call-Direction': 'inbound',
            'Caller-Destination-Number': '230021',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_CREATE',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print(r)
    data = {'Call-Direction': 'inbound',
            'Caller-Destination-Number': '230021',
            'Caller-Caller-ID-Number': '88362429578',
            'Event-Name': 'CHANNEL_CREATE',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print(r)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '1117',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_CREATE',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print(r)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '1102',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_CREATE',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print(r)
    time.sleep(5)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '1117',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_ANSWER',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_answer(data)
    print(r)
    """
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '1102',
            'Caller-Caller-ID-Number': '88362429578',
            'Event-Name': 'CHANNEL_ANSWER',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_answer(data)
    print (r)
    """
    time.sleep(5)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '1117',
            'Caller-Caller-ID-Number': '+79278831370',
            'Event-Name': 'CHANNEL_HANGUP_COMPLETE',
            'Hangup-Cause': 'NORMAL_CLEARING',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_hangup_complete(data)
    print(r)
    # time.sleep(5)
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '1102',
            'Caller-Caller-ID-Number': '88362429578',
            'Event-Name': 'CHANNEL_HANGUP_COMPLETE',
            'Hangup-Cause': 'NORMAL_CLEARING',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_hangup_complete(data)
    print(r)
    """
    data = {'Call-Direction': 'outbound',
            'Caller-Destination-Number': '+79278831370',
            'Caller-Caller-ID-Number': '0000000000',
            'variable_sip_gateway_name': '09177079999',
            'Event-Name': 'CHANNEL_CREATE',
            'Event-Date-Timestamp': datetime.datetime.now()}
    r = yield channel_create(data)
    print (r)
    """


if __name__ == '__main__':
    main1()
    print(trunks.trunks)
