#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.storage import Storage
import re
from BeautifulSoup import BeautifulSoup as bs
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

reg_ref=re.compile(r"\[ref\](.*?)\[\/ref\]")#A()
reg_c=re.compile(r"\[c\](.*?)\[\/c\]")#SPAN()
colors=['green','brown','violet','red','crimson','black','gray']
reg_ccolors={color:re.compile(r"\[c %s\](.*?)\[\/c\]"%color) for color in colors}#SPAN()
reg_i=re.compile(r"\[i\](.*?)\[\/i\]")#I()
reg_b=re.compile(r"\[b\](.*?)\[\/b\]")#B()
reg_p=re.compile(r"\[p\](.*?)\[\/p\]")#I()
reg_skobki=re.compile(r"(\(.*\))")#SPAN()
reg_numerate=re.compile(r"([^\d])(\d{1,2})[).]([^\d])")#SPAN()
reg_alfavite=re.compile(u"([^a-zа-я]+)([abcdeабвгд])\)")#SPAN()
reg_m=re.compile(r"\[m([1-4])\](.*?)\[\/m\]")#DIV()
reg_ex=re.compile(r"\[ex\](.*?)\[\/ex\]")#DIV()
reg_mi=re.compile(r"(\[m[1-4]\])")
reg_apndx=re.compile(r"\[apndx\](.*?)\[\/apndx\]")

def normalise_perevod(text):
    """Функция устраняет незакрытые или неоткрытые тэги (то, что в квадр.скобках [команды, метки])
    синтаксиса словарной статьи, а также преобразует кодировку в 'utf-8' во избежание проблем с кодировкой"""
    if not text: return ''
    #perevod=unicode(text, 'utf-8') if not isinstance(text,unicode) else text
    perevod=text
    #Удаляем знаки переноса на новую строку
    perevod=perevod.replace("\n","")
    #Эранируем управл. символы html, если они есть в тексте
    perevod=perevod.replace("&","&amp;")#Амперсанд
    perevod=perevod.replace(">","&gt;")#Больше
    perevod=perevod.replace("<","&lt;")#Меньше
    #perevod=perevod.replace("'","&apos;")#Апостроф
    #perevod=perevod.replace('"',"&quot;")#Кавычка
    #Очищаем или преобразуем некоторые конструкции синтаксиса словаря
    perevod=perevod.replace("[m1]-----[/m]","[m1]")
    perevod=perevod.replace("[i];[/i]",";")
    perevod=perevod.replace("[i].[/i]",".")
    perevod=perevod.replace("[i] [/i]"," ")
    perevod=perevod.replace("[*][ex]","[ex]").replace("[/ex][/*]","[/ex]")
    perevod=perevod.replace("[*]","[ex]").replace("[/*]","[/ex]")
    perevod=perevod.replace("[e]","[ex]").replace("[/e]","[/ex]")
    perevod=perevod.replace(u"①","[m1]1)").replace(u"②","[m1]2)").replace(u"③","[m1]3)").replace(u"④","[m1]4)")
    #Перенос скобок во внутрь тэгов
    #perevod=perevod.replace("([i]","[i](").replace("[/i])",")[/i]")
    #perevod=perevod.replace("([c]","[c](").replace("[/c])",")[/c]")
    #perevod=perevod.replace("([b]","[b](").replace("[/b])",")[/b]")
    #Проверка соблюдения правил вложенности
    perevod1=[]#Список отбработанных частей
    #разобъем строку по закрывающему тэгу абзаца "[/m]"
    for x in perevod.split("[/m]"):
        x=x.strip()#Подрезаем кончики
        if x=="":continue#Исключаем пустые
        x=reg_mi.sub(r"[/m]\1",x)#Заменяем открывающие тэги абзаца на тот же тэг с закрывающим тэгом в начале
        for y in x.split("[/m]"):#разобъем строку по закрывающему тэгу абзаца "[/m]"
            y=y.strip()#Подрезаем кончики
            if y=="":continue#Исключаем пустые
            if reg_mi.search(y)==None:y="[m1]"+y#Если открывающего тэга абзаца нет, то ставим его в начале
            perevod1.append(y)#Добавляем в список отбработанных частей
        # В итоге полученный список perevod1 должен содержать элементы начинающиеся с откр.тэгов абзаца [m1]-[m4]
        # Добавляем закрывающий тэг абзаца [/m] со знаком переноса строки \n (для рег.выраж.)
        # в конец каждого элемента списка, сцепляем элементы и возвращаем строку
    return "".join([x+"[/m]\n" for x in perevod1 if x.strip()!=""])

