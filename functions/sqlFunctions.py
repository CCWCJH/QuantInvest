import mysql.connector
from header import dbs_info
from functions import basicFunctions

dbpass = open(basicFunctions.dbpw, 'r').read()


def createDbSql(db_name):
    """
    执行sql创建数据库
    :param :db_name
    :return:
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    db.cursor().execute("CREATE DATABASE IF NOT EXISTS " + db_name)
    db.commit()
    db.close()


def dropDbSql(db_name):
    """
    执行sql删除数据库
    :param :db_name
    :return:
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    db.cursor().execute("DROP DATABASE IF EXISTS " + db_name)
    db.commit()
    db.close()


def createTableSql(db_name, table_name, cols_tup, unique_cols, first):
    """
    执行sql创建表格
    :param :db_name, table_name, cols_tup, unique_cols, first
    :return:
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    if db_name == "stock_daily":
        cols = str(cols_tup).replace('\'', '').replace('))', ")")
    else:
        cols = str(cols_tup).replace('\'', '').replace(',', " NOT NULL,").replace('))', ") NOT NULL")
    addAttribute = ""
    if (not unique_cols == "") and (table_name in dbs_info.dropTableList or first):
        addAttribute = ", primary key unique_cols (" + unique_cols + ")"
    db.cursor().execute("CREATE TABLE IF NOT EXISTS " + db_name + "." + table_name + " " + cols + addAttribute + ")")
    db.commit()
    db.close()


def dropTableSql(db_name, table_name):
    """
    执行sql删表
    :param :db_name, table_name
    :return:
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    db.cursor().execute("DROP TABLES IF EXISTS " + db_name + "." + table_name)
    db.commit()
    db.close()


def insertSql(db_name, values_df, table_name, cols_tup):
    """
    执行sql插入
    :param :db_name, values_df, table_name, cols_tup
    :return:
    """
    if len(values_df) == 0:
        return
    sql = "INSERT INTO " + db_name + "." + table_name + " " + str(cols_tup).replace('\'',
                                                                                    '') + " VALUES (%s" + ", %s" * (
                  len(cols_tup) - 1) + ") ON DUPLICATE KEY UPDATE "
    len_cols_tup = len(cols_tup)
    for i in range(len_cols_tup - 1):
        sql += cols_tup[i] + " = VALUES (" + cols_tup[i] + "), "
    sql += cols_tup[len_cols_tup - 1] + " = VALUES (" + cols_tup[len_cols_tup - 1] + ")"
    val = basicFunctions.turnDfToListTuple(values_df)
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    cursor = db.cursor()
    for i in range(0, len(val), 2000):
        try:
            cursor.executemany(sql, val[i:i + 2000])
            db.commit()
        except:
            db.rollback()
    while True:
        cursor.execute("SELECT COUNT(*) FROM " + db_name + "." + table_name)
        db.commit()
        fetch = cursor.fetchone()
        if fetch:
            result = fetch[0]
            break
    db.close()
    print(db_name + "." + table_name, ":", result, "条记录已插入")