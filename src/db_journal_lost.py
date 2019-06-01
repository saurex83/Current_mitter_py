# Анализируем мгновенные значения.
# Добавляем запись в журанал при понижении среднего тока за 30 сек ниже 
# допустимой граници

import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import threading
import datetime
import logging
import time

logger = logging.getLogger("mitter.db_journal_lost")

# Пороговое значение тока
LOW_CURR = 50e-3
# Уровни журнала
J_INFO = 0
J_WARNING = 1
J_ALARM = 2

# Работа с базой данных
DB_Base = declarative_base()
DB_Engine = create_engine("postgres://mitter:mitter@localhost/mitter")
DB_Session = sessionmaker(bind = DB_Engine)

class JournalCurrLost(threading.Thread):
	""" """
	def __init__(self):
		threading.Thread.__init__(self)
		DB_Base.metadata.create_all(DB_Engine)
		self.chStateGood = {0 : True , 1 : True , 2 : True}

	def run(self):
		logger.info('Поток журналирования потери питания запущен')
		try:
			while True:
				self._check_current(0)
				self._check_current(1)
				self._check_current(2)
				time.sleep(5)

		except Exception:
			logger.exception("Исключение в потоке")

	def _check_current(self, ch):
		logger.info("Проверка наличия тока канала - %i"%(ch))
		avr = self._get_aver_db(ch)
		logger.info(avr)

		avr_new_state = False
		try:
			if avr > LOW_CURR:
				avr_new_state = True 
		except TypeError:
			return # Если значений нет то регистрировать нечего

		if avr_new_state == True:
			logger.info("Ток в норме")
		else:
			logger.info("Ток ниже порога")

		# Если состояние канала не изменилось то ничего предпринимать не нужно
		if avr_new_state == self.chStateGood[ch]:
			return

		logger.info("Состояние канала изменилось")

		# Запомним новое состояние
		self.chStateGood[ch] = avr_new_state

		# Добавим запись в журнал что ток появился
		if avr_new_state == True:
			self._write_journal_msg(
				J_INFO,
				'Информация',
				'Канал %i'%(ch),
				'Ток поднялся выше порога %.1f мА'%(LOW_CURR*1000)
				)
		else:
				self._write_journal_msg(
				J_ALARM,
				'Тревога',
				'Канал %i'%(ch),
				'Ток опустился ниже порога %.1f мА'%(LOW_CURR*1000)
				)

	def _get_aver_db(self, ch):
		session = DB_Session()
		current_time = datetime.datetime.now()
		last_time = current_time - datetime.timedelta(seconds=15)
		aver = session.query(func.avg(AverageCurr.value)).filter(
			 AverageCurr.time > last_time).filter(AverageCurr.ch == ch).all()
		session.close()
		return aver[0][0]

	def _write_journal_msg(self, errlevel,errleveltext, source, message):
		session = DB_Session()
		JR = Journal(errlevel,errleveltext, source, message)
		session.add(JR)
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
