from sqlalchemy import Column, Integer, String, Float, create_engine, DateTime
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base


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