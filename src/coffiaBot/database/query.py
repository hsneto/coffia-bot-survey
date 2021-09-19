from math import ceil
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from .tables import *
from .general import engine, Session

def addUser(name, job, company, telegramId):
    session = Session()
    session.add(User(name, job, company, telegramId))
    session.commit()
    session.close()

def getUser(telegramId):
    session = Session()
    userId = session.query(User) \
        .with_entities(User.id) \
        .filter(User.telegramId==telegramId) \
        .first()
    session.close()
    return userId[0] if userId else None

def addImage(name):
    session = Session()
    session.add(Image(name))
    session.commit()
    session.close()

def getImage(name):
    session = Session()
    imageId = session.query(Image) \
        .with_entities(Image.id) \
        .filter(Image.name==name) \
        .first()
    session.close()
    return imageId[0] if imageId else None

def getLabels():
    session = Session()
    labels = session.query(Label).all()
    session.close()
    return labels

def getLabelName(labelId):
    session = Session()
    labelName = session.query(Label) \
        .with_entities(Label.name) \
        .filter(Label.id==labelId) \
        .first()
    session.close()
    return labelName[0] if labelName else None

def getKeybordLabels():
    labels = getLabels()
    inlineKeyboards=[
        InlineKeyboardButton(text=l.name, callback_data=l.id) for l in labels]

    batchSize = 2
    return InlineKeyboardMarkup(inline_keyboard=[inlineKeyboards[i:i+batchSize] 
        for i in range(0, len(inlineKeyboards), batchSize)])

    # return InlineKeyboardMarkup(inline_keyboard=[[
    #     InlineKeyboardButton(text=l.name, callback_data=l.id) for l in labels]])
        
def addSurvey(userId, imageId, labelId):
    session = Session()
    session.add(Survey(userId, imageId, labelId))
    session.commit()
    session.close()


    