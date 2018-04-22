# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
    return dict()

def run():

    if not scheduler.task_status(db.scheduler_task.task_name == 'bkrs_init', output=True):
        scheduler.queue_task(
            'bkrs_init',
            pvars=dict(file="static/dsl/dabkrs.dsl",truncate=True),
            prevent_drift=True,
            immediate=True,
            timeout=10800,
            sync_output=3)
    return response.json(dict(status=worker_start()))


def stop():
    return response.json(dict(
            status=scheduler.stop_task(scheduler.task_status(db.scheduler_task.task_name == 'bkrs_init').uuid)!=None
        ))


def new_start():
    db(db.scheduler_task.task_name == 'bkrs_init').delete()
    return response.json(dict(status=True))


from gluon.contrib.simplejson import loads
def stepper():
    file=os.path.normpath(os.path.join(request.folder, 'static/dsl/dabkrs.dsl'))
    task_status = scheduler.task_status(db.scheduler_task.task_name == 'bkrs_init', output=True)
    if task_status and os.path.exists(file):
        if task_status.scheduler_task.status in ["COMPLETED", "FAILED", "STOPPED"]:
            scheduler.terminate()
        return response.json(dict(
                file_ready=True,
                task_status=task_status.scheduler_task.status,
                run_status=task_status.scheduler_run.status,
                run_output=task_status.scheduler_run.run_output,
                start_time=task_status.scheduler_run.start_time,
                run_traceback=task_status.scheduler_run.traceback
            ))
    else:
        return response.json(dict(
                file_ready=os.path.exists(file),
                task_status=None,
                run_status=None,
                run_output=None,
                start_time=None,
                run_traceback=None
            ))


def set_bywords_short():
    """Добавляет в базу слова с кратким переводом"""
    file_path=os.path.join(current.request.folder,'static/dsl/shortlist.txt')
    if not os.path.exists(file_path):
        return False
    with open(file_path, mode='r') as f:
        for slovo, short in [x.split("\t") for x in f.read().split("\n")]:
            row=db(slovar.slovo == slovo).select().first()
            if row:
                row.update_record(bywords_short = short, use_short = True)
    return response.json(dict(status=True))


def set_penaty():
    """Задает слова-исключения из пословного перевода"""
    file_path=os.path.join(current.request.folder,'static/dsl/penalty.txt')
    if not os.path.exists(file_path):
        return False
    with open(file_path, mode='r') as f:
        for x in f.read().replace(',', '\n').split('\n'):
            slovo = x.strip()
            if not slovo: continue
            row = db(slovar.slovo == slovo).select().first()
            if row:
                row.update_record(bywords_out = True)
    return response.json(dict(status=True))
