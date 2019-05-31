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
from frame import RawFrame as RF
from db_aver_1min import DataAverage1min
from db_aver_10min import DataAverage10min
from db_datastrip import DBStriper
from queue import Queue 
import threading
import logging
from logging.handlers import RotatingFileHandler
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import os

appdir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger("mitter")

q1 = Queue() # Очередь первого канала измерителя
q2 = Queue() # Очередь второго канала измерителя
q3 = Queue() # Очередь третьего канала измерителя
	
thread_DH = DataHarvest(q1, q2, q3)
thread_DA1 = DataAnalysis(q1)
thread_DA2 = DataAnalysis(q2)
thread_DA3 = DataAnalysis(q3)
thread_AVER1MIN = DataAverage1min() 
thread_AVER10MIN = DataAverage10min() 
thread_DBStrip = DBStriper()

THREAD_CHECK_TIMEOUT = 1 # Интервал контроля работоспособности потоков в сек.

def MainRoutine():
	_logger_config()
	_postgres_db_check()
	
	try:
		_main_thread_loop()
	except Exception:
		logger.exception("Исключение в главном цикле программы")

def _main_thread_loop():
	global thread_DH
	global thread_DA1
	global thread_DA2
	global thread_DA3
	global thread_AVER1MIN
	global thread_AVER10MIN
	global thread_DBStrip
	global q1
	global q2
	global q3
	# Поднимаем потоки
	thread_DH.start()
	thread_DA1.start()
	thread_DA2.start()
	thread_DA3.start()
	thread_AVER1MIN.start()
	thread_AVER10MIN.start()
	thread_DBStrip.start()

	# Перезапускаем потоки по мере их падения
	while True:
		if thread_DH.isAlive() == False:
			thread_DH = DataHarvest(q1, q2, q3)
			thread_DH.start()
			logger.warning('Поток сборщика данных перезапущен.')
		if thread_DA1.isAlive() == False:
			thread_DA1 = DataAnalysis(q1)
			thread_DA1.start()
			logger.warning('Поток анализа данных канала 1 перезапущен.')
		if thread_DA2.isAlive() == False:
			thread_DA2 = DataAnalysis(q2)
			thread_DA2.start()
			logger.warning('Поток анализа данных канала 2 перезапущен.')
		if thread_DA3.isAlive() == False:
			thread_DA3 = DataAnalysis(q3)
			thread_DA3.start()
			logger.warning('Поток анализа данных канала 3 перезапущен.')
		if thread_AVER1MIN.isAlive() == False:
			thread_AVER1MIN = DataAverage1min()
			thread_AVER1MIN.start()
			logger.warning('Поток усреднения данных за 1 минуту перезапущен.')
		if thread_AVER10MIN.isAlive() == False:
			thread_AVER10MIN = DataAverage1min()
			thread_AVER10MIN.start()
			logger.warning('Поток усреднения данных за 10 минуту перезапущен.')
		if thread_DBStrip.isAlive() == False:
			thread_DBStrip = DataAverage1min()
			thread_DBStrip.start()
			logger.warning('Поток удаления старых данных перезапущен.')
		sleep(THREAD_CHECK_TIMEOUT)

def _logger_config():
	global logger
	#fh = logging.FileHandler("mitter.log")
	fh = RotatingFileHandler(appdir+"/mitter.log", mode='a', 
		maxBytes=64*1024, backupCount=10, encoding=None, delay=0)


	fmt = logging.Formatter(
		'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
		)
	fh.setFormatter(fmt)
	logger.addHandler(fh)
	logger.setLevel(logging.INFO)

def _postgres_db_check():
	""" Проверим или создаим базу данных """
	engine = create_engine("postgres://mitter:mitter@localhost/mitter")

	if not database_exists(engine.url):
		logger.info('База данных отсутвует. Создадим ее.')
		create_database(engine.url)
	else:
		logger.info('База данных существует.')

if __name__ == '__main__':
	MainRoutine()
