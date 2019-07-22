# Описывает структуры входящих данных, декодирует, проверяет
# Я как то плохо поступил назвав crc32..хотя  нужен 1 байт для xor
# так и размерость uint16

import time
from ctypes import *

class DataStruct(Structure):
	""" Разбор байтового массива на структуру """
	_pack_ = 1
	_fields_ = [('xor8', c_uint8),
				('REF', c_float),
				('adc_ref_val', c_uint16),

				# В таком формате упаковываются данные
				('ch_num_1', c_uint8),
				('avr_value_1', c_uint16),
				('max_value_1', c_uint16),
				
				('ch_num_2', c_uint8),
				('avr_value_2', c_uint16),
				('max_value_2', c_uint16),
				
				('ch_num_3', c_uint8),
				('avr_value_3', c_uint16),
				('max_value_3', c_uint16),
			   ]

class RawFrame:
	""" Данные с измерительного канала """
	def __init__(self):
		self.REF = None
		self.adc_ref_val = None
		self.xor8 = None
		self.chanel_data = list()
		self.timestamp = None
		self.struct_data = DataStruct()
		self.data_valid = False

	def set_raw_frame(self, raw_data):
		""" Загрузить сырые данные """
		# Проверим что хватит размера структуры
		if len(raw_data) != sizeof(DataStruct):
			raise ValueError('Size of raw data not DataStruct size')
		
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
		self.REF = self.struct_data.REF
		self.adc_ref_val = self.struct_data.adc_ref_val
		self.xor8 = self.struct_data.xor8

	def _data_parse(self):
		""" Разбор данных пакета """


		# Вычисляем коэфф. преобразования АЦП.
		k = self.REF/self.adc_ref_val

		# Формируем словарь с данными и переводим в вольты
		self.chanel_data = list()
		self.chanel_data.append({'ch':self.struct_data.ch_num_1,
							'avr':k*self.struct_data.avr_value_1,
							'max':k*self.struct_data.max_value_1})

		self.chanel_data.append({'ch':self.struct_data.ch_num_2,
							'avr':k*self.struct_data.avr_value_2,
							'max':k*self.struct_data.max_value_2})

		self.chanel_data.append({'ch':self.struct_data.ch_num_3,
							'avr':k*self.struct_data.avr_value_3,
							'max':k*self.struct_data.max_value_3})