def repres_perevod(perevod,*args):
    """Функция создает html представление синтаксиса словарной стати, путем замены соответствующих тэгов"""
    #Нормализуем словарную статью
    perevod=normalise_perevod(perevod)
    perevod=reg_alfavite.sub(r"\1<span>\2.</span>",perevod)#Выделяем буквенное перечисление
    perevod=reg_numerate.sub(r"\1<span>\2.</span>\3",perevod)#Выделяем нумерованное перечисление
    perevod=reg_skobki.sub(r"<span>\1</span>",perevod)#Всё что в скобках обозначаем как span
    #Текст может содержать тэги ссылок, создадим ссылку на действие slovo контроллера slovar для обработки нажатия этих ссылок
    link=URL(c="slovar",f="slovo")
    perevod=reg_ref.sub(r"<a href='%s\?slovo=\1' slovo='\1'>\1</a>"%link,perevod)#Заменяем тэги ссылок [ref] на html тэги
    perevod=reg_c.sub(r"<span>\1</span>",perevod)#Заменяем тэги выделения на html тэги
    for color,reg_ccolor in reg_ccolors.items():
        perevod=reg_ccolor.sub(r"<span class='%s'>\1</span>"%color,perevod)#Заменяем тэги выделения цветом на html тэги
    perevod=reg_i.sub(r"<i class='green'>\1</i>",perevod)#Заменяем тэги курсива [i] на html тэги
    perevod=reg_p.sub(r"<i class='green'>\1</i>",perevod)#Заменяем тэги пометок [p] на html тэги
    perevod=reg_b.sub(r"<b>\1</b>",perevod)#Заменяем тэги жирным [b] на html тэги
    perevod=reg_m.sub(r"<div class='m\1'>\2</div>",perevod)#Заменяем тэги абзацев [m1~4] на html тэги
    perevod=reg_ex.sub(r"<div class='ex'>\1</div>",perevod)#Заменяем тэги примера [ex] на html тэги
    perevod=reg_apndx.sub(r"<div class='apndx'>\1</div>",perevod)
    perevod=perevod.replace("\[","<span>[")#Заменяем экранирование спецсимвола синтаксиса словарной статьи
    perevod=perevod.replace("\]","]</span>")#Заменяем экранирование спецсимвола синтаксиса словарной статьи
    perevod=re.sub(r"<div class='m[1-4]'>\s*</div>","",perevod)#Удаляем пустые блоки(содержащие пробельные символы)

    return TAG(bs(perevod).renderContents())#Создаем экземпляр класса TAG путем парсинга текста, предварительно пропустив его через BeautifulSoup

def cut_perevod(perevod,*args):
    """Функция убирает примеры из html представления словарной статьи"""
    tagObj=repres_perevod(perevod)#Возвращает уже объект класса TAG, а не текст
    tagObj.elements('div.ex', replace=None)#Убираем примеры
    tagObj.elements('div',_class=re.compile(r'm[1-4]'),replace=lambda div: "" if div.flatten().strip()=="" else div)#Удаляем пустые блоки
    return tagObj

def split_perevod(div,slovo):
    """Разбивает текст в блоках div сласса m[1-4] на варианты перевода в зависимости от вида разделителя ("," или ";") и возвращает элементы списка LI"""
    text=div.flatten().strip()
    sep=","
    if ";" in text or re.search(u"[,，、。]",slovo):sep=";"
    return CAT(*[LI(x.strip()) for x in text.split(sep) if x.strip()!=""])

