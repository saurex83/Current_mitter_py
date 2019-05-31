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

logger = logging.getLogger("mitter.db_aver_1min")

# Работа с базой данных
DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)

class DataAverage1min(threading.Thread):
	""" """
	def __init__(self):
		threading.Thread.__init__(self)
		DB_Base.metadata.create_all(DB_Engine)


	def run(self):
		logger.info('Поток усреднения данных за 1 минуту запущен')
		try:
			while True:

				ch = 0 
				avr = self._get_aver_db(ch)
				if avr != None:
					self._put_aver_db(ch, avr)

				ch = 1 
				avr = self._get_aver_db(ch)
				if avr != None:
					self._put_aver_db(ch, avr)
			
				ch = 2 
				avr = self._get_aver_db(ch)
				if avr != None:
					self._put_aver_db(ch, avr)

				time.sleep(60)

		except Exception:
			logger.exception("Исключение в потоке")

	def _get_aver_db(self, ch):
		session = DB_Session()
		current_time = datetime.datetime.now()
		last_time = current_time - datetime.timedelta(seconds=60)
		aver = session.query(func.avg(AverageCurr.value)).filter(
			 AverageCurr.time > last_time).filter(AverageCurr.ch == ch).all()
		session.close()
		return aver[0][0]

	def _put_aver_db(self, ch, value):
		session = DB_Session()
		AC = AverageCurr_1min(value, ch)
		session.add(AC)
		session.commit()
		session.close()

class AverageCurr(DB_Base):
	__tablename__ = 'AVERCUR'
	id = Column(Integer, primary_key = True)
	time = Column(DateTime(timezone=True), default=datetime.datetime.now)
	ch = Column(Integer)
	value = Column(Float)

	def __init__(self, value, ch):
		self.value = value
		self.ch = ch

class AverageCurr_1min(DB_Base):
	__tablename__ = 'AVERCUR1MIN'
	id = Column(Integer, primary_key = True)
	time = Column(DateTime(timezone=True), default=datetime.datetime.now)
	ch = Column(Integer)
	value = Column(Float)

	def __init__(self, value, ch):
		self.value = value
		self.ch = ch

