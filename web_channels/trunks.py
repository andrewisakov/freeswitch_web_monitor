import threading, psycopg2 as pg2
import datetime
from tornado.locks import Semaphore
from tornado import gen
from collections import OrderedDict
trunks = OrderedDict()
trunks_groups = OrderedDict()
trunks_semaphore = Semaphore(1)

@gen.coroutine
def _read_trunks():
    global trunks
    global trunks_groups
    if trunks and trunks_groups:
        raise gen.Return(trunks)
        
    trunks = OrderedDict()
    trunks_groups = OrderedDict()
    try:
        db = pg2.connect('host=192.168.222.20 port=5432 dbname=freeswitch_trunks user=freeswitch password=freeswitch')
        c = db.cursor()
        SELECT = 'select tr.name as group_trunks, trl.phone as trunk_name, o.name as operator_name, o.icon_name, ' \
        'trl.in_trunk_position, c.id as channel_id, trl.direction, d.id as device_id, ' \
        'c.lines as max_lines, c.sip_gateway_name, d.address, c.port, dcl.name as device_class, tr.screen_position, ' \
        'trl.trunk_id ' \
        'from trunk_lines trl ' \
        'left join operators o on (o.id=trl.operator_id) ' \
        'left join trunks tr on (tr.id=trl.trunk_id) ' \
        'left join channels c on (c.id=trl.channel_id) ' \
        'left join devices d on (d.id=c.device_id) ' \
        'left join device_classes dcl on (dcl.id=d.class_id) ' \
        'where (trl.channel_id > 0) and (c.is_active) ' \
        'order by tr.screen_position, group_trunks, trl.in_trunk_position '
        c.execute(SELECT)
        for r in c.fetchall():
            trunk_name = r[9] if r[9] else '0'+r[1] if r[1][:2] != '23' else r[1]
            # trunk_name = r[9] if r[9] else '0'+r[1]

            if not trunk_name in trunks:
                trunks[trunk_name] = OrderedDict()
            if not r[0] in trunks_groups:
                trunks_groups[r[0]] = []
            trunks_groups[r[0]].append(trunk_name)
            trunks[trunk_name].update(callers           = dict(), # Обрабатываемы(е/й) звонок(и)
                                        max_lines       = r[8], # channels.lines
                                        operator_logo   = 'static/img/%s.png' % r[3], # operators.icon_name
                                        channel_id      = r[5], # channels.id
                                        counters        = {'answered': 0, 'total': 0, 'rejected': 0}, # Счётчики
                                        direction       = r[6], # trunk_lines.directions ['inbound', 'outbound', 'sms']
                                        channel         = '%s:%s' % (r[10], r[11]), # device.address, channel.port
                                        group           = r[0], # trunks.name
                                        semaphore       = Semaphore(1), # Блокировка транка
                                        phone           = r[1], # Номер телефона на линии
                                        device_id       = r[7],
                                        screen_position = r[13],
                                        trunk_id        = r[14],
                                      ) 
            print (trunk_name)
        c.close()
        db.close()
    except Exception as e:
        print ('ChannelHandler._read_trunks исключение: %s' % e)
    # print ('ChannelHandler._read_trunks данные: %s' % trunks)
    raise gen.Return(trunks)

