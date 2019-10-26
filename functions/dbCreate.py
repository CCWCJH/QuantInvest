from functions import basicFunctions, sqlFunctions
from header import dbs_info

db_names = dbs_info.db_names


def createDbs():
    for db_name in db_names:
        if basicFunctions.first:
            sqlFunctions.dropDbSql(db_name)
        sqlFunctions.createDbSql(db_name)
