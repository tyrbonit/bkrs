# О приложении bkrs
Приложение разработано на базе фреймворка web2py и является клиент-серверным приложением.
Серверная часть написана на языке python - фреймворк web2py, клиентская часть частично основана на компонентах Vue.js.
Работа клиентской часть в основном протестирована на браузерах, основанных на Google Chrome.
В качестве базы данных используется Postgresql (портативная версия), но возможна любая другая база данных, которая поддерживается web2py.
База данных заполняется словами из dsl словаря с https://bkrs.info/p47. Для транскрипции китайских иероглифов используется питон-библиотека pypinyin, которая была дополнена таблицей Палладия и кириллическим стилем (в последствии это дополнение было принято автором pypinyin).
# Возможности
* Пословный перевод в стиле карточек как на bkrs.info
* Пословный перевод с выдачей вариантов перевода в стиле google translate
* Редактор новых и существующих карточек перевода
* Редактор вариантов перевода
* Сортировка вариантов перевода по частоте использования
* Траснкрипция иероглифов на английском и русском
* Преобразование прописных чисел на китайском языке в цифры
* Преобразование чисел с китайскими множителями (тысяча, 10 тысяч) в простое число
* Преобразование прописи дробных чисел
* Преобразование календарных дат в китайском формате в русский формат
* Преобразование наименований разделов документации (часть, статья, глава, подраздел)
* Преобразование нумерованных списков в китайском формате в русский формат
* Преобразование китайских знаков пунктуации в русский формат.
Также в интерфейсе словаря доступен весь список слов, хранящийся в базе данных с возможностью сортировки, фильтрации и редактирования
# Инициализация приложения
Для работы приложения требуется каркас - фреймворк web2py, куда собственно и устанавливается приложение.
Свежую версию web2py можно скачать с http://www.web2py.com/init/default/download, рекомендуется версия для windows.
После скачивания архив web2py следует распаковать в корень любого диска в папку "web2py", например.
## Запуск web2py
После распаковки web2py_win.zip запустить web2py.exe в папке web2py, в окне приложения придумать пароль администратора, нажать "start server". После запуска откроется браузер на странице приложения по умолчанию - welcome, которое можно изменить в дальнейшем на другое.
## Установка приложения
Установить приложение можно 2-мя способами
* Путем копирования файлов из данного репозитория в созданную папку bkrs в папке приложений web2py\applications\
* Путем автоматической установки специально подготовленного пакета с приложением через веб-интерфейс, для этого необходимо зайти по адресу http://127.0.0.1:8000/admin в секции справа "Upload and install packed application" ввести название bkrs (или любое другое по желанию) загрузить пакет и нажать установить.
## Подготовка к запуску приложения bkrs
``` Примечание: Для нормальной работы web2py версии 2.16.1 необходимо устранить некоторые "болячки", которые надеюсь будут устранены в последующих версиях: 1. В файле web2py\gluon\languages.py следует изменить строки 113, 117, 121 на return to_bytes(to_unicode(s).upper()), return to_bytes(to_unicode(s).title()) и return to_bytes(to_unicode(s).capitalize()) соответственно. 2. В файле web2py\gluon\packages\dal\pydal\base.py строку 403 изменить на credential_decoder = lambda cred: unquote(cred). После изменения следует перезагрузить web2py. ```

Для функционирования bkrs необходимо дополнительно запустить сервер базы данных. Рекомендуется PostgreSQLPortable, который после скачивания следует установить и просто запустить PostgreSQLPortable.exe, окно оставить свернутым.

По умолчанию приложение bkrs настроено на работу с данной СУБД, настройка выполняется в файле web2py\applications\bkrs\private\appconfig.ini. При желании строку подключения можно изменить на другую, в зависимости от используемой СУБД.

Для того, чтобы при запуске web2py окно браузера открывалось на приложении bkrs, необходимо открыть в текстовом редакторе файл web2py\examples\routes.parametric.example.py и изменить строку 107 на default_application='bkrs', измененный файл сохранить под именем routes.py в папку web2py\.

