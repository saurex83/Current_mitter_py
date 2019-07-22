# Подгружает настройки программы из всех источников


import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)
DB_Base.metadata.create_all(DB_Engine)


PARAMS_DEFAULT = {"MAX_CURR_CH1" : "50", "MAX_CURR_CH2" : "50",
					"MAX_CURR_CH3" : "50", "MAX_TIME_CH1" : "3",
					"MAX_TIME_CH2" : "3", "MAX_TIME_CH3" : "3",
					"NAME_CH1" : "Фаза 1",
					"NAME_CH2" : "Фаза 2", "NAME_CH3" : "Фаза 3",
					"NAME_OBJ" : "Помещение #1" }
PARAMS = dict()

def extractParams():
	PARAMS = PARAMS_DEFAULT
	session = DB_Session()
	
	tmp = CNF()
	tmp = session.query(CNF).all()
	for item in tmp:
		PARAMS[item.name] = item.value

	tmp = session.query(CNF).first()

	session.close()
	return PARAMS
	#print(PARAMS)

# Таблица настроек
class CNF(DB_Base):
	__tablename__ = 'CNF'
	id = Column(Integer, primary_key = True)
	
	name = Column(String) # Имя параметра
	value = Column(String) # Значение параметра в json

	def __init__(self):
		pass