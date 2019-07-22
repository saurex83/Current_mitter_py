# модуль пожирает данные из uart и выдает по очередям

import serial
import threading
from queue import Queue
from frame import RawFrame as RF
from time import sleep
import logging

logger = logging.getLogger("mitter.data_harvester")

SERIAL_SPEED = 115200
SERIAL_DEV = '/dev/ttyS0'
PACKET_INTERVAL = 50e-3
PACKET_SIZE = 22	# Принимаем только такие пакеты
READ_TIMEOUT = 2000e-3

class DataHarvest(threading.Thread):
    def __init__(self,data_queue):
        threading.Thread.__init__(self)
        self.serialport = serial.Serial(
            port = SERIAL_DEV, 
        	baudrate = SERIAL_SPEED,
            timeout = READ_TIMEOUT
        )

        self.data_queue = data_queue

    def run(self):
        logger.info('Поток сборщика данных запущен.')
        try:
            while (True):
                # Ожидаем и принимаем пакет
                self._wait_silence()
                rdata = self._serial_get_packet()
                # Пакет нужной длинны
                if len(rdata) != PACKET_SIZE:
                    logger.warning('Не верный размер пакета.')
                    continue
        		# Упаковываем данные 
                packet = RF()
                packet.set_raw_frame(rdata)

                # Пакет принят с ошибками
                if not packet.validate():
                    logger.warning('Пакет с неверным xor8')
                    continue
    			# Пакет принят без ошибок
               # logger.debug('Принят пакет')
                self.data_queue.put(packet)
    
        except Exception:
            logger.exception("Исключение в потоке")

    def _wait_silence(self):
        """ Дождемся начала передачи пакета """
        while True:
            self.serialport.reset_input_buffer()
            sleep(PACKET_INTERVAL)
            if self.serialport.inWaiting() == 0:
                return

    def _serial_get_packet(self):
        self._wait_silence()
        rdata = self.serialport.read(PACKET_SIZE)
        return rdata