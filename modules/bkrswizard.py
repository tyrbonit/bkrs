#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Данный файл(модуль) содержит функции, которые будут запускаться
в отдельном фоновом потоке (в потоке исполнения "работника").
Функции задач ставятся в очередь через метод .queue_task планировщика scheduler,
который определен в модели scheduler.py приложения web2py.
Работники можно запустить вне web2py из консоли командной строки командами:
python web2py.py -K bkrs из исходного кода(используется python версии 2.7)
или
web2py.exe -K bkrs для исполняемого файла windows
Но в контроллере мастера установки реализован автозапуск.
"""
import io
from gluon import *
from gluon.serializers import json
import re, os, chardet
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def read_by_blocks(file_path, block_size=512, encode='utf-8'):
    """Генератор, считывающий файл по блокам из строк,
    которые заканчиваются пустой строкой.
    Возращает текстовый блок и прогресс чтения файла.
    """
    i = 0  # Счетчик строк в файле
    # Открываем файл в бинарном режиме и определяем кодировку
    with io.open(file_path, mode='rb') as f:
        enc = chardet.detect(f.read(block_size)).get('encoding')  # Определяем кодировку
        f.close()

    # Общее число строк в файле для подсчета процентов
    with io.open(file_path, mode='r', encoding=enc) as f:
        n = sum(1 for _ in f)
        f.close()

    # Переходим к чтению по блокам, заканчивающихся пустой строкой
    with io.open(file_path, mode='r', encoding=enc) as f:
        empty_line = u'\n'
        bufer = f.readlines(block_size)  # Считываем в буфер список строк размером около block_size Б
        while True:
            if empty_line in bufer:
                indx = bufer.index(empty_line) + 1
                lines, bufer = bufer[:indx], bufer[indx:]
                i += len(lines)
                yield "".join(lines).encode(encode), round(float(i)/n*100, 3)
            else:
                lines = f.readlines(block_size)
                if lines:
                    bufer.extend(lines)
                    continue
                else:
                    yield "".join(bufer).encode(encode), round(float(i + len(bufer))/n*100, 3)
                    break

def coroutine(func):
    """Декоратор для автозапуска корутины"""
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start


@coroutine
def dsl_parser(pattern):
    """Разборка блока текста в формате dsl и добавление в словарь"""
    regexp = re.compile(pattern)
    text=""
    while True:
        text = (yield regexp.findall(text))


def sozdanie_bazy(file, truncate=False):
    """Заполнение базы из файла словаря в формате DSL."""
    if not os.path.exists(file): file=os.path.normpath(os.path.join(current.request.folder, file))
    if not os.path.exists(file): return "Файл не найден"
    # convertfile(file)#Пересохраняем в utf-8
    db = current.db
    slovar = db.slovar
    if truncate:slovar.truncate()#Опустошаем таблицу базы данных, если надо
    inserted, updated = 0, 0  #Счетчик вставленных и обновленных записей в базе данных
    parser = dsl_parser(r"(?m)^([^\s].*?)\n\s(.*?)\n\s(.*?)$")
    for blocktext, progress in read_by_blocks(file):
        for slovo, pinyin, perevod in parser.send(blocktext):
            try:
                slovar.insert(slovo = slovo,
                              pinyin = pinyin,
                              perevod = perevod
                             )
                inserted+=1
            except:
                db.commit()
                row=db(slovar.slovo == slovo).select().first()
                if not row:
                    continue
                row.pinyin = pinyin
                row.perevod = perevod
                row.update_record()
                updated += 1
        if inserted%5000==0:
            db.commit()
            msg=dict(inserted=inserted, updated=updated, progress=progress)
            current.W2P_TASK.logger.write('!clear!%s'%json(msg))
    parser.close()
    db.commit()

class Master(object):

    def __init__(self):
        self.scheduler = current._scheduler
        self.db = current.db
        self.process = None
        if not self.scheduler.task_status(self.db.scheduler_task.task_name == 'sozdanie_bazy', output=True):
            self.queue_task = self.scheduler.queue_task(
                'sozdanie_bazy',
                pvars=dict(file="static/dsl/dabkrs.dsl",truncate=True),
                prevent_drift=True,
                immediate=True,
                timeout=10800,
                sync_output=3)
        self.task_status = self.scheduler.task_status(self.db.scheduler_task.task_name == 'sozdanie_bazy', output=True)

    def execute(self):
        cmd = current.request.args
        cmd = cmd[0] if cmd else None
        func=dict(
            stepper=self.stepper,
            run=self.worker_start,
            stop=self.stop,
            new_start=self.clear,
            set_shorts=self.set_bywords_short,
            set_penalty=self.set_penalty
        ).get(cmd, lambda: dict())
        return func()

    def worker_start(self):
        import subprocess
        # Определяем путь к исполняемому файлу web2py
        winwworker=os.path.join(current.request.env.web2py_path,'web2py.exe')
        pyworker=os.path.join(current.request.env.web2py_path,'web2py.py')
        application = current.request.application
        # Строим консольную комманду
        cmd=[winwworker, '-K', application] if os.path.isfile(winwworker) else ['python', pyworker, '-K', application]
        # Пытаемся 3 раза запустить процесс работника
        for i in [0,1,2]:
            p = subprocess.Popen(cmd, stdout=sys.stdout)
            if p.poll()==None:
                self.process = p
                return dict(status=True)
        self.process = None
        return dict(status=False)


    def stop(self):
        return dict(status=self.scheduler.stop_task(self.task_status.uuid)!=None)


    def clear(self):
        self.db(self.db.scheduler_task.task_name == 'sozdanie_bazy').delete()
        return dict(status=True)


    def stepper(self):
        request=current.request
        file = os.path.normpath(os.path.join(request.folder, 'static/dsl/dabkrs.dsl'))
        task_status = self.task_status
        if task_status and os.path.exists(file):
            if task_status.scheduler_task.status in ["COMPLETED", "FAILED", "STOPPED"]:
                self.scheduler.terminate()
            return dict(
                    file_ready=True,
                    task_status=task_status.scheduler_task.status,
                    run_status=task_status.scheduler_run.status,
                    run_output=task_status.scheduler_run.run_output,
                    start_time=task_status.scheduler_run.start_time,
                    run_traceback=task_status.scheduler_run.traceback
                )
        else:
            return dict(
                    file_ready=os.path.exists(file),
                    task_status=None,
                    run_status=None,
                    run_output=None,
                    start_time=None,
                    run_traceback=None
                )


    def set_bywords_short(self):
        """Добавляет в базу слова с кратким переводом"""
        file_path = os.path.join(current.request.folder,'static/dsl/shortlist.txt')
        db = current.db
        slovar = current.db.slovar
        if not os.path.exists(file_path):
            return dict(status=False)
        with open(file_path, mode='r') as f:
            for slovo, short in [x.split("\t") for x in f.read().split("\n")]:
                row = db(slovar.slovo == slovo).select().first()
                if row:
                    row.update_record(bywords_short = short, use_short = True)
                else:
                    current.db.slovar.insert(slovo=slovo, bywords_short = short, use_short = True)
            db.commit()
        return dict(status=True)


    def set_penalty(self):
        """Задает слова-исключения из пословного перевода"""
        file_path=os.path.join(current.request.folder,'static/dsl/penalty.txt')
        db = current.db
        slovar = current.db.slovar
        if not os.path.exists(file_path):
            return dict(status=False)
        with open(file_path, mode='r') as f:
            for x in f.read().replace(',', '\n').split('\n'):
                slovo = x.strip()
                if not slovo: continue
                row = db(slovar.slovo == slovo).select().first()
                if row:
                    row.update_record(bywords_out = True)
            db.commit()
        return dict(status=True)


def createlinks():
    """Создание ссылок между записями словарных статей"""
    db = current.db
    slovar = db.slovar
    reg_ref=re.compile(r"\[ref\](.*?)\[/ref\]")
    i,j=0,0
    n=db(slovar.id>0).count()
    for x in db(slovar.id>0).iterselect():
        i+=1
        for slovlnk in reg_ref.findall(x.perevod):
            row=db(slovar.slovo==slovlnk).select().first()
            if row==None:continue

            tolist=x.linksto if x.linksto!=None else []
            if row.id not in tolist:
                tolist.append(row.id)
                x.update_record(linksto=tolist)

            fromlist=row.linksfrom if row.linksfrom!=None else []
            if x.id not in fromlist:
                fromlist.append(x.id)
                row.update_record(linksfrom=fromlist)
            j+=1
        if j%1000==0:
            db.commit() # Фиксируем каждые 1000 вставок

        msg=json(
                dict(founded=j,
                     progress=round(float(i)/n*100, 2)
                    ))
        current.W2P_TASK.logger.write('!clear!%s'%msg)
    db.commit()
    return "Complite"


def calc_records():
    """Расчет записей для вычисляемых полей"""
    db = current.db
    slovar = db.slovar
    #Список объектов вычисляемых полей
    to_compute=[ofield for ofield in slovar if ofield.compute]
    if to_compute:
        i=0
        rows=db(slovar.id>0)
        n=rows.count()
        for x in rows.iterselect():
            i+=1
            x.update_record(**{ofield.name:ofield.compute(x) for ofield in to_compute})
            if i%10000==0:
                db.commit()#Фиксируем каждые 10000 обновлений
            msg=json(
                dict(id=x.id,
                     progress=round(float(i)/n*100, 2)
                    ))
            current.W2P_TASK.logger.write('!clear!%s'%msg)
        db.commit()
    return "Complite"


def choiselist():
    """Заполнение списка вариантов перевода"""
    from bkrstools import get_choices
    db = current.db
    slovar = db.slovar
    i=0
    rows=db(slovar.choiselist==[])
    n=rows.count()
    for x in rows.iterselect(slovar.id, slovar.perevod, slovar.choiselist):
        i+=1
        msg=json(
                dict(id=x.id,
                     progress=round(float(i)/n*100, 2)
                    ))
        current.W2P_TASK.logger.write('!clear!%s'%msg)
        slovlist=get_choices(x.perevod)
        if slovlist:
            x.update_record(choiselist=slovlist)
        if i%10000==0: db.commit() # Фиксируем каждые 10000 обновлений
    db.commit()
    return "Complite"


def extract_examles():
    """Извлечение примеров из словаря"""
    db = current.db
    slovar = db.slovar
    i,j,k,l=0,0,0,0
    rows=db((slovar.is_example==False)&(slovar.processed==False))
    n=rows.count()
    for x in rows.iterselect(slovar.id,slovar.perevod):
        i+=1
        updated,inserted=extract_save_examples(x.perevod, x.id)
        j+=updated+inserted
        k+=updated
        l+=inserted
        msg=json(
                dict(id=x.id,
                     progress=round(float(i)/n*100, 2),
                     founded=j,
                     updated=k,
                     inserted=l
                    ))
        current.W2P_TASK.logger.write('!clear!%s'%msg)
        x.processed=True
        x.update_record()
        # if j%10000==0:db.commit() # Фиксируем каждые 10000 обновлений
        db.commit()
    return "Complite"

# from bkrstools import extract

# def extract_save_examples(perevod,id=None):
    """Извлечение и сохранение примеров из перевода"""
    """slovar=current.slovar
    db=current.db
    exlist=extract(perevod)
    updated,inserted=0,0
    for exam in exlist:
        try:
            slovar.insert(
                slovo=exam.slovo,
                pinyin=exam.pinyin,
                perevod=exam.perevod,
                linksfrom=[id] if id else [],
                is_example=True)
            inserted+=1
        except:
            db.commit()
            row=db(slovar.slovo==exam.slovo).select().first()
            if not row:continue
            if id and id not in row.linksfrom: row.linksfrom.append(id)
            if exam.perevod not in row.perevod.decode('utf-8'):
                row.perevod=row.perevod.decode('utf-8')+u"[apndx]"+exam.perevod+u"[/apndx]"
                row.with_appendix=True
                row.update_record()
                updated+=1
    return updated,inserted"""