@gen.coroutine
def select_trunk(caller_id_number=None, destination_number=None, hangup=0, answer=0, oper_time=datetime.datetime.now(), max_lines=1, debug=False):

    global trunks
    global trunks_semaphore

    try:
        oper_time = datetime.datetime.strptime(
            oper_time, '%Y-%m-%d %H:%M:%S.%f')
    except Exception as e:
        oper_time = oper_time

    with (yield trunks_semaphore.acquire()): # Захват глобального лока
        if not trunks: # Усли пусто - подгрузить
            trunks = yield _read_trunks()

    caller_id_number = caller_id_number[-10:]
    if (not destination_number) and (caller_id_number):  # Выяснить транк
        for tr in trunks:
            with (yield trunks[tr]['semaphore'].acquire()):  # Захват транка
                if caller_id_number in trunks[tr]['callers']:
                    if not ('hangup' in trunks[tr]['callers'][caller_id_number]):
                        if hangup == 1:  # Отбой
                            if debug:
                                print('select_trunk: Освободить %s' %
                                      caller_id_number)
                            trunks[tr]['callers'][caller_id_number]['hangup'] = oper_time
                            if not ('answer' in trunks[tr]['callers'][caller_id_number]):
                                trunks[tr]['counters']['rejected'] += 1

                        if answer > 0:  # Отвечен
                            trunks[tr]['callers'][caller_id_number]['answer'] = oper_time
                            trunks[tr]['counters']['answered'] += 1
                        elif answer < 0:  # Не отвечен
                            trunks[tr]['callers'][caller_id_number]['reject'] = oper_time
                            trunks[tr]['counters']['rejected'] += 1
                        raise gen.Return(
                            (trunks[tr]['callers'][caller_id_number], 
                            tr, 
                            trunks[tr]['counters'], 
                            trunks[tr]['channel_id'],))  # Выход
        raise gen.Return((None, None, None, None))
    elif destination_number and caller_id_number:  # Выделить канал в транке
        # destination_number = destination_number[-10:]
        # if not (destination_number in trunks):
        #     trunks[destination_number] = dict(max_lines=max_lines,  # Максимально количество линий на транке
        #                                       counters=dict(
        #                                           answered=0, rejected=0, total=0),
        #                                       semaphore=Semaphore(1),
        #                                       callers={})
        if not (destination_number in trunks):
            raise gen.Return((None, None, None, None))
        with (yield trunks[destination_number]['semaphore'].acquire()):
            # Если пока ещё есть с таким входящим
            if caller_id_number in trunks[destination_number]['callers']:
                if 'hangup' in trunks[destination_number]['callers'][caller_id_number]:
                    del trunks[destination_number][
                        'callers'][caller_id_number]['hangup']
                    trunks[destination_number]['callers'][
                        caller_id_number]['create'] = oper_time
                    trunks[destination_number]['counters']['total'] += 1
                    raise gen.Return((trunks[destination_number]['callers'][caller_id_number],
                                      destination_number,
                                      trunks[destination_number]['counters'], 
                                      trunks[destination_number]['channel_id'],))  # Выход
                # else:
                #  raise gen.Return() # Выход
            # Если линий достаточно, просто добавим
            if len(trunks[destination_number]['callers']) < trunks[destination_number]['max_lines']:
                trunks[destination_number]['callers'][caller_id_number] = {'line': len(trunks[destination_number]['callers']),
                                                                           'create': oper_time,
                                                                           }
                trunks[destination_number]['counters']['total'] += 1
                raise gen.Return((trunks[destination_number]['callers'][caller_id_number],
                                  destination_number,
                                  trunks[destination_number]['counters'],
                                  trunks[destination_number]['channel_id'],))  # Выход
            # Искать самую старую hangup
            candidates = {}
            for c in trunks[destination_number]['callers']:
                if 'hangup' in trunks[destination_number]['callers'][c]:
                    candidates[trunks[destination_number]['callers'][c]['hangup']] = (
                        c, trunks[destination_number]['callers'][c]['line'])
            if candidates:
                candidate, line = candidates[min(candidates)]
                del trunks[destination_number]['callers'][candidate]
                trunks[destination_number]['counters']['total'] += 1
                trunks[destination_number]['callers'][caller_id_number] = {'line': line,
                                                                           'create': oper_time, }
                #print ('trunks.select_trunk %s: %s' (caller_id_number, trunks[destination_number][caller_id_number]))
                raise gen.Return((trunks[destination_number]['callers'][caller_id_number],
                                  destination_number,
                                  trunks[destination_number]['counters'],
                                  trunks[destination_number]['channel_id'],))  # Выход
            else:
                raise gen.Return((None, None, None, None))  # Выход


@gen.coroutine
def main():
    a = yield select_trunk('9278831370', '230021')
    print('Захват 9278831370', a)

    a = yield select_trunk('9278831370')
    print('Поиск 9278831370', a)

    a = yield select_trunk('9024306878')
    print('Поиск 9024306878', a)

    a = yield select_trunk('9278831370', hangup=1)
    print('Освобождение 9278831370', a)

    a = yield select_trunk('9278831370', '230021')
    print('Захват 9278831370', a)

    a = yield select_trunk('9024306878', '230021')
    print('Захват 9024306878', a)

    # print('\n', trunks)
    # print(trunks_groups)

if __name__ == '__main__':
    main()
