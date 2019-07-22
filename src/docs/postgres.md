# Установка
Установка включала в себя сервер и клиент.

Для питона использую пакет алхимии. Сдесь была заморочка с 
установкой - нужен пакет psycopg2 который просто так не ставился

я сделал так:
'''sh
sudo apt-get install python-psycopg2
sudo apt-get install libpq-dev
sudo pip3 install psycopg2
pip3 install psycopg2-binary
pip3 install sqlalchemy-utils
'''

CREATE USER mitter WITH PASSWORD 'mitter';
CREATE DATABASE mitter OWNER mitter;

\dt просмотр списка таблиц
SELECT * FROM "CURDATA";

# Пользователи
Используется пользователь mitter с паролем mitter.

# Время
Временные метки сохранены в UTC с таймзоной

# Команды
select * from "AVERCUR" where "time" > NOW() at time zone 'utc'  - interval '1 minutes'and "ch" = 0;

Расчет среднего! 
select avg("value") from "AVERCUR" where "time" > NOW() at time zone 'utc'  - interval '10 minutes'and "ch" = 0;


select * from (select * from "AVERCUR" where "time" > NOW() at time zone 'utc'  - interval '1 minutes'and "ch" = 0) as TI where "time"  


select * from "AVERCUR" where "time" > NOW() at time zone 'utc'  - interval '1 minutes'and "ch" = 0;

select * from "AVERCUR" where



select * 
	from "AVERCUR" 
	where "time" > NOW() at time zone 'utc'  - interval '1 minutes'and "ch" = 0

