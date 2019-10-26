from functions import basicFunctions
from header import dbs_info

procNum = basicFunctions.procNum


def get_and_insert_basic_data(first, db_name, table_names):
    for table_name in table_names:
        dbs_info.dbs[db_name][table_name]["get_func"](first)
        # 调试用
        # if table_name == "":
        #     findColMaxMinLen(values_df)
        #     writeDfToFile(values_df, "数据.txt", "a")


def multi_get_and_insert_basic_data():
    """
    多线程获得并插入基础数据
    """
    db_names = list(dbs_info.dbs.keys())
    for db_name in db_names:
        if db_name == "stock_daily":
            continue
        else:
            table_names = list(dbs_info.dbs[db_name].keys())
            num = len(table_names)
            args = [[basicFunctions.first, db_name,
                     [table_names[j] for j in range(num // procNum * i, num // procNum * (i + 1))]] for
                    i in range(procNum)]
            for j in range(num // procNum * procNum, num):
                args[-1][-1].append(table_names[j])
            basicFunctions.multiProcessJob(4, get_and_insert_basic_data, args)
