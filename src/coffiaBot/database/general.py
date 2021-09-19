from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ..utils import loadJson, toNamedtuple

def loadDatabase(db, filename='./macros.json'):
    """Carrega os parâmetros de conexão de um banco de dados."""

    data = loadJson(filename)
    return toNamedtuple(data["databases"][db], "database")

def dbUri(dbDict):
    """Converte os parâmetro em uma string de conexão."""

    # Connect to a MySQL/MariaDB database
    if dbDict.engine in ('MariaDB', 'MySQL'):
        strCon = (
            f'mysql+pymysql://{dbDict.user}:{dbDict.pw}@'
            f'{dbDict.host}:{dbDict.port}/{dbDict.database}'
        )
        
    # Connect to a PostgreSQL database
    elif dbDict.engine == 'PostgreSQL':
        strCon = (
            f'postgresql://{dbDict.user}:{dbDict.pw}@'
            f'{dbDict.host}:{dbDict.port}/{dbDict.database}'
        )

    # Connect to a Oracle database 
    elif dbDict.engine == "Oracle":
        import cx_Oracle
        dsnStr = cx_Oracle.makedsn(dbDict.host, dbDict.port, service_name=dbDict.service)
        strCon = f'oracle://{dbDict.user}:{dbDict.pw}@{dsnStr}'

    # Connect to a AzureSQL database
    elif dbDict.engine == "SQL Server":
        import urllib

        params = urllib.parse.quote_plus(
            f"DRIVER={dbDict.driver};"
            f"SERVER={dbDict.host};"
            f"DATABASE={dbDict.database};"
            f"UID={dbDict.user};"
            f"PWD={dbDict.pw};"
            f"Authentication={dbDict.authentication}"
        )
        strCon = f'mssql+pyodbc:///?odbc_connect={params}'

    # Unknown database
    else: 
        raise Exception('Unknown database type.')

    return strCon

def createEngine(dbDict):
    """Cria uma engine do banco de dados."""

    return create_engine(dbUri(dbDict))


# Cria as engines da API
engine = createEngine(loadDatabase("base"))
Session = sessionmaker(bind=engine)
Base = declarative_base()