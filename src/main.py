import sys
import os
import daemon
import lockfile
from lockfile import AlreadyLocked
from daemon import pidfile
import time

# Сдесь будем демонезировать наш главный цикл
appdir = os.path.abspath(os.path.dirname(__file__))
pid = pidfile.TimeoutPIDLockFile(appdir+'/mitter.pid', -1)

#std = open('stdout.txt', 'w')

def _demon_process():
	_try_pidlock()
	_run_app()


def _run_app():
	print("Запуск контекста демона")
	with daemon.DaemonContext(
		umask=0o002,
		pidfile=pid,
		stdout=sys.stdout,
		stderr=sys.stdout,
	)as context:
		# Производим импорт модулей только в этом контексте.
		from main_routine import MainRoutine
		print("Контекс запущен.")
		MainRoutine()
		context.close()


def _isPid_Locked():
	try:
		pid.acquire()
	except AlreadyLocked:
		return True
	pid.break_lock()
	return False

def _isDaemon_Run():
	if not (type(pid.read_pid())  is int):
		return False
	try:
		os.kill(pid.read_pid(), 0)
	except OSError:
		return False
	return True

def _try_pidlock():
	# Если PID не защелкнут, значит можно запускать демона
	if not _isPid_Locked():
		print("PID не заблокирован.")
		return

	# PID может быть защелкнуть по причине некоректного завершения демона
	# вызванной перезагрузкой устройства.
	if not _isDaemon_Run():
		print("PID заблокирован, но демон не работает.")
		pid.break_lock()
		return

	print("Экземпляр демона работает.PID = %i. Выход."%(pid.read_pid()))
	exit(1)



	try:
		pid.acquire()
	except AlreadyLocked:
		print("Экземпляр демона работает.PID = %i. Выход."%(pid.read_pid()))
		exit(1)
	pid.break_lock()


	# Поток не создан
	print(type(pid.read_pid()))
	if not (type(pid.read_pid())  is int):
		print("PID пустой.")
		return

	# Запущен ли поток указанный в PID
	try:
		os.kill(pid.read_pid(), 0)
	except OSError:
		# Указанный поток не существует, снимаем блокировку
		print("Потока не существует.")
		pid.break_lock()
		return

	print("Экземпляр демона работает.PID = %i. Выход."%(pid.read_pid()))
	exit(1)





def _demon_stop_process():
	print("Пробуем остановить демона.")
	try:
		if  not (type(pid.read_pid()) is int):
			print("Демон уже остановлен.")
			exit(0)
		os.kill(pid.read_pid(), 9)
		print("Демон остановлен.")
		pid.break_lock()
		exit(0)

	except OSError:
		print("Потока демона нет. Разблокируем PID.")
		pid.break_lock()	
	pass

if __name__ == "__main__":
    # Отладочный режим
    # Запускаем код без демона

	if 'debug' in sys.argv:
		from main_routine import MainRoutine
		print("Запуск в режиме отладки.")
		MainRoutine()

	if 'start' in sys.argv:
		print("Запуск в режиме демона.")
		_demon_process()

	if 'stop' in sys.argv:
		print("Остановка демона.")
		_demon_stop_process()

	print ("Usage start|stop|debug")