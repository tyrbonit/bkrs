# -*- coding: utf-8 -*-

def index():
    """Действие по умолчанию, показывает таблицу словарной базы данных"""
    form=SQLFORM.grid(
        slovar,
        csv=False,
    )
    return dict(form=form)


def translater():
    if request.args:
        # В списке request.args после обработки все юникодные символы заменяются на "_", поэтому возъмем их напрямую
        path = request.env.path_info[1:] if request.env.path_info.startswith('/') else request.env.path_info
        args = path.split('/')[3:]
        if request.args[0] != 'bywords':
            request.vars.text = args[0]
        elif len(request.args)>1:
            request.vars.text = args[1]
    return dict()


@request.restful()
def api():
    response.view = 'generic.json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'
    #@cache.action(cache_model=cache.ram, prefix='translated-text')
    def GET(*args, **vars):
        vars=Storage(vars)
        if 'translate' in args:
            return bywords.bw_parser(vars.text or '', cross='cross' in args, fullmatch_return='fullmatch' in args)
        elif 'pinyin' in args:
            return bkrstools.getpinyin(vars.text or '', style=vars.style or 'tone', heteronym = 'heteronym' in args, lazy=True)
        return dict(alert='Invalid request path', type='error')

    def POST(*args, **vars):
        vars=Storage(vars)
        path='/'.join(args)
        if not auth.user:
            return dict(alert='Need authorization', type='warning')

        if path=='slovar':
            msg="New word added" if db.slovar.update_or_insert(
                db.slovar.slovo == vars.slovo,
                **vars
            ) else "Saved"
            return dict(alert=msg, type='success')

        m = re.match(r'^slovar/\d+$', path)
        if m:
            row = db.slovar[vars.id]
            row.update_record(**vars)
            return dict(alert="Saved", type='success')

        m = re.match(r'^slovar/(\d+)/choiselist$', path)
        if m:
            id=m.group(1)
            row=db.slovar[id]
            if vars.new:
                row.choiselist.insert(0, vars.new)
                msg="New added"
            if vars.first:
                row.choiselist.remove(vars.first)
                row.choiselist.insert(0, vars.first)
                msg="Choise set as first"
            if vars.remove:
                row.choiselist.remove(vars.remove)
                msg="Choise removed"
            row.update_record()
            cache.ram.clear('translated-text.*')
            return dict(alert=msg, type='success')

        m = re.match(r'^slovar/(onbypass|offbypass)/(\d+)$', path)
        if m:
            id=m.group(2)
            db.slovar[id].update_record(bywords_out=m.group(1)=='onbypass')
            msg="Word set as byword %s"%(m.group(1))
            cache.ram.clear('translated-text.*')
            return dict(alert=msg, type='success')
        return dict(alert='Invalid request path', type='error')

    return locals()
