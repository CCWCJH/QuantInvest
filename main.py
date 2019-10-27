from functions import tablesCreate, basicFunctions, dbCreate, dataGetInsert
from header import dbs_info

if __name__ == "__main__":
    basicFunctions.init()
    dbCreate.createDbs()
    tablesCreate.multiCreateTables()
    dataGetInsert.multi_get_and_insert_basic_data()
    tablesCreate.multiCreateStockTable()
    dbs_info.get_basic(basicFunctions.first)
    basicFunctions.writeNewestTimeToFile()
