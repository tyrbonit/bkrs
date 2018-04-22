#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.storage import Storage
import re
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")
from bkrstools import get_choices


def corrector(a):
    if not "," in "|".join(a):
        return False
    b=[]
    for x in a:
        b.extend(x.split(','))
    a=[]
    for x in b:
        if (not x in a) and x.strip():
            a.append(x.strip())
    return a


def row_corrector(row):
    if row.corrected: return row
    if row.choiselist:
        new_list = corrector(row.choiselist)
    else:
        new_list = get_choices(row.bywords_short if row.use_short else row.perevod)
    if new_list:
        row.choiselist=new_list
        row.corrected=True
        row.update_record()
        current.db.commit()
    return row


def zhnum(txt):
    """Преобразует прописную форму числа на китайском в цифровую форму"""
    txt = txt.decode('utf-8')
    numreplace={'零':'0','〇':'0','一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9'}
    if re.search(u"^[零〇一二三四五六七八九]{2,}$", txt):
        return re.sub(u"[零〇一二三四五六七八九]", lambda m: numreplace[m.group(0).encode('utf-8')], txt)
    regcorr = re.compile(u"([百佰万亿])[一二两三四五六七八九零壹贰叁肆伍陆柒捌玖]$")
    repcorr = {"百":"十","佰":"十","万":"千","亿":"万"}
    regroup1 = re.compile(u"([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰千仟万萬]+)([万萬亿億兆])")
    wani = {"万":"10000", "萬":"10000","亿":"100000000","億":"100000000", "兆":"1000000000000"}
    regroup2 = re.compile(u"([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰]+)([千仟])")
    regroup3 = re.compile(u"([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖]+)([十百拾佰])")
    shibai = {"十":"10", "百":"100", "拾":"10", "佰":"100"}
    slogi = {"〇":"+0","一":"+1","二":"+2","两":"+2","三":"+3","四":"+4","五":"+5",
           "六":"+6","七":"+7","八":"+8","九":"+9","零":"+0","壹":"+1","贰":"+2",
           "叁":"+3","肆":"+4","伍":"+5","陆":"+6","柒":"+7","捌":"+8","玖":"+9",
           "十":"+10", "百":"+100", "拾":"+10", "佰":"+100", "千":"+1000",
           "仟":"+1000", "万":"+10000","萬":"+10000","亿":"+100000000","億":"+100000000", "兆":"+1000000000000"}
    reslogi = re.compile(u"[〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰千仟万萬亿億兆]")

    txt = txt.replace(u"万万",u"亿")

    txt = regcorr.sub(lambda m: m.group(0)+repcorr[m.group(1).encode('utf-8')], txt)

    txt = regroup1.sub(lambda m: "+("+m.group(1)+")*"+wani[m.group(2).encode('utf-8')], txt)

    txt = regroup2.sub(lambda m: "+("+m.group(1)+")*1000", txt)

    txt = regroup3.sub(lambda m: m.group(1)+"*"+shibai[m.group(2).encode('utf-8')], txt)

    txt = reslogi.sub(lambda m: slogi[m.group(0).encode('utf-8')], txt)

    return "{:,}".format(eval(txt))


