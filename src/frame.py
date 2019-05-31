# Описывает структуры входящих данных, декодирует, проверяет
# Я как то плохо поступил назвав crc32..хотя  нужен 1 байт для xor
# так и размерость uint16

import time
from ctypes import *

# Размер структуры возьму с запасом
MAX_DATA_LEN = 5000

class DataStruct(Structure):
	""" Разбор байтового массива на структуру """
	_pack_ = 1
	_fields_ = [('xor8', c_uint8),
				('REF', c_float),
				('adc_ref_val', c_uint16),
				('channel', c_uint8),
				('period_us', c_uint16),
				('val_count', c_uint16),
				('data', c_uint16*MAX_DATA_LEN)
			   ]

class RawFrame:
	""" Данные с измерительного канала """
	def __init__(self):
		self.channel = None
		self.REF = None
		self.adc_ref_val = None
		self.period_us = None
		self.val_count = None
		self.xor8 = None
		self.float_data = list()
		self.timestamp = None
		self.struct_data = DataStruct()
		self.data_valid = False

	def set_raw_frame(self, raw_data):
		""" Загрузить сырые данные """
		# Проверим что хватит размера структуры
		if len(raw_data) > sizeof(DataStruct):
			raise ValueError('Size of raw data more DataStruct size')
		
		# Отметим время прихода пакета
		self.timestamp = time.time()

		# Заполним структуру
		memmove(byref(self.struct_data), raw_data, len(raw_data))
		
		# Заполняем поля класса на основе присланных данных
		self._header_parse()
		
		# Посчитаем xor8
		xor8 = 0
		for x in raw_data[1:]:
			xor8 ^= x

		# Проверим целостность данных
		self.data_valid = False
		if self.struct_data.xor8 == xor8:
			self.data_valid = True
		else :
			return

		self._data_parse()

	def validate(self):
		return self.data_valid

	def _header_parse(self):
		""" Разбор заголовка """
		self.channel = self.struct_data.channel
		self.REF = self.struct_data.REF
		self.adc_ref_val = self.struct_data.adc_ref_val
		self.period_us = self.struct_data.period_us
		self.val_count = self.struct_data.val_count
		self.xor8 = self.struct_data.xor8

	def _data_parse(self):
		""" Разбор данных пакета """
		# Убедимся что количество uint16 данных не более максимального размера
		# поля данных структуры.
		if self.val_count > MAX_DATA_LEN:
			raise ValueError('Value counts more then size of MAX_DATA_LEN')

		# Вычисляем коэфф. преобразования АЦП.
		k = self.REF/self.adc_ref_val

		# Переводим отсчеты в вольты
		self.float_data = list()
		for index in range(self.val_count - 1):
			v_float = k*self.struct_data.data[index]
			self.float_data.append(v_float)



