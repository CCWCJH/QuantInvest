from functions import basicFunctions, sqlFunctions
from header import dbs_info

db_names = dbs_info.db_names
procNum = basicFunctions.procNum


def createTables(first, db_name, table_names):
    dropTableList = dbs_info.dropTableList
    for table_name in table_names:
        if first or table_name in dropTableList:
            sqlFunctions.dropTableSql(db_name, table_name)
            sqlFunctions.createTableSql(db_name, table_name, tuple(dbs_info.dbs[db_name][table_name]["db_cols"].split(",")),
                                        dbs_info.dbs[db_name][table_name]["unique_cols"], first)
            print("创建表格" + table_name + "完成")


def createStockTable(first, ts_code_list):
    for ts_code in ts_code_list:
        if first:
            sqlFunctions.dropTableSql("stock_daily", ts_code)
        sqlFunctions.createTableSql("stock_daily", ts_code,
                                    tuple(dbs_info.dbs["stock_daily"]["basic"]["db_cols"].split(",")),
                                    dbs_info.dbs["stock_daily"]["basic"]["unique_cols"], first)
        print("创建表格" + ts_code + "完成")


def multiCreateTables():
    for db_name in db_names:
        if db_name == "stock_daily":
            continue
        table_names = list(dbs_info.dbs[db_name].keys())
        num = len(table_names)
        args = [[basicFunctions.first, db_name, [table_names[j] for j in range(num // procNum * i, num // procNum * (i + 1))]] for
                i in range(procNum)]
        for j in range(num // procNum * procNum, num):
            args[-1][-1].append(table_names[j])
        basicFunctions.multiProcessJob(procNum, createTables, args)


def multiCreateStockTable():
    ts_code_listStr, num = basicFunctions.get_ts_code_listStr(create=True)
    ts_code_listStr = ts_code_listStr.replace(".", "_")
    ts_code_list = ts_code_listStr.split(",")
    args = [[basicFunctions.first, [ts_code_list[j] for j in range(num // procNum * i, num // procNum * (i + 1))]] for i in range(procNum)]
    for j in range(num // procNum * procNum, num):
        args[-1][-1].append(ts_code_list[j])
    basicFunctions.multiProcessJob(procNum, createStockTable, args)
