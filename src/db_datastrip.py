# проверяет размер  таблиц базы даннх и подрезает ее
# Усредняем поминутно

import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import threading
import datetime
import logging
import time

logger = logging.getLogger("mitter.db_datastrip")

# Работа с базой данных
DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)

# Интервал хранениня данных. Все что раньше будет обрезано
TMIN = 60
THOUR = 60*TMIN
TDAY = 24*THOUR
STRIP_INTERVAL = 10*TDAY 		#сек

class DBStriper(threading.Thread):
	""" """
	def __init__(self):
		threading.Thread.__init__(self)
		DB_Base.metadata.create_all(DB_Engine)

	def run(self):
		logger.info('Поток удаления старых данных запущен')
		try:
			while True:
				self._strip_CURDATA()
				time.sleep(60)

		except Exception:
			logger.exception("Исключение в потоке")

	def _strip_CURDATA(self):
		session = DB_Session()

		current_time = datetime.datetime.now()
		last_time = current_time - datetime.timedelta(seconds=STRIP_INTERVAL)
		
		deleted = session.query(Curdata)
		deleted = deleted.filter(Curdata.time < last_time)
		deleted = deleted.delete()

		logger.warning('Из таблицы CURDATA удалено %i записей'%(deleted))
		session.commit()
		session.close()

# Таблица измеренных данных
class Curdata(DB_Base):
	__tablename__ = 'CURDATA'
	id = Column(Integer, primary_key = True)
	time = Column(DateTime(timezone=True), default=datetime.datetime.now)
	# DateTime(timezone=True), server_default=func.now()
	# time = Column(DateTime, default=datetime.datetime.now)
	ch = Column(Integer)
	c_avr = Column(Float)
	c_max = Column(Float)

	def __init__(self, ch, cavr, cmax):
		self.c_avr = cavr
		self.c_max = cmax
		self.ch = ch

