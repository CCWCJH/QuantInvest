import datetime
import time
import mysql.connector
import tushare as ts
import numpy as np
from pathlib import Path
from urllib3.connectionpool import xrange
from multiprocessing import Process

filesdir = "files/"
dbpw = filesdir + "dbpassword"
tk = filesdir + "token"
isInit = filesdir + "init"
startDt = filesdir + "startDt"
lockF = filesdir + "lock"
first = None
dbpass = open(dbpw, 'r').read()
procNum = 4


def init():
    """
    初始化
    """
    global first, start_dt, end_dt, pro
    token = open(tk, 'r').read()
    ts.set_token(token)
    time_temp = datetime.datetime.now()
    end_dt = time_temp.strftime('%Y%m%d')
    if not Path(isInit).exists():
        first = True
        start_dt = '19901219'
        with open(isInit, "w") as f:
            f.write("database initiated")
    else:
        first = False
        start_dt = open(startDt, 'r').read()
    with open(startDt, "w") as f:
        f.write(end_dt)
    print("初始化完成")


def writeDfToFile(df, filename, method):
    """
    将df写到txt
    :param :df, filename, method
    :return:
    """
    with open(filename, method) as f:
        for i in range(len(df)):
            for string in df.iloc[i]:
                if isinstance(string, str):
                    f.write(string)
                else:
                    f.write("空")
                f.write(" ")
            f.write("\n")


def findColMaxMinLen(df):
    """
    寻找每列最长最短长度
    :param :df
    :return:
    """
    for col in df:
        maxi = 0
        mini = 999
        for element in df[col]:
            if isinstance(element, str):
                # if(col=='employees' and len(element)==8):
                #     print(element)
                if len(element) > maxi:
                    maxi = len(element)
                if len(element) < mini:
                    mini = len(element)
        print(col + " max：", maxi)
        print(col + " min：", mini)
    print('')


def turnDfToListTuple(df):
    """
    将df转化为[(，，), (，，), (，，)]
    :param :df
    :return:val
    """
    val = []
    for i in range(len(df)):
        listTemp = []
        for string in df.iloc[i]:
            if isinstance(string, str):
                listTemp.append(string)
            else:
                listTemp.append("空")
        val.append(tuple(listTemp))
    return val


def floatToStr(df, cols, isInt):
    """
    df列属性float转为str
    :param :df, cols, isInt
    :return:df
    """
    for col in cols:
        ser = df[col]
        if isInt:
            ser.replace(np.nan, 0, inplace=True)
            df[col] = df[col].astype(int).astype(str)
        else:
            ser.replace(np.nan, "空", inplace=True)
            df[col] = df[col].astype(str)
    return df


def getTsCodeList():
    """
    获取所有股票代码（列表形式）
    :param :
    :return:result
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    cursor = db.cursor()
    cursor.execute("SELECT ts_code FROM stock_basic.stock_company")
    db.commit()
    result = cursor.fetchall()
    db.close()
    return result


def get_ts_code_listStr():
    """
    获取所有股票代码（字符串形式）
    :param :
    :return:ts_code_listStr, len(ts_codes)
    """
    ts_code_listStr = ""
    while True:
        lock = open(lockF, 'r').read()
        if not lock == "0":
            ts_codes = getTsCodeList()
            break
        time.sleep(1)
    for i in range(len(ts_codes)):
        ts_code_listStr += str(ts_codes[i])[2:-3]
        ts_code_listStr += ","
    return ts_code_listStr, len(ts_codes)


def get_trade_date_list():
    """
    获得交易日日期（列表形式）
    :param :
    :return:result
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=dbpass,
        charset='utf8'
    )
    cursor = db.cursor()
    cursor.execute("SELECT cal_date FROM stock_basic.trade_cal WHERE exchange = \"SSE\" and is_open = \"1\"")
    db.commit()
    result = cursor.fetchall()
    db.close()
    return result


def multiProcessJob(n, job, args):
    """
    多进程
    :param :n: 多进程数,job: 函数任务,args：参数（列表形式:[[],[]]）
    :return:
    """
    processes = [Process(target=job, args=args[i]) for i in xrange(n)]  # 保存了n个process对象,实例化多进程
    for t in processes:
        t.start()  # 开始进程，必须调用
    for t in processes:
        t.join()  # 等待直到该进程结束
        # join是阻塞线程，所有进程执行完毕后，才执行后边语句
