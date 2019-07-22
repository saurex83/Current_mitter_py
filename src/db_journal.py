# Анализируем мгновенные значения.
# Добавляем запись в журанал при понижении среднего тока за 30 сек ниже 
# допустимой граници

import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import threading
import datetime
import logging
import time
from param import extractParams

DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)


logger = logging.getLogger("mitter.Journal")

# Уровни журнала
J_INFO = 0
J_WARNING = 1
J_ALARM = 2

class EventJournal(threading.Thread):
	""" """
	def __init__(self):
		threading.Thread.__init__(self)
		self.chStateGood = {1 : True , 2 : True , 3 : True}
		DB_Base.metadata.create_all(DB_Engine)
		max_curr = list()
		ch_name =list()
		time_ch = list()

	def run(self):
		logger.info('Поток журналирования потери питания запущен')
		
		try:
			# Извлекаем настройки граничных условий
			while True:
				PARAMS = extractParams()
				self.max_curr = list()
				self.max_curr.append(0) # Нумерация начинается с 1
				self.max_curr.append(float(PARAMS["MAX_CURR_CH1"]))
				self.max_curr.append(float(PARAMS["MAX_CURR_CH2"]))
				self.max_curr.append(float(PARAMS["MAX_CURR_CH3"]))


				self.ch_name = list()
				self.ch_name.append('x') # Нумерация начинается с 1
				self.ch_name.append(PARAMS["NAME_CH1"])
				self.ch_name.append(PARAMS["NAME_CH2"])
				self.ch_name.append(PARAMS["NAME_CH3"])

				self.time_ch = list()
				self.time_ch.append(0)
				self.time_ch.append(int(PARAMS["MAX_TIME_CH1"]))
				self.time_ch.append(int(PARAMS["MAX_TIME_CH2"]))
				self.time_ch.append(int(PARAMS["MAX_TIME_CH3"]))





				self._check_current()

				time.sleep(1)

		except Exception:
			logger.exception("Исключение в потоке")

	# Проверим что все значения curr превышают порог th. Вернем True
	def _more_than_th(self, curr, th):
		more = True
		for i in curr:
			if i < th:
				more = False
				break
		return more

	# добавляем сообщение в лог если произошло превышение тока
	# Функция повторно не добавлет событие в журнал, пока уровень не понизиться
	def _error_accured(self,curr, ch, th, CN):
		if self.chStateGood[ch] == True:
			self.chStateGood[ch] = False
			logger.debug("Ток в канале %i выше %i"%(ch,th))
			self._write_journal_msg(
			J_ALARM,
			'Тревога',
			'%s'%(CN),
			'Ток превысил границу.I = %.1f А, MAX I = %.1f А'%(curr[0], th)
			)			
	
	# добавляем сообщение в лог если произошло понижение тока ниже границы
	# Функция повторно не добавлет событие в журнал, пока уровень не повыситься
	def _info_accured(self,curr, ch, th, CN):
		if self.chStateGood[ch] == False:
			self.chStateGood[ch] = True
			logger.debug("Ток в канале %i ниже %i"%(ch,th))
			self._write_journal_msg(
			J_INFO,
			'Информация',
			'%s'%(CN),
			'Ток вернулся в границу.I = %.1f А, MAX I = %.1f А'%(curr[0], th)
			)	

	def _check_current(self):
		logger.debug("Проверка наличия тока канала")

		for channel in range(1,4):
			curr = self._get_last_n_sec_curr(channel)

			# Измерений может и не быть, выход
			if len(curr) == 0:
				return
			
			MC = self.max_curr[channel]
			CN = self.ch_name[channel]

			if self._more_than_th(curr, MC):
				""" Превысили порог тока за отведенное время """
				self._error_accured(curr, channel, MC, CN)
			else:
				self._info_accured(curr, channel, MC, CN)

# Возвращает список значений тока за последнии N сек по каналу ch
	def _get_last_n_sec_curr(self, ch):
		curr = list()
		session = DB_Session()

		current_time = datetime.datetime.now()
		last_time = current_time - datetime.timedelta(seconds = self.time_ch[ch])

		aver = session.query(Curdata)
		aver = aver.filter( Curdata.time > last_time)
		aver = aver.filter( Curdata.ch == ch)
		aver = aver.with_entities(Curdata.c_avr)
		aver = aver.all()		
		session.close()
		
		# Список кортежей приведем к нормальному списку
		for i in aver:
			curr.append(i[0])

		return(curr)

# Добавить сообщение в журнал
	def _write_journal_msg(self, errlevel,errleveltext, source, message):
		DB_Base.metadata.create_all(DB_Engine)
		session = DB_Session()
		JR = Journal(errlevel,errleveltext, source, message)
		session.add(JR)
		session.commit()
		session.close()

# Таблица журнала
class Journal(DB_Base):
	__tablename__ = 'JOURNAL'
	id = Column(Integer, primary_key = True)
	time = Column(DateTime(timezone=True), default=datetime.datetime.now)
	adapttime = Column(String)
	errlevel = Column(Integer)
	errleveltext = Column(String)
	source = Column(String)
	message = Column(String)

	def __init__(self, errlevel, errleveltext,source, message):
		self.errlevel = errlevel
		self.errleveltext = errleveltext
		self.source = source
		self.message = message
		now = datetime.datetime.now()
		self.adapttime = now.strftime('%d/%m/%y %H:%M:%S')

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