def sokr_perevod(perevod,slovo,*args):
    """Функция создает список вариантов перевода"""
    #if not isinstance(slovo,unicode):slovo=unicode(slovo, 'utf-8')
    tagObj=repres_perevod(perevod)#Возвращает уже объект класса TAG, а не текст
    perevod_po_silke=[]
    for ref in tagObj.elements('a'):
        ref_perevod=current.db(current.slovar.slovo==ref["_slovo"]).select(current.slovar.perevod).first()
        if ref_perevod!=None:
            perevod_po_silke.append(repres_perevod(ref_perevod.perevod))
    tagObj.append(CAT(*perevod_po_silke))
    tagObj.elements('a',replace=None)
    tagObj.elements('div.ex', replace=None)#Убираем примеры
    tagObj.elements('i', replace=None)#Убираем курсив
    tagObj.elements('span', replace=None)#Убираем разрывы
    tagObj.elements('b', replace=None)#Убираем жирный
    tagObj.elements('div',_class=re.compile(r'm[1-4]'),replace=lambda div: "" if div.flatten().strip()=="" else div)#Удаляем пустые блоки

    tagObj.elements('div',_class=re.compile(r'm[1-4]'),replace=lambda div: split_perevod(div,slovo))#Непустые блоки преобразуем в элементы списка
    values=[]
    for value in [x.flatten().strip() for x in tagObj.elements('li')]:
        if not value in values and not re.search(u"[。（）【】～！”“；：《》一-龥]",value, 'utf-8',re.U): values.append(value)
        #if not value in values and not re.search(u"[。（）【】～！”“；：《》一-龥]",unicode(value, 'utf-8'),re.U): values.append(value)
    #tagObj=UL(values)
    return values#tagObj


def splitby(spisok,ngroup):
    """Разбивает список на подсписки из заданного числа элементов"""
    newspisok=[]
    i=1
    x=[]
    while spisok!=[]:
        if i>ngroup:
            newspisok.append(x)
            x=[]
            i=1
        x.append(spisok.pop(0))
        i+=1
        if spisok==[]:newspisok.append(x)
    return newspisok



reg_pinyin=re.compile(u"\[b\]([^一-龥]*?)\[/b\]",re.U)#B()
def extract(perevod):
    """Извлечение примеров из словарной статьи"""
    a=normalise_perevod(perevod)
    exlist=[x for x in reg_ex.findall(a)]#Список примеров

    #Предобработка
    exlist=[x.replace("\[","\{").replace("\]","\}") for x in exlist]
    exlist=[re.sub(u"\[([ a-z]+)\]([一-龥]*?)\[/([ a-z]+)\]",r"{\1}\2{/\3}",x,flags=re.U) for x in exlist]

    #Добавляем разделитель "\n " перед началом русского текста
    exlist=[re.sub(u"""((?:\[[bcip]*?\].*?\[/[bcip]*?\]|[ \{«(\\\[\]cip*°0-9-])*?[а-яёА-ЯЁ])""",r"\n \1",x,count=1,flags=re.U) for x in exlist]
    #Добавляем разделитель "\n " перед началом английского текста, если нет русского текста
    exlist=[x if re.search(u"[а-яёА-ЯЁ]",x,re.U) else re.sub(u"""((?:\[[bcip]*?\].*?\[/[bcip]*?\]|[ \{«(\\\[\]cip*°0-9-])*?[a-zA-Z])""",r"\n \1",x,count=1,flags=re.U) for x in exlist]
    #Добавляем разделитель "\n " в конце, если нет ни русского, ни английского текста
    exlist=[x if re.search(u"[а-яёА-ЯЁa-zA-Z]",x,re.U) else x+"\n " for x in exlist]

    #Постобработка
    exlist=[x.replace("\{","\[").replace("\}","\]") for x in exlist]
    exlist=[re.sub(u"{([ a-z]+)}([一-龥]*?){/([ a-z]+)}",r"[\1]\2[/\3]",x,flags=re.U) for x in exlist]

    #Разбивка
    exlist1=[]
    for x in exlist:
        slovo,perevod=x.split("\n ")
        pinyin=";".join([y for y in reg_pinyin.findall(perevod)]+[z for z in reg_pinyin.findall(slovo)]).replace("("," ").replace(")"," ")
        perevod=reg_pinyin.sub(r"",perevod)
        slovo=reg_pinyin.sub(r"",slovo)
        exlist1.append(Storage(slovo=slovo.strip(),pinyin=pinyin.strip('\t :-;.'),perevod=perevod.strip('\t :-;.,')))
    return exlist1


