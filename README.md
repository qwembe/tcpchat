# Report

## Исходный код приложения.

Код сервера находится в пакете [tcp/server](https://github.com/qwembe/tcpchat/blob/via_baseserver_sol/tcp/server.py)

Код клиента находится [tcp/client](https://github.com/qwembe/tcpchat/blob/via_baseserver_sol/tcp/client.py)

Пример приложения находится в [main.py](https://github.com/qwembe/tcpchat/blob/via_baseserver_sol/main.py)

``` python
from tcp.client import MyTCPClient, MyClientTCPHandler
from tcp.server import MyTCPServer, MyServerTCPHandler

flag = "server"

if flag == "server":
    with open("syslog", "a") as log:
        with MyTCPServer((HOST, PORT), MyServerTCPHandler, bind_and_activate=True) as server_socket:
            server_socket.myinit(log)
            server_socket.serve_forever()
else:
    with MyTCPClient((HOST, PORT), MyClientTCPHandler, bind_and_activate=True) as client_socket:
        client_socket.serve_forever()

```

## Список используемых библиотек

Для использования не требуются посторонние зависимости<br>
Список ключевых используемых модулей - 
* socketserer
* socket
* threading
* json
* selectors

## Инструкция по установке

### Общее

Чат будет работать везде, где можно установить python 3.6+
Можно добавить модули в virtualenv via pip

```bash
pip install -e git+https://github.com/qwembe/tcpchat#egg=tcpchat
```

### Oracle linux

Сначала необходимо установить python 3.9

```bash
sudo dnf module install -y python39
```

Затем убедится, что есть git

```bash
sudo dnf install -y python39-pip
```

Установим виртуальную среду

```bash
python3.9 -m venv tcpchat
source tcpchat/bin/activate
```

Установка модуля
```bash
python3.9 -m pip install -e git+https://github.com/qwembe/tcpchat#egg=tcpchat
```

## Описание утилит

Модуль __*tcp*__ состоит из двух __*.py__ файлов: server.py & client.py

```
src\
    README.md
    main.py
    setup.py
    tcp\
        __init__.py
        client.py
        server.py
```

В модуле __main.py__ показан пример использования утилит

#### Клиент

Для того, чтобы использовать клиента необходимо импортировать 
следующие объекты - 

```python
from tcp.client import MyTCPClient, MyClientTCPHandler
```


Пример кода для запуска клиента - 

```python
with MyTCPClient((HOST, PORT), MyClientTCPHandler, bind_and_activate=True) as client_socket:
    client_socket.serve_forever()
```

* MyTCPClient - объект, отвечающий за обеспечение соединения
* (HOST, PORT) - адрес сервера {Пример ("localhost", 6060)}
* MyClientTCPHandler - класс, для обработки сообщений

#### Сервер

Импорт -

```python
from tcp.server import MyTCPServer, MyServerTCPHandler
```

Использование -

```python
with open("syslog", "a") as log:
    with MyTCPServer((HOST, PORT), MyServerTCPHandler, bind_and_activate=True) as server_socket:
        server_socket.myinit(log)
        server_socket.serve_forever()
```
* MyTCPServer - Сервер
* (HOST, PORT)
* MyServerTCPHandler - Отвечает за инициацию/поддержку/обработку соединения
* __*.myinit(log)*__ - где log файл - это файл, куда сохраняются сообщения от клиентов

### Пример использования - 
Сперва запускаем сервер 

```commandline
$ python main.py 
Usage python <server|client> <Host> <Port:int>
server (HOST,PORT) set to (localhost,6060)
```
Видим, что он установлен и готов по адресу (localhost,6060)

Подключаем клиента -

```commandline
$ python main.py client                                                     
client (HOST,PORT) set to (localhost,6060)
Enter login: {Ваш логин}
< Server is WAIT4CLIENTS >
< Hi! I'm a menu. Enter a command >
1. Is server available?
2. Who available?
3. Send to available client
4. Send message to all
5. Close connection
```

Первое, что нужно сделать клиенту - это ввести логин (Так Вас будут видеть другие клиенты и сервер)

Сразу после соединения выводится статус сервера : **WAIT4CLIENTS**.Это значит, что сервер ожидает еще одного клиента.

Также сперва пользователь видит меню, которое блокирует получение новых
сообщений от сервера. Чтобы его отключить надо, либо ввести опцию, либо нажать **Enter**

```commandline
< Waiting for messages ... >
< press <enter> to see menu: >
Big Brother  : I'm watching you ...
```

Чтобы отправить сообщение, необходимо узнать логин того, кому вы собираетесь отправить сообщение

```commandline
< Hi! I'm a menu. Enter a command >
1. Is server available?
2. Who available?
3. Send to available client
4. Send message to all
5. Close connection
2
< Waiting for messages ... >
< press <enter> to see menu: >
Users:
duck; Big Brother                   <- Кто доступен
```

Чтобы отправить сообщение, надо ввести логин адресата и само сообщение

```commandline
< Hi! I'm a menu. Enter a command >
1. Is server available?
2. Who available?
3. Send to available client
4. Send message to all
5. Close connection
3
Enter login: duck                    <- логин
Enter message: *quack*               <- сообщение
< Waiting for messages ... >
< press <enter> to see menu: >
< Message have been delivered! >  =) <- сообщение было доставлено
```
Вы увидите сообщение
```commandline
< Message have been delivered! >
или 
< Message sending failure >
```
Если удалось связаться с клиентом серверу и получение от него подтверждение или нет, если что-то пошло не так