import re
import json
from collections import namedtuple

def loadJson(filename):
    """Lê um arquivo JSON e retorna um dict com os dados."""
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def writeJson(data, filename):
    """Escreve um arquivo JSON baseado em um dicionário."""
    with open(filename, "a") as f:
        f.write(json.dumps(data, sort_keys=True, indent=4))

def toNamedtuple(data, name="data"):
    """Converte um dict para namedtuple."""
    return namedtuple(name, data.keys())(*data.values())

def loadMacros(filename="./macros.json"):
    """Lê um arquivo JSON com as macros e retorna um dict com os dados."""
    return toNamedtuple(loadJson(filename))

def createPattern(string):
    """Cria um padrão de comandos de bot."""
    return re.compile(f"/{string}|{string}")
    
def matchPattern(string, pattern):
    """Verifica se uma string contém um padrão."""
    return bool(pattern.match(string.lower()))
