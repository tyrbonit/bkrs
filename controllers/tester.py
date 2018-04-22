# -*- coding: utf-8 -*-
tokenizer = bywords.tokenizer
bw_parser = bywords.bw_parser

def chunks2table(rez):
    chunks=rez.chunks
    chunks.sort(key = lambda x:x.start)
    m=max(chunks, key=lambda x:x.end).end
    b=[[TH('Часть'), TH('Занимаемые позиции', _colspan=m), TH('Перевод')]]
    for x in chunks:
        a=[rez.data.get(x.id).slovo]
        a.extend([TD("", _style="width: 30px") for s in range(x.start)])
        a.extend(TD(s, _style="width: 30px") for s in range(x.start, x.end))
        a.extend([TD("", _style="width: 30px") for s in range(x.end, m)])
        a.extend([", ".join(rez.data.get(x.id).choiselist[:3])])
        b.append(a)
    return TABLE(b)


def index():
    form = FORM(
        TEXTAREA(_name='slovo',
              _placeholder="Введите здесь текст для пословного перевода ...",
              _id="w2p_keywords", _class="form-control", _required=""),
        INPUT(_type='submit', _value="Искать", _class="btn"),
        _id="forma-poiska"
    )
    a, b, c, d = "", "", "", ""
    if form.process(keepvalues=True).accepted or request.vars.slovo!=None:
        a = chunks2table(bw_parser(request.vars.slovo, cross=True))
        b = chunks2table(bw_parser(request.vars.slovo, cross=False))
        c = chunks2table(bw_parser(request.vars.slovo, cross=None))
        data = tokenizer(request.vars.slovo)
        rez = Storage(chunks=[], data=Storage())
        for key, value in data.items():
            id = hash(key)
            rez.data[id] = Storage(slovo=key, choiselist = [value.value or ""])
            rez.chunks.extend([Storage(start=x[0], end=x[1], id=id) for x in value.pos])
        d = chunks2table(rez)
    return dict(form=form, a=a,b=b, c=c, d=d)