def pretranslater(txt):
    """Ищет прописные числа и даты в тексте, выдает список координат, формирует область занятых позиций и перевод"""
    txt = txt.decode('utf-8')
    slovdict = Storage(scope=set())

    def find_pattern(pattern, callback):
        for m in re.finditer(pattern, txt):
            pos = [m.start(), m.end()]
            scope=set(range(*pos))
            if not slovdict.scope.isdisjoint(scope): continue
            slovdict.scope|=scope
            key = m.group(0).encode('utf-8')
            if key in slovdict:
                slovdict[key].pos.append(pos)
            else:
                slovdict[key]=Storage(
                    pos=[pos],
                    value=callback(m))

    # Полный формат даты цифрами
    find_pattern(u"(\d{4}|\d{2})年(\d{1,2})月(\d{1,2})日",
                 lambda m: "{0:0=2}.{1:0=2}.{2} г.".format(int(m.group(3)), int(m.group(2)), int(m.group(1))))

    # Полный формат даты прописью
    find_pattern(u"([零〇一二三四五六七八九]{1,4})年([一二三四五六七八九十]{1,2})月([一二三四五六七八九十]{1,3})[日号]",
                 lambda m: "{0:0=2}.{1:0=2}.{2} г."%format(int(zhnum(m.group(3).encode('utf-8'))),
                                                           int(zhnum(m.group(2).encode('utf-8'))),
                                                           zhnum(m.group(1).encode('utf-8'))))

    # Дата в виде месяц-год цифрами
    months = {1: "январь", 2: "февраль", 3: "март", 4: "апрель", 5: "май", 6: "июнь",
              7: "июль", 8: "август", 9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"}
    find_pattern(u"(\d{4}|\d{2})年(\d{1,2})月(?!\d)",
                 lambda m: "%s %s г."%(months.get(int(m.group(2)), "%s месяц"%m.group(2)), m.group(1)))

    # Дата в виде месяц-год прописью
    find_pattern(u"([零〇一二三四五六七八九]{1,4})年([一二三四五六七八九十]{1,2})月(?![一二三四五六七八九十])",
                 lambda m: "%s %s г."%(months.get(int(zhnum(m.group(2))), "%s месяц"%zhnum(m.group(2))), zhnum(m.group(1))))

    # Дата в виде день-месяц
    months = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
              7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
    find_pattern(u"(\d{1,2})月(\d{1,2})日",
                 lambda m: "%s %s"%(m.group(2), months.get(int(m.group(1)), "%s месяца"%m.group(1))))

    # Дата в виде день-месяц прописью
    find_pattern(u"([一二三四五六七八九十]{1,2})月([一二三四五六七八九十]{1,3})[日号]",
                 lambda m: "%s %s"%(zhnum(m.group(2)), months.get(int(zhnum(m.group(1))), "%s месяца"%zhnum(m.group(1)))))

    # Даты в виде год-год
    find_pattern(u"(\d{1,4}-\d{1,4})年",
                 lambda m: "%s гг."%(m.group(1)))

    # Время прописью
    find_pattern(u"(?:((?:上午)|(?:早上))|((?:下午)|(?:晚上)))?([〇一二三四五六七八九十]{1,2})点([〇一二三四五六七八九十]{1,3})分",
                 lambda m: "{0:0=2}:{1:0=2}{2}".format(int(zhnum(m.group(3).encode('utf-8'))),
            int(zhnum(m.group(4).encode('utf-8'))),"AM" if m.group(1) else ("PM" if m.group(2) else "")))

    # Дробные числа с плавающей точкой
    find_pattern(u"([〇一二两三四五六七八九十百千万亿]+)点([〇一二两三四五六七八九十百千万亿]+)",
                 lambda m: "%s.%s"%(zhnum(m.group(1).encode('utf-8')), zhnum(m.group(2).encode('utf-8'))))

    # Дробные числа без плавающей точки
    find_pattern(u"([〇一二两三四五六七八九十百千万亿]+)又([〇一二两三四五六七八九十百千万亿]+)分之([〇一二两三四五六七八九十百千万亿]+)",
                 lambda m: "%s %s/%s"%(zhnum(m.group(1).encode('utf-8')), zhnum(m.group(3).encode('utf-8')), zhnum(m.group(2).encode('utf-8'))))

    # Простые дроби
    find_pattern(u"((?<!又)[〇一二两三四五六七八九十百千万亿]+)分之([〇一二两三四五六七八九十百千万亿]+)",
                 lambda m: "%s%s"%(zhnum(m.group(2).encode('utf-8')), "/"+zhnum(m.group(1).encode('utf-8')) if m.group(1)!=u"百" else " %")
                 )

    # Цифры с множителем 1000, 10000...
    find_pattern(u"(\d+(?:\.\d+)?)(?:\s+)?([仟万萬亿億兆])",
                 lambda m: "{:,}".format(
                     eval(m.group(1)+"*"+{u'仟':'1000', u'万':'10000', u'萬':'10000', u'亿':'100000000', u'億':'100000000', u'兆':'1000000000000'}[m.group(2)])
                 ))
    # Наименование разделов документации 第一部分 часть 1, 第九十九条 статья 99, 第十二章 глава 12, 第二节 подраздел 2
    parts={u"部分":u"часть", u"条":u"статья", u"章":u"глава", u"节":u"раздел"}
    find_pattern(u"第(?:(\d{1,3})|([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰千仟]+))((?:部分)|[条章节])",
                 lambda m: "%s %s"%(parts.get(m.group(3)), m.group(1) if m.group(1) else zhnum(m.group(2))))

    # Целые числа больше 10
    find_pattern(u"[〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰千仟万萬亿兆]{2,}",
                 lambda m: zhnum(m.group(0).encode('utf-8')
                 ))

    # Нумерованные списки
    find_pattern(u"(?m)^([\d.]+)[、]",
                 lambda m: "%s. "%m.group(1)
                 )

    return slovdict


def tokenizer(txt):
    """Разбирает на отдельные иеролифы(символы) или их возможные сочетания(состоящие из 1 до n-1 символов)
    Формат вывода: {"key1":{pos:[[start1,end1], [start2,end2], ..], value: "value1"}, "key2":{pos:[[start1,end1], [start2,end2], ..], value: "value2"}}
    key - часть текста для поиска в словаре
    value - предварительно полученное значение для известных форматов (цифры, даты и т.д.), может отсутствовать
    pos - диапазоны нахождения ключа
    """
    txt = txt.decode('utf-8')
    re_pass = re.compile(u"[-\ 。.,\[\]\"а-яёА-ЯЁa-zA-Z0-9（）【】～！”“；：《》<>=+\n\s_/]")#Группа символов, содержащая один из символов в скобках, пропускается
    maxn = 20  #Макс.длина слова
    n = len(txt)  #Длина текста
    l = n if n < maxn else maxn
    numbers=pretranslater(txt)
    slovdict = Storage()
    for i in range(1, l+1):
        for j in range(i):
            for x in re.finditer(r".{%d}"%(i), txt[j:], re.S):
                key = x.group(0)
                pos=[x.start() + j, x.end()+j]
                if set(range(*pos)).isdisjoint(numbers.scope)==False or re_pass.search(key): continue
                key=key.encode('utf-8')
                if key in slovdict:
                    slovdict[key].pos.append(pos)
                else:
                    slovdict[key] = Storage(pos=[pos])
    numbers.pop('scope')
    slovdict.update(numbers)
    if not slovdict.keys():
        slovdict[txt.encode('utf-8')] = Storage(pos=[[0, len(txt)]])
    return slovdict


def bw_parser(text, cross=False, fullmatch_return=False):
    """Выдает объект, содержащий найденные слова. Если cross=True, то показывать слова на пересечении
    Формат вывода:
    {text: "слово1слово2кусок1слово2слово1кусок2"，
    record: False,//Номер записи в базе, если весь текст найден
    bypass: [{id:xxx, spans:[[start1, end1], [start2, end2]]}, {...}, ...],//Список слов, для которых указано пропускать в пословном (bywords_out)
    chunks: [{id:1, start:0, end:6, i:0}, {id:2, start:6, end:12 i:1}, {id:'с1', start:12, end:18 i:2}, ...],//Куски с id в данных и индексом начала и индексом конца+1, если текста нет в базе, то id начинается с "с"+номер неразобранного куска
    data: {1: {slovo:'slovo', pinyin:'pinyin', perevod:'perevod', use_short = True, bywords_short = 'short perevod', choiselist:['var1','var2'], bywords_out: False},
        2: {slovo:'slovo', pinyin:'pinyin', perevod:'perevod', use_short = False, bywords_short = '', choiselist:['var1','var2'], bywords_out: False},
        'с1': {slovo:'кусок 1', pinyin:'', perevod:'', use_short = False, bywords_short = '', choiselist:[]},
        'с1': {slovo:'кусок 2', pinyin:'', perevod:'', use_short = False, bywords_short = '', choiselist:[]}
        }//Объект данных по словам, id которых указанно в chunks, record, bypass
    """
    db = current.db
    slovar = db.slovar
    result = Storage(text = text, record=False, data = Storage(), chunks=[], bypass=[])
    ##############               Прямой поиск                ################
    row = db(slovar.slovo == text).select().first()
    if row:
        # Корректировка списка вариантов
        row=row_corrector(row)
        result.record=row.id
        result.data[row.id] = Storage(
            id = row.id,
            slovo=row.slovo,
            pinyin = row.pinyin,
            perevod = row.perevod,
            use_short = row.use_short,
            bywords_short = row.bywords_short or '',
            choiselist = row.choiselist,
            bywords_out = row.bywords_out
        )
        if fullmatch_return:
            result.chunks.append(Storage(
                    id=row.id,
                    start = 0,
                    end = len(text.decode('utf-8'))
                ))
            return result
    ##############            Пословный поиск                ################
    # Если текста в словаре нет, то разбиваем текст на слова
    # Словарь из комбинаций иероглифов в ключах и позициями данной комбинации в значениях (кортеж)
    slovdict = tokenizer(text)

    if text in slovdict:
        if not slovdict[text].value:
            slovdict.pop(text)

    # Заготовка в виде экземпляра Storage, ключ - позиция первого символа слова в тексте, значение - объект представления слова (экз. Storage)
    for key, keyvalue in slovdict.items():
        if keyvalue.value:
            cid='d%d'%hash(keyvalue.value)
            value=keyvalue.value
            result.data[cid] = Storage(id=cid, slovo=key, pinyin='', perevod=value, use_short=False, bywords_short='', choiselist = [])
            result.chunks.extend([Storage(id=cid, start=x[0], end=x[1]) for x in keyvalue.pos])
            continue
        # Запрашиваем в базе
        row = db(slovar.slovo == key).select().first()
        #if row == None or row.bywords_out:continue#Если нет или задано исключение, то берем следущее слово
        if row == None:
            continue
        # Корректировка списка вариантов
        row=row_corrector(row)
        # Слово есть в базе, добавим его в result.data
        result.data[row.id] = Storage(
            id = row.id, slovo = row.slovo,
            pinyin = row.pinyin,
            perevod = row.perevod,
            use_short = row.use_short,
            bywords_short = row.bywords_short or '',
            choiselist = row.choiselist,
            bywords_out = row.bywords_out
        )
        #Если указано пропускать данное слово, то перейдем к следующему
        if row.bywords_out:
            result.bypass.append(Storage(id=row.id, spans=keyvalue.pos))
            continue
        #Пропуск запрещен, значит добавляем позиции данного слова в result.chunks
        #Слово может несколько раз встречаться в тексте, поэтому пройдемся по этим местам и запишем координаты
        for start,end in keyvalue.pos:
            # Подготовим объект, представляющий слово (со всем содержимым экземпляра Row в переменной row, плюс атрибуты позиций и длина)
            result.chunks.append(
                Storage(
                    id = row.id,
                    start = start,
                    end = end
                ))

    # Если нет составляющих, то возвращаем результат с неразобранным текстом, либо с найденным текстом
    if len(result.chunks) == 0:
        if not result.record:
            cid='c%d'%hash(text)
            result.chunks.append(Storage(id=cid, start=0, end=len(text.decode('utf-8'))))
            result.data[cid] = Storage(id = cid, slovo = result.text,
                                       pinyin = '', perevod = result.text,
                                       use_short = False, bywords_short = '',
                                       choiselist = [])
        return result

    ##############Разбор кусков текста, которых нет в словаре################
    # Составим из result.chunks множество занятых позиций
    scope=set()
    for s in result.chunks:
        scope|=set(range(s.start, s.end))
    # Составим список индексов для тех символов, которых нет в множестве занятых позиций
    #Для примера, допустим список индексов получился [1,2,3,5,7,8,9,15,16,18,20,25]
    noparse = [i for i in range(len(text.decode('utf-8'))) if not i in scope]
    # Преобразуем к виду [[1, 2, 3], [5], [7, 8, 9], [15, 16], [18], [20], [25]], то сгруппируем есть по непрерывным последовательностям для этого
    noparse=''.join(['|' if x in noparse else '-' for x in list(range(max(noparse)+1))] if noparse else [])
    noparse=[list(range(x.start(), x.end())) for x in re.finditer('[|]+', noparse)]
    # Вырежем из текста неразобранные куски и поместим их в данные и в список кусков результата
    for x in noparse:
        start = x[0]
        end = x[-1] + 1
        txt = text.decode('utf-8')[start:end].encode('utf-8')
        #txt = text[start:end]
        cid='c%d'%hash(txt)
        result.data[cid] = Storage(id=cid, slovo=txt, pinyin='', perevod=txt, use_short=False, bywords_short='', choiselist = [])
        result.chunks.append(Storage(id=cid, start=start, end=end))
    #result.chunks=[Storage(start=0, end=4),Storage(start=4, end=10),Storage(start=4, end=7),Storage(start=6, end=8),Storage(start=8, end=10),Storage(start=10, end=15),Storage(start=13, end=16),Storage(start=14, end=18),Storage(start=18, end=21),Storage(start=14, end=18),Storage(start=16, end=17),Storage(start=15, end=16),Storage(start=17, end=18),Storage(start=19, end=20),Storage(start=20, end=21)]
    # Отсортируем по стартовым позициям, так чтобы более длинные с одним началом шли первыми
    result.chunks.sort(key = lambda x:+(x.start-x.end))# Сортируем по убыванию длины слова
    result.chunks.sort(key = lambda x:x.start)# Сортируем по возрастанию начала слова
    # Найдем ключи с вложенными диапазонами
    # Вспомогательный список из множеств - раскрытых диапазонов позиций символов слова
    nabor=[set(range(x.start,x.end)) for x in result.chunks]
    for i,x in enumerate(nabor):
        for j,y in enumerate(nabor):
            if result.chunks[i]==False or i==j: continue
            if cross==True: # Если задано оставлять слова на стыке
                if y<=x: result.chunks[j]=False
            if cross==False: # Если слова на стыке отключены
                if len(x.intersection(y)):
                    result.chunks[j]=False
    result.chunks=[x for x in result.chunks if x!=False]
    ###########################################################################
    # Подчистим result.data
    idlist=[x.id for x in result.chunks]
    if result.record: idlist.append(result.record)
    result.data=Storage({id:result.data[id] for id in idlist})
    return result
