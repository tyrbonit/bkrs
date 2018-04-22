# -*- coding: utf-8 -*-
from scheduler import Scheduler
from bkrswizard import sozdanie_bazy
import sys, time
from gluon.serializers import json


def test_percentage(*args,**vars):
    """Тестовая функция"""
    for i in range(10):
        time.sleep(5)
        msg='!clear!%s'%(json(dict(progress=i*10, inserted=i+1, updated=i+3)))
        W2P_TASK.logger.write(msg)


scheduler = Scheduler(db,
                      max_empty_runs=50,
                      tasks=dict(bkrs_init=sozdanie_bazy),
                      heartbeat=1
                     )


def worker_start():
    import subprocess
    # Определяем путь к исполняемому файлу web2py
    winwworker=os.path.join(request.env.web2py_path,'web2py.exe')
    pyworker=os.path.join(request.env.web2py_path,'web2py.py')
    # Строим консольную комманду
    cmd=[winwworker, '-K', request.application] if os.path.isfile(winwworker) else ['python', pyworker, '-K', request.application]
    # Пытаемся 3 раза запустить процесс работника
    for i in [0,1,2]:
        p = subprocess.Popen(cmd, stdout=sys.stdout)
        if p.poll()==None:
            return True
    return False
