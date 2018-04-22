#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon.globals import current
from gluon.storage import Storage
from gluon.fileutils import listdir
from gluon.html import URL
import gluon.serializers as serializers
from functools import wraps
import os, sys, locale


class Vue(Storage):
    """Класс, обеспечивающий работу с компонентами Vue
    Для использования необходимо создать экземпляр данного класса в модели или контроллере.
    После создания экземпляра все функции в контроллере оборачиваются декоратором share для выдачи однофайловых компонентов.
    """
    _folder=''
    _components = []


    def __init__(self, *args, **vars):
        # Оборачиваем декоратором share все функции в контроллерах
        current.response._caller = lambda f: self.share(*args, **vars)(f)()


    @classmethod
    def search_components(cls):
        """Функция поиска компонентов Vue в папке контроллера"""
        request = current.request
        views_folder = os.path.join(request.folder, 'views')
        controller_folder = os.path.join(views_folder, request.controller)
        components = listdir(controller_folder, '.+\.vue$')
        components = [os.path.abspath(os.path.join(controller_folder, x)) for x in components]
        components = [x.decode(locale.getpreferredencoding()).encode() for x in components]
        components = [(x.split(os.path.sep)[-1][:-4], os.path.relpath(x, views_folder)) for x in components]
        return dict(components)


    @classmethod
    def share(cls, key='@vue.share'):
        """Декоратор с параметрами для выдачи однофайлового компонента Vue
           Компонет выдается если первый аргумент в URL равен key,
           либо в запросе задан заголовок "vue-component-file"
           со значением, сожержащим путь к файлу компонента.
           Компонент не выдается если функция контроллера возвращает текст.
        """
        request = current.request
        response = current.response

        class decorator(object):
            """Собственно класс декоратора для выдачи однофайлового компонента Vue"""
            def render(self, vars=dict()):
                    if isinstance(vars, dict):
                        return response.render(response.view, vars)
                    return vars


            def __call__(self, action):
                @wraps(action)
                def wrapper():
                    if request.env.http_vue_component:
                        args = [key]+request.env.http_vue_component_file.split('/')
                    else:
                        args = request.env.path_info.split('/')
                        args = args[4:] if request.application in args else args[3:]
                    if len(args) >1:
                        if args.pop(0) == key:
                            if args[-1][-4:]!='.vue':
                                args[-1] +='.vue'
                            args = ['..' if x=='__' else x for x in args]
                            response.view = os.path.join(*args)
                            request.extension='vue'
                            response.postprocessing.append(self.render)
                    return action()

                return wrapper

            def __repr__(self):
                return serializers.json({k:'url:%s'%URL(args=[key]+v.split(os.path.sep)) for k, v in cls.search_components().items()})

        return decorator()


    @staticmethod
    def switch(*args, **vars):
        """Декоратор для функций в контроллерах, позволяющий переключить
        декорируемую функцию на другую функцию, например, на функцию
        выдачи json данных при выполнении некоторых условий.
        caller - замещающая функция или какие то данные
        trigger - условие вызова или функция, возвращающая булево значение.
        send - передать декорируемую функцию к замещающей функции
        json - вернуть в json формате, если caller не является функцией
        """

        class decorator(object):

            def __init__(self, caller=None, trigger=False, send=False, json=False):
                self.caller = caller
                self.trigger = trigger
                self.send = send
                self.json = json

            def __call__(self, _action):
                @wraps(_action)
                def wrapper():
                    trigger =  self.trigger() if callable(self.trigger) else  self.trigger
                    if self.trigger:
                        if callable(self.caller):
                            return self.caller(_action) if self.send else self.caller()
                        else:
                            return current.response.json(self.caller) if self.json else self.caller
                    else:
                        return _action()
                return wrapper
        return decorator(*args, **vars)
