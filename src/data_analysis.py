
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from queue import Queue
from frame import RawFrame as RF
import threading
import logging
import datetime

DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)

logger = logging.getLogger("mitter.data_analysis")

CT_RATIO = 2500 # Соотношение витков токового трансформатора
R_SENSE = 51 # Сопротивление нагрузочного резистора
OPA_AMPL = 1.5 # Коэффициент усиления

class DataAnalysis(threading.Thread):
	""" """
	def __init__(self, in_queue):
		threading.Thread.__init__(self)
		self.in_queue = in_queue
		self.item = RF()
		self.insert_data = list()
		DB_Base.metadata.create_all(DB_Engine)

	def run(self):
		logger.info('Поток анализатора данных запущен')
		try:
			while True:
				self.item = self.in_queue.get()

				self._calc_current()

				#logger.debug('Анализ данных произведен')

				self._put_to_db()
				
		except Exception:
			logger.exception("Исключение в потоке")

	def _put_to_db(self):
		session = DB_Session()
		for i in self.insert_data:
			tmp = Curdata(i['ch'], i['avr'], i['max'])
			session.add(tmp)
		session.commit()
		session.close()
		
	def _calc_current(self):
		self.insert_data = list()
		for i in self.item.chanel_data:
			tmp = dict()
			tmp['ch'] = i['ch']
			tmp['avr'] = self._conv(i['avr'])
			tmp['max'] = self._conv(i['max'])
			self.insert_data.append(tmp)

	def _conv(self, volt):
		""" Преобразуем напряжение в ток """
		I = volt/(R_SENSE*OPA_AMPL)
		I = I*CT_RATIO
		return I

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

#start_time = TMM.time()    ####################################### DEBUG
#print("--- %s seconds ---" % (TMM.time() - start_time)) ############