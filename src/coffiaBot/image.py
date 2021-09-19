import random
from os.path import sep
from .database.query import addImage, getImage

def getImageData(filenames):
    f = random.choice(filenames)
    name = f.split(sep)[-1]

    imageId = getImage(name)
    if not imageId:
        addImage(name)
        imageId = getImage(name)

    return imageId, f