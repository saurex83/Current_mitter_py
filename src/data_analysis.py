# анализирует принятые данные, считает среднее и сует в базу

# Первоначально я хотел сохранять осциллограммы тока в базу данных.
# Это оказалось проблемно из-за скорость записии. 2000 элементов 
# с использованием save_bulk вставлялися от 1.5 сек и с ростом нагрузки на БД
# время увеличивалось. Теперь я сохраняю только среднии значения тока
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from queue import Queue
from frame import RawFrame as RF
import threading
import datetime
import logging

logger = logging.getLogger("mitter.data_analysis")

CT_RATIO = 2500 # Соотношение витков токового трансформатора
R_SENSE = 51 # Сопротивление нагрузочного резистора
OPA_AMPL = 1.5 # Коэффициент усиления

# Работа с базой данных
DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)

class DataAnalysis(threading.Thread):
	""" """
	def __init__(self, in_queue):
		threading.Thread.__init__(self)
		self.in_queue = in_queue
		self.item = RF()
		self.current_osc = list()
		self.current_avr = 0
		DB_Base.metadata.create_all(DB_Engine)


	def run(self):
		logger.info('Поток анализатора данных запущен')
		try:
			while True:
				self.item = self.in_queue.get()

				self._calc_current_osc()
				self._calc_current_avr()

				logger.info(
					'Анализ данных канала %i произведен'%(self.item.channel)
					)
				# Вставка осцилограммы в БД очень время затратная операция
				#self._put_osc_to_db()
				self._put_avr_to_db()
				
		except Exception:
			logger.exception("Исключение в потоке")

	def _put_avr_to_db(self):
		session = DB_Session()
		AC = AverageCurr(self.current_avr, self.item.channel)
		session.add(AC)
		session.commit()
		session.close()

	def _put_osc_to_db(self):
		pass
		
	def _calc_current_avr(self):
    	# На основе осциллограммы считаем средний ток
    	# Так как интервал между отсчетами равномерный, я посчитаю среднее
		current_avr = 0
		for val in self.current_osc:
			current_avr += val
		current_avr /= len(self.current_osc)
		self.current_avr = current_avr

	def _calc_current_osc(self):
    	# Создаем осциллограмму тока
		self.current_osc= list()
		time_step = self.item.period_us
		for volt in self.item.float_data:
			self.current_osc.append(self._conv(volt))

	def _conv(self, volt):
		""" Преобразуем напряжение в ток """
    	#TODO отсчечку по току I < 100 ма  = 0А
		I = volt/(R_SENSE*OPA_AMPL)
		I = I*CT_RATIO
		return I

class AverageCurr(DB_Base):
	__tablename__ = 'AVERCUR'
	id = Column(Integer, primary_key = True)
	time = Column(DateTime(timezone=True), default=datetime.datetime.now)
	# DateTime(timezone=True), server_default=func.now()
	# time = Column(DateTime, default=datetime.datetime.now)
	ch = Column(Integer)
	value = Column(Float)

	def __init__(self, value, ch):
		self.value = value
		self.ch = ch



#start_time = TMM.time()    ####################################### DEBUG
#print("--- %s seconds ---" % (TMM.time() - start_time)) ############