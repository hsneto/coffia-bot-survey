from .general import Base, engine
from sqlalchemy import *


class Image(Base):
    __tablename__ = "image"

    id = Column(Integer(), primary_key='True', autoincrement=True)
    name = Column(String(32))

    def __init__(self, name):
        self.name = name


class Label(Base):
    __tablename__ = "label"

    id = Column(Integer(), primary_key='True', autoincrement=True)
    name = Column(String(8))

    def __init__(self, name):
        self.name = name


class User(Base):
    __tablename__ = "user"

    id = Column(Integer(), primary_key='True', autoincrement=True)
    name = Column(String(128))
    job = Column(String(128))
    company = Column(String(128))
    telegramId = Column("telegram_id", BigInteger())
    

    def __init__(self, name, job, company, telegramId):
        self.name = name
        self.job = job
        self.company = company
        self.telegramId = telegramId


class Survey(Base):
    __tablename__ = "survey"

    id = Column(Integer(), primary_key='True', autoincrement=True)
    userId = Column("user_id ", Integer())
    imageId = Column("image_d", Integer())
    labelId = Column("label_d", Integer())

    def __init__(self, userId, imageId, labelId):
        self.userId = userId
        self.imageId = imageId
        self.labelId = labelId


# Gera as bases
Base.metadata.create_all(engine)
