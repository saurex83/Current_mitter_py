# это главный цикл

# Сдесь настраиваем логер
# Создаем 3 очереди
# Загружаем файл настроек
# Запускаем поток сборщика
# Запускаем потоки анализвторов
# запускаем модуль удаления старых данных из бд
# Следим за потоками и если что поднимем их

from data_harvester import DataHarvest
from data_analysis import DataAnalysis 
from db_datastrip import DBStriper
from db_journal import EventJournal
from queue import Queue 
import threading
import logging
from logging.handlers import RotatingFileHandler
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import os
from param import extractParams

appdir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger("mitter")

packet_queue = Queue()

	
thread_DH = DataHarvest(packet_queue)
thread_DA1 = DataAnalysis(packet_queue)
thread_DBStrip = DBStriper()
thread_J = EventJournal()

THREAD_CHECK_TIMEOUT = 1 # Интервал контроля работоспособности потоков в сек.

def MainRoutine():
	_logger_config()
	_postgres_db_check()
	
	extractParams()
	
	try:
		_main_thread_loop()
	except Exception:
		logger.exception("Исключение в главном цикле программы")

def _main_thread_loop():
	global thread_DH
	global thread_DA1
	global thread_DBStrip
	global thread_J
	global packet_queue

	# Поднимаем потоки
	thread_DH.start()
	thread_DA1.start()
	thread_DBStrip.start()
	thread_J.start()

	# Перезапускаем потоки по мере их падения
	while True:
		if thread_DH.isAlive() == False:
			thread_DH = DataHarvest(packet_queue)
			thread_DH.start()
			logger.warning('Поток сборщика данных перезапущен.')

		if thread_DA1.isAlive() == False:
			thread_DA1 = DataAnalysis(packet_queue)
			thread_DA1.start()
			logger.warning('Поток анализа данных канала перезапущен.')

		if thread_DBStrip.isAlive() == False:
			thread_DBStrip = DBStriper()
			thread_DBStrip.start()
			logger.warning('Поток удаления старых данных перезапущен.')

		if thread_J.isAlive() == False:
			thread_J = EventJournal()
			thread_J.start()
			logger.warning('Поток журналирования перезапущен.')

		sleep(THREAD_CHECK_TIMEOUT)

def _logger_config():
	global logger
	fh = logging.StreamHandler()
	#fh = RotatingFileHandler(appdir+"/mitter.log", mode='a', 
	#	maxBytes=64*1024, backupCount=10, encoding=None, delay=0)


	fmt = logging.Formatter(
		'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
		)
	fh.setFormatter(fmt)
	logger.addHandler(fh)
	logger.setLevel(logging.DEBUG)

def _postgres_db_check():
	""" Проверим или создаим базу данных """
	engine = create_engine("postgres://mitter:mitter@localhost/mitter")

	if not database_exists(engine.url):
		logger.info('База данных отсутвует. Создадим ее.')
		create_database(engine.url)
	else:
		logger.info('База данных существует.')
