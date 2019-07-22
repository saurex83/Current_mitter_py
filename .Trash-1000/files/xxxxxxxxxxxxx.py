import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
DB_Base = declarative_base()

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

# Таблица настроек
class CNF(DB_Base):
	__tablename__ = 'CNF'
	id = Column(Integer, primary_key = True)
	
	name = Column(String) # Имя параметра
	value = Column(String) # Значение параметра в json

	def __init__(self):
		pass


J = Journal(0,'','','')
C = Curdata(0,0,0)
CN = CNF()

print ('CREATEEEE')
