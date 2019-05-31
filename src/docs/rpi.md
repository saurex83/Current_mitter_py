# Настройка RPI


## ip адресс
В офисе для отладки RPI на 192.168.1.234

## Подключение диска RPI по ssh
'''sh
sshfs mitter@192.168.1.234:/home/mitter/ /home/saurex/Projects/cmservice/
'''

## Пользователь
Все программы работают под пользователем
>login:mitter
>passw:mitter
Пользователь состоит в группах:
* sudo
* root
* postgress
* dialout (доступ к ttyAMA0)

## Требуемые приложения для работы curren mitter
* postgresql
* python3.5

## Программа cmservice 
Работает в виртуальном окружении Python