### Добавлено 09.11.2017г. ####
def bb2delta(txt):
    """Функция преобразования текста в Дельта формат"""
    # TRANSFORM = {'*':'star', 'i':'italic', 'b':'bold', 'e':'ex', 'c':'color', 'ref':'link', 'p':'tag', 'apndx':'m', 'hr':'divider'}
    bl_tags = ['m', 'hr'] # list(map(lambda key: TRANSFORM.get(key, key), ['m', 'hr']))
    bl_class = ['*', 'ex'] # list(map(lambda key: TRANSFORM.get(key, key), ['*', 'ex']))
    RE_BB_TXT_GROUPS = re.compile(r"(^(?:\[[-*\/\s\w]+\])*)(.*)")  # Делит строку на группу с тэгами и группу с текстом
    RE_BB_TAG = re.compile(r"(?<!\\)\[(\/?)([a-z*]+)\s?([\w\s]*?)(?<!\\)\]")  # Определяет параметры тэга - тип, имя, атрибут
    blocks = [Storage(childs=[], attrs=Storage())]
    txt = txt.replace("[m1]-----[/m]", "[hr][/hr]")
    for match in re.finditer(r"(?m)(?:(?:\[[-*\/\s\w]+\])+.*?|(?:.+?))(?=\[[-*\/\s\w]+\]|$)", txt):
        m = RE_BB_TXT_GROUPS.match(match.group(0))
        text = m.group(2) or ''
        tag_group = m.group(1) or ''
        text = text.replace("\[", "[").replace("\]", "]")
        iattrs = Storage(blocks[-1].childs[-1].attrs.copy()) if blocks[-1].childs else Storage()
        for t in RE_BB_TAG.finditer(tag_group):
            open = t.group(1) == ""
            tag = t.group(2)
            value = t.group(3) or True
            if open and tag == 'c' and value == True:
                value = 'green'
            #tag = TRANSFORM.get(tag, tag)
            if tag in bl_tags:
                iattrs = Storage()
                if open:
                    if blocks[-1].childs:
                        blocks.append(Storage(childs=[], attrs=Storage()))
                    blocks[-1].attrs[tag] = value
                else:
                    blocks.append(Storage(childs=[], attrs=Storage()))

            elif tag in bl_class:

                if open:
                    blocks[-1].attrs[tag] = value

            else:
                if open:
                    iattrs[tag] = value
                elif iattrs[tag]:
                    iattrs.pop(tag)

        if text:
            blocks[-1].childs.append(Storage(txt=text, attrs=iattrs))
    return blocks


def get_choices(text):
    """Извлекает варианты перевода из текста словаря, на входе - форматир. текст, на выходе - список"""
    choices = ""
    for block in bb2delta(text):
        if set(block.attrs.keys()).isdisjoint(set(['*', 'ex'])):
            lines=""
            for child in block.childs:
                if not child.attrs or len(child.txt.decode()) == 1:
                    lines += child.txt
            choices += "\n%s"%re.sub(r"[,;]", "\n", lines)
    choices = choices.replace("①", "\n").replace("②", "\n").replace("③", "\n").replace("④", "\n")  # Убираем нумерацию круглыми цифрами
    choices = re.sub(u"[一-龥，、，。（）【】～！”“；：《》○·‧？「」]+", "", choices.decode()).encode()  # Убираем кит. иерогл.
    choices = re.sub(r"(?m)^\d{1,2}[.]", "", choices)  # Убираем цифру с точкой в начале
    choices = re.sub(r'(?m)^[-?\s).*:;"=\]]+', "", choices)  # Убираем пробел, закр. скобку, точку и звездочку в начале
    choices = re.sub(r'(?m)[-\s(.*:;"=\[]+$', "", choices)  # Убираем дефис, пробел, откр. скобку, точку и звездочку в конце
    choices = re.sub(r"(?m)\s?\(.*?(?:\)+|$)", "", choices)  # Убираем обе скобки или все что после откр. скобки
    choices = re.sub(r"(?m)^.*?\)+\s?", "", choices)    # Убираем все что перед закр. скобкой
    choices = re.sub(r"(?m)[IVX*]+\s?", "", choices)  # Убираем нумерацию римскими цифрами вместе с пробелом
    choicelist=[]
    for x in choices.split("\n"):
        x=x.strip()
        if x and x not in choicelist:
            choicelist.append(x)
    return choicelist


def perevod_represent(text, *args, **vars):
    if not isinstance(text, (str, unicode)):
        return ""
    trans_table=dict(i=I, b=B, c=SPAN, ref=A, p=SPAN)
    container=DIV(_class="bkrs-ru")
    for block in bb2delta(text):

        if block.attrs.hr:
            container.append(HR(_class="bkrs-divider"))
            continue

        p=P()
        for k, v in block.attrs.items():
            k="bkrs-star" if k == "*" else ("bkrs-%s-%s"%(k, v) if isinstance(v, (str, unicode)) else "bkrs-%s"%k)
            p.add_class(k)

        for inline in block.childs:
            child=inline.txt
            for k, v in inline.attrs.items():
                child=trans_table.get(k, SPAN)(child)
                if isinstance(v, (str, unicode)):
                    child.add_class("bkrs-%s-%s"%(k, v))
                else:
                    child.add_class("bkrs-%s"%k)
                if k=="ref":
                    child['_href']=inline.txt
            p.append(child)

        container.append(p)

    return container


#### PINYIN ####
from pypinyin import core, pinyin, lazy_pinyin

"""
>>> pinyin('中心')
[['zhōng'], ['xīn']]
>>> pinyin('中心', heteronym=True)  # Задействовать режим выдачи иероглифов с несколькими вариантами произношения (омографы)
[['zhōng', 'zhòng'], ['xīn']]
>>> pinyin('中心', style=pypinyin.FIRST_LETTER)  # Настройка фонетического стиля
[['z'], ['x']]
>>> pinyin('中心', style=pypinyin.TONE2, heteronym=True)
[['zho1ng', 'zho4ng'], ['xi1n']]
>>> pinyin('中心', style=pypinyin.BOPOMOFO)  # Фонетический стиль - чжуи́нь или бопомофо
[['ㄓㄨㄥ'], ['ㄒㄧㄣ']]
    >>> pinyin('中心', style=pypinyin.CYRILLIC)  # Фонетический стиль - запись кириллицей по системе Палладия
[['чжун1'], ['синь1']]
>>> lazy_pinyin('中心')  # Без учета омографов
['zhong', 'xin']
"""
PINYIN_STYLE = {
    'NORMAL': 0,
    'TONE': 1,
    'TONE2': 2,
    'TONE3': 8,
    'INITIALS': 3,
    'FIRST_LETTER': 4,
    'FINALS': 5,
    'FINALS_TONE': 6,
    'FINALS_TONE2': 7,
    'FINALS_TONE3': 9,
    'BOPOMOFO': 10,
    'BOPOMOFO_FIRST': 11,
    'CYRILLIC': 12,
    'CYRILLIC_FIRST': 13,
}

PINYIN_STYLES = {
    0: 'normal',
    1: 'tone',
    2: 'tone2',
    8: 'tone3',
    3: 'initials',
    4: 'first_letter',
    5: 'finals',
    6: 'finals_tone',
    7: 'finals_tone2',
    9: 'finals_tone3',
    10: 'bopomofo',
    11: 'bopomofo_first',
    12: 'cyrillic',
    13: 'cyrillic_first'
}

def getpinyin(txt, style=1, heteronym = False, lazy = True):
    """Функция, изменяющая формат вывода библиотеки pypinyin в более удобную для сериализации форму
    Аргумент style может быть ключем из PINYIN_STYLE или числом, допускается задавать несколько стилей в списке
    Аргумент heteronym - выдавать или не выдавать несколько вариантов произношения, при этом даже если вариант 1, то он все равно будет в списке
    Аргумент lazy - включает или отключает выдачу пиньина в виде строки, если включен,
    то heteronym ставится принудительно, при этом выдается список строк, а не список списков
    Пиньин идет всегда в виде списка (строк или списков вариантов), а неразобранный текст ввиде строк
    Например, если на входе: txt=中心abc, style=[1, 2], heteronym=False, lazy=True,
    то на выходе будет: {words: ["中心", "abc"], tone: [[zhōng, xīn], "abc"], tone3:[['zho1ng','xi1n'], "abc"]}
    words - список слов
    tone - список в тоновом стиле tone, состоящий из разобранных слов (в виде списка из пиньин произношений) и неразобранных слов (просто текст)
    tone3 - то же самое, что и для tone, только в стиле tone3
    """
    txt=txt.decode('utf-8')
    style=style if isinstance(style, (list, tuple)) else [style]
    seglst=core.seg(txt)
    pyoutput=Storage(words=seglst)
    for s in style:
        if not isinstance(s, int):
            s=PINYIN_STYLE.get(s.upper(), 1)
        key=PINYIN_STYLES[s]
        pyoutput[key]=[]
        for word in seglst:
            if heteronym or not lazy:
                py=pinyin(word, style=s, heteronym=heteronym)
                pyoutput[key].append(word if word in py[0] else py)
            else:
                py=lazy_pinyin(word, style=s)
                pyoutput[key].append(word if word in py else py)
    return pyoutput
