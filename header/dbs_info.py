import datetime
import time
import mysql.connector
import pandas as pd
import tushare as ts
from functions import basicFunctions, sqlFunctions

procNum = basicFunctions.procNum
end_dt = datetime.datetime.now().strftime('%Y%m%d')


def get_stock_company(first):
    pro = ts.pro_api()
    sse_stock_company = pro.stock_company(fields=dbs["stock_basic"]["stock_company"]["query_cols"])
    szse_stock_company = pro.stock_company(exchange='SZSE', fields=dbs["stock_basic"]["stock_company"]["query_cols"])
    stock_company = sse_stock_company.append(szse_stock_company)
    float_to_str_list = ['reg_capital']
    stock_company = basicFunctions.floatToStr(stock_company, float_to_str_list, False)
    float_to_int_to_str_list = ['employees']
    stock_company = basicFunctions.floatToStr(stock_company, float_to_int_to_str_list, True)
    sqlFunctions.insertSql("stock_basic", stock_company, "stock_company",
                           tuple(dbs["stock_basic"]["stock_company"]["query_cols"].split(",")))
    with open(basicFunctions.lockF, 'w') as f:
        f.write("1")
    print("已获取上市公司基本信息")


def job_stk_managers(ts_code_listStr):
    df_col_list = dbs["stock_basic"]["stk_managers"]["query_cols"].split(",")
    interval = 150
    stk_managers = pd.DataFrame(columns=df_col_list)
    pro = ts.pro_api()
    print("正在获取", ts_code_listStr[:9], "等上市公司管理层")
    for i in range(0, len(ts_code_listStr), interval):
        stk_managers = stk_managers.append(pro.stk_managers(ts_code=ts_code_listStr[i:i + interval],
                                                            fields=dbs["stock_basic"]["stk_managers"]["query_cols"]))
        time.sleep(0.6)
    print("stock_basic.stk_managers 开始插入：", len(stk_managers))
    sqlFunctions.insertSql("stock_basic", stk_managers, "stk_managers",
                           tuple(dbs["stock_basic"]["stk_managers"]["query_cols"].split(",")))


def get_stk_managers(first):
    ts_code_listStr, num = basicFunctions.get_ts_code_listStr()
    strLen = 10
    args = [[ts_code_listStr[num // procNum * i * strLen:num // procNum * (i + 1) * strLen]] for i in range(procNum)]
    args[-1][-1] += ts_code_listStr[num // procNum * procNum * strLen:]
    basicFunctions.multiProcessJob(procNum, job_stk_managers, args)
    print("已获取上市公司管理层")


def get_stock_basic_l_or_p(first):
    """
    无delist_date
    :param first:
    :return:
    """
    pro = ts.pro_api()
    stock_basic_L = pro.stock_basic(list_status='L', fields=dbs["stock_basic"]["stock_basic_l_or_p"]["query_cols"])
    stock_basic_P = pro.stock_basic(list_status='P', fields=dbs["stock_basic"]["stock_basic_l_or_p"]["query_cols"])
    stock_basic_l_or_p = stock_basic_L.append(stock_basic_P)
    sqlFunctions.insertSql("stock_basic", stock_basic_l_or_p, "stock_basic_l_or_p",
                           tuple(dbs["stock_basic"]["stock_basic_l_or_p"]["query_cols"].split(",")))
    print("已获取上市股票列表")


def job_stk_rewards(ts_code_listStr):
    df_col_list = dbs["stock_basic"]["stk_rewards"]["query_cols"].split(",")
    interval = 50
    stk_rewards = pd.DataFrame(columns=df_col_list)
    pro = ts.pro_api()
    print("正在获取", ts_code_listStr[:9], "等管理层薪酬和持股")
    for i in range(0, len(ts_code_listStr), interval):
        stk_rewards = stk_rewards.append(pro.stk_rewards(ts_code=ts_code_listStr[i:i + interval],
                                                         fields=dbs["stock_basic"]["stk_rewards"]["query_cols"]))
        time.sleep(0.6)
    float_to_str_list = ['reward']
    stk_rewards = basicFunctions.floatToStr(stk_rewards, float_to_str_list, False)
    float_to_int_to_str_list = ['hold_vol']
    stk_rewards = basicFunctions.floatToStr(stk_rewards, float_to_int_to_str_list, True)
    print("stock_basic.stk_rewards 开始插入：", len(stk_rewards))
    sqlFunctions.insertSql("stock_basic", stk_rewards, "stk_rewards",
                           tuple(dbs["stock_basic"]["stk_rewards"]["query_cols"].split(",")))


def get_stk_rewards(first):
    ts_code_listStr, num = basicFunctions.get_ts_code_listStr()
    strLen = 10
    args = [[ts_code_listStr[num // procNum * i * strLen:num // procNum * (i + 1) * strLen]] for i in range(procNum)]
    args[-1][-1] += ts_code_listStr[num // procNum * procNum * strLen:]
    basicFunctions.multiProcessJob(procNum, job_stk_rewards, args)
    print("已获取管理层薪酬和持股")


def get_stock_basic_d(first):
    """
    无area、industry。
    :param first:
    :return:
    """
    pro = ts.pro_api()
    stock_basic_d = pro.stock_basic(list_status='D', fields=dbs["stock_basic"]["stock_basic_d"]["query_cols"])
    sqlFunctions.insertSql("stock_basic", stock_basic_d, "stock_basic_d",
                           tuple(dbs["stock_basic"]["stock_basic_d"]["query_cols"].split(",")))
    print("已获取退市股票列表")


def get_trade_cal(first):
    pro = ts.pro_api()
    if first:
        start_dt = '19901219'
    else:
        start_dt = open(basicFunctions.startDt, 'r').read()
    sse_trade_cal = pro.trade_cal(exchange='SSE', start_date=start_dt, end_date=end_dt,
                                  fields=dbs["stock_basic"]["trade_cal"]["query_cols"])
    szse_trade_cal = pro.trade_cal(exchange='SZSE', start_date=start_dt, end_date=end_dt,
                                   fields=dbs["stock_basic"]["trade_cal"]["query_cols"])
    trade_cal = sse_trade_cal.append(szse_trade_cal)
    trade_cal['is_open'] = trade_cal['is_open'].astype(str)  # 将一整列由int转为str
    sqlFunctions.insertSql("stock_basic", trade_cal, "trade_cal",
                           tuple(dbs["stock_basic"]["trade_cal"]["query_cols"].split(",")))
    print("已获取交易日历")


def get_namechange(first):
    pro = ts.pro_api()
    if first:
        start_dt = '19901219'
    else:
        start_dt = open(basicFunctions.startDt, 'r').read()
    namechange = pro.namechange(start_date=start_dt, end_date=end_dt,
                                fields=dbs["stock_basic"]["namechange"]["query_cols"])
    sqlFunctions.insertSql("stock_basic", namechange, "namechange",
                           tuple(dbs["stock_basic"]["namechange"]["query_cols"].split(",")))
    print("已获取股票曾用名")


def get_hs_const(first):
    pro = ts.pro_api()
    sh_hs_const = pro.hs_const(hs_type='SH', is_new=0, fields=dbs["stock_basic"]["hs_const"]["query_cols"]).append(
        pro.hs_const(hs_type='SH', fields=dbs["stock_basic"]["hs_const"]["query_cols"]))
    sz_hs_const = pro.hs_const(hs_type='SZ', is_new=0, fields=dbs["stock_basic"]["hs_const"]["query_cols"]).append(
        pro.hs_const(hs_type='SZ', fields=dbs["stock_basic"]["hs_const"]["query_cols"]))
    hs_const = sh_hs_const.append(sz_hs_const)
    sqlFunctions.insertSql("stock_basic", hs_const, "hs_const",
                           tuple(dbs["stock_basic"]["hs_const"]["query_cols"].split(",")))
    print("已获取沪深股通成份股")


def job_new_share(start, end):
    df_col_list = dbs["stock_basic"]["new_share"]["query_cols"].split(",")
    day_interval = (end - start).days
    if day_interval > 3000:
        gap = day_interval
        for i in range(3000, 0, -1):
            if gap % i == 0:
                day_interval = i
                break
    new_share = pd.DataFrame(columns=df_col_list)
    num = (end - start).days
    pro = ts.pro_api()
    for i in range(0, num, day_interval):
        new_share = new_share.append(
            pro.new_share(start_date=(start + datetime.timedelta(days=i)).strftime('%Y%m%d'),
                          end_date=(start + datetime.timedelta(days=i + day_interval)).strftime('%Y%m%d'),
                          fields=dbs["stock_basic"]["new_share"]["query_cols"]))
    float_to_str_list = ['issue_date', 'amount', 'market_amount', 'price', 'pe', 'limit_amount', 'funds', 'ballot']
    new_share = basicFunctions.floatToStr(new_share, float_to_str_list, False)
    sqlFunctions.insertSql("stock_basic", new_share, "new_share",
                           tuple(dbs["stock_basic"]["new_share"]["query_cols"].split(",")))


def get_new_share(first):
    cur_day = datetime.datetime.now()
    start_day = datetime.datetime(2007, 5, 25)
    num = (cur_day - start_day).days
    args = [[start_day + datetime.timedelta(days=(num // procNum * i)),
             start_day + datetime.timedelta(days=(num // procNum * (i + 1)))] for i in range(procNum)]
    args[-1][-1] = cur_day
    basicFunctions.multiProcessJob(procNum, job_new_share, args)
    print("已获取IPO新股列表")


def get_daily(start_dt, ts_code):
    df_col_list = dbs["stock_daily"]["daily"]["query_cols"].replace("change_", "change").split(",")
    daily = pd.DataFrame(columns=df_col_list)
    day_interval = 2000
    start_dt_query = start_dt
    if start_dt == "19901219":
        time_temp = datetime.datetime(1990, 12, 19) + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    else:
        time_temp = datetime.datetime.now()
        end_dt_query = end_dt
    pro = ts.pro_api()
    while start_dt_query <= end_dt:
        daily = daily.append(
            pro.daily(ts_code=ts_code.replace("_", "."), start_date=start_dt_query, end_date=end_dt_query,
                      fields=dbs["stock_daily"]["daily"]["query_cols"].replace("change_", "change")), sort=False)
        time.sleep(0.6)
        time_temp = time_temp + datetime.timedelta(days=1)
        start_dt_query = time_temp.strftime('%Y%m%d')
        time_temp = time_temp + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    if daily is not None:
        if len(daily) > 0:
            float_to_str_list = ["open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"]
            daily = basicFunctions.floatToStr(daily, float_to_str_list, False)
            print("开始插入", ts_code, "日线行情数据：", len(daily))
            sqlFunctions.insertSql("stock_daily", daily, ts_code,
                                   tuple(dbs["stock_daily"]["daily"]["query_cols"].split(",")))
        else:
            print(ts_code, "无日线行情数据")
    else:
        print(ts_code, "无日线行情数据")


def get_adj_factor(start_dt, ts_code):
    df_col_list = dbs["stock_daily"]["adj_factor"]["query_cols"].split(",")
    adj_factor = pd.DataFrame(columns=df_col_list)
    day_interval = 2000
    start_dt_query = start_dt
    if start_dt == "19901219":
        time_temp = datetime.datetime(1990, 12, 19) + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    else:
        time_temp = datetime.datetime.now()
        end_dt_query = end_dt
    pro = ts.pro_api()
    while start_dt_query <= end_dt:
        adj_factor = adj_factor.append(
            pro.adj_factor(ts_code=ts_code.replace("_", "."), start_date=start_dt_query, end_date=end_dt_query,
                           fields=dbs["stock_daily"]["adj_factor"]["query_cols"]), sort=False)
        time.sleep(0.6)
        time_temp = time_temp + datetime.timedelta(days=1)
        start_dt_query = time_temp.strftime('%Y%m%d')
        time_temp = time_temp + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    if adj_factor is not None:
        if len(adj_factor) > 0:
            float_to_str_list = ["adj_factor"]
            adj_factor = basicFunctions.floatToStr(adj_factor, float_to_str_list, False)
            print("开始插入", ts_code, "复权因子数据：", len(adj_factor))
            sqlFunctions.insertSql("stock_daily", adj_factor, ts_code,
                                   tuple(dbs["stock_daily"]["adj_factor"]["query_cols"].split(",")))
        else:
            print(ts_code, "无复权因子数据")
    else:
        print(ts_code, "无复权因子数据")


def get_daily_basic(start_dt, ts_code):
    df_col_list = dbs["stock_daily"]["daily_basic"]["query_cols"].split(",")
    daily_basic = pd.DataFrame(columns=df_col_list)
    day_interval = 2000
    start_dt_query = start_dt
    if start_dt == "19901219":
        time_temp = datetime.datetime(1990, 12, 19) + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    else:
        time_temp = datetime.datetime.now()
        end_dt_query = end_dt
    pro = ts.pro_api()
    while start_dt_query <= end_dt:
        daily_basic = daily_basic.append(
            pro.daily_basic(ts_code=ts_code.replace("_", "."), start_date=start_dt_query, end_date=end_dt_query,
                            fields=dbs["stock_daily"]["daily_basic"]["query_cols"]), sort=False)
        time.sleep(0.6)
        time_temp = time_temp + datetime.timedelta(days=1)
        start_dt_query = time_temp.strftime('%Y%m%d')
        time_temp = time_temp + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    if daily_basic is not None:
        if len(daily_basic) > 0:
            float_to_str_list = ["turnover_rate", "turnover_rate_f", "volume_ratio", "pe", "pe_ttm", "pb", "ps",
                                 "ps_ttm", "total_share", "float_share", "free_share", "total_mv", "circ_mv"]
            daily_basic = basicFunctions.floatToStr(daily_basic, float_to_str_list, False)
            print("开始插入", ts_code, "每日指标数据：", len(daily_basic))
            sqlFunctions.insertSql("stock_daily", daily_basic, ts_code,
                                   tuple(dbs["stock_daily"]["daily_basic"]["query_cols"].split(",")))
        else:
            print(ts_code, "无每日指标数据")
    else:
        print(ts_code, "无每日指标数据")


def get_moneyflow(start_dt, ts_code):
    df_col_list = dbs["stock_daily"]["moneyflow"]["query_cols"].split(",")
    moneyflow = pd.DataFrame(columns=df_col_list)
    day_interval = 2000
    start_dt_query = start_dt
    if start_dt == "19901219":
        time_temp = datetime.datetime(1990, 12, 19) + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    else:
        time_temp = datetime.datetime.now()
        end_dt_query = end_dt
    pro = ts.pro_api()
    while start_dt_query <= end_dt:
        moneyflow = moneyflow.append(
            pro.moneyflow(ts_code=ts_code.replace("_", "."), start_date=start_dt_query, end_date=end_dt_query,
                          fields=dbs["stock_daily"]["moneyflow"]["query_cols"]), sort=False)
        time.sleep(0.6)
        time_temp = time_temp + datetime.timedelta(days=1)
        start_dt_query = time_temp.strftime('%Y%m%d')
        time_temp = time_temp + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    if moneyflow is not None:
        if len(moneyflow) > 0:
            float_to_str_list = ["buy_sm_vol", "buy_sm_amount", "sell_sm_vol", "sell_sm_amount", "buy_md_vol",
                                 "buy_md_amount", "sell_md_vol", "sell_md_amount", "buy_lg_vol", "buy_lg_amount",
                                 "sell_lg_vol", "sell_lg_amount", "buy_elg_vol", "buy_elg_amount", "sell_elg_vol",
                                 "sell_elg_amount", "net_mf_vol", "net_mf_amount"]
            moneyflow = basicFunctions.floatToStr(moneyflow, float_to_str_list, False)
            print("开始插入", ts_code, "个股资金流向数据：", len(moneyflow))
            sqlFunctions.insertSql("stock_daily", moneyflow, ts_code,
                                   tuple(dbs["stock_daily"]["moneyflow"]["query_cols"].split(",")))
        else:
            print(ts_code, "无个股资金流向数据")
    else:
        print(ts_code, "无个股资金流向数据")


def get_stk_limit(start_dt, ts_code):
    df_col_list = dbs["stock_daily"]["stk_limit"]["query_cols"].split(",")
    stk_limit = pd.DataFrame(columns=df_col_list)
    day_interval = 2000
    start_dt_query = start_dt
    if start_dt == "19901219":
        time_temp = datetime.datetime(1990, 12, 19) + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    else:
        time_temp = datetime.datetime.now()
        end_dt_query = end_dt
    pro = ts.pro_api()
    while start_dt_query <= end_dt:
        stk_limit = stk_limit.append(
            pro.stk_limit(ts_code=ts_code.replace("_", "."), start_date=start_dt_query, end_date=end_dt_query,
                          fields=dbs["stock_daily"]["stk_limit"]["query_cols"]), sort=False)
        time.sleep(0.6)
        time_temp = time_temp + datetime.timedelta(days=1)
        start_dt_query = time_temp.strftime('%Y%m%d')
        time_temp = time_temp + datetime.timedelta(days=day_interval)
        end_dt_query = time_temp.strftime('%Y%m%d')
    if stk_limit is not None:
        if len(stk_limit) > 0:
            float_to_str_list = ["up_limit", "down_limit"]
            stk_limit = basicFunctions.floatToStr(stk_limit, float_to_str_list, False)
            print("开始插入", ts_code, "每日涨跌停价格数据：", len(stk_limit))
            sqlFunctions.insertSql("stock_daily", stk_limit, ts_code,
                                   tuple(dbs["stock_daily"]["stk_limit"]["query_cols"].split(",")))
        else:
            print(ts_code, "无每日涨跌停价格数据")
    else:
        print(ts_code, "无每日涨跌停价格数据")


def job_get_basic(start_dt, ts_code_list):
    table_names = list(dbs["stock_daily"].keys())
    del (table_names[0])
    for ts_code in ts_code_list:
        for table_name in table_names:
            dbs["stock_daily"][table_name]["get_func"](start_dt, ts_code)


def job_del_null_col(ts_code_list):
    for ts_code in ts_code_list:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd=sqlFunctions.dbpass,
            charset='utf8'
        )
        cursor = db.cursor()
        cursor.execute("DELETE FROM stock_daily." + ts_code + " WHERE open is null")
        db.commit()  # 一定要有，否则删除语句无效
        db.close()
        print(ts_code, "删除空数据完成")


def get_basic(first):
    if first:
        start_dt = '19901219'
    else:
        start_dt = open(basicFunctions.startDt, 'r').read()
    ts_code_listStr, num = basicFunctions.get_ts_code_listStr()
    ts_code_listStr = ts_code_listStr.replace(".", "_")
    ts_code_list = ts_code_listStr.split(",")
    args = [[start_dt, [ts_code_list[j] for j in range(num // procNum * i, num // procNum * (i + 1))]] for i in
            range(procNum)]
    for j in range(num // procNum * procNum, num):
        args[-1][-1].append(ts_code_list[j])
    basicFunctions.multiProcessJob(procNum, job_get_basic, args)
    args = [[[ts_code_list[j] for j in range(num // procNum * i, num // procNum * (i + 1))]] for i in
            range(procNum)]
    for j in range(num // procNum * procNum, num):
        args[-1][-1].append(ts_code_list[j])
    basicFunctions.multiProcessJob(procNum, job_del_null_col, args)
    print("已获取并插入日线基础数据")


dbs = {
    "stock_basic":
        {
            "stock_company":
                {
                    "db_cols": "ts_code CHAR(9) PRIMARY KEY,exchange VARCHAR(4),chairman VARCHAR(50),manager VARCHAR(50),secretary VARCHAR(50),reg_capital VARCHAR(15),setup_date CHAR(8),province VARCHAR(3),city VARCHAR(15),introduction VARCHAR(700),website VARCHAR(100),email VARCHAR(200),office VARCHAR(100),business_scope VARCHAR(1500),employees VARCHAR(10),main_business VARCHAR(500)",
                    "unique_cols": "",
                    "query_cols": "ts_code,exchange,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,business_scope,employees,main_business",
                    "get_func": get_stock_company
                },
            "stk_managers":
                {
                    "db_cols": "ts_code CHAR(9),ann_date CHAR(8),name VARCHAR(100),gender CHAR(1),lev VARCHAR(10),title VARCHAR(30),edu CHAR(2),national VARCHAR(10),birthday CHAR(8),begin_date VARCHAR(10),end_date VARCHAR(10),resume VARCHAR(1500)",
                    "unique_cols": "ts_code,ann_date,name,gender,lev,title,edu,national,birthday,begin_date,end_date",
                    "query_cols": "ts_code,ann_date,name,gender,lev,title,edu,national,birthday,begin_date,end_date,resume",
                    "get_func": get_stk_managers
                },
            "stock_basic_l_or_p":
                {
                    "db_cols": "ts_code CHAR(9) PRIMARY KEY,symbol CHAR(6) UNIQUE,name VARCHAR(20) UNIQUE,area VARCHAR(3),industry VARCHAR(5),fullname VARCHAR(50) UNIQUE,enname VARCHAR(100) UNIQUE,market VARCHAR(3),exchange VARCHAR(4),curr_type CHAR(3),list_status CHAR(1),list_date CHAR(8),is_hs CHAR(1)",
                    "unique_cols": "",
                    "query_cols": "ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,is_hs",
                    "get_func": get_stock_basic_l_or_p
                },
            "stk_rewards":
                {
                    "db_cols": "ts_code CHAR(9),ann_date CHAR(8),end_date CHAR(8),name VARCHAR(100),title VARCHAR(30),reward VARCHAR(15),hold_vol VARCHAR(15)",
                    "unique_cols": "ts_code,ann_date,end_date,name,title,reward,hold_vol",
                    "query_cols": "ts_code,ann_date,end_date,name,title,reward,hold_vol",
                    "get_func": get_stk_rewards
                },
            "stock_basic_d":
                {
                    "db_cols": "ts_code CHAR(9) PRIMARY KEY,symbol CHAR(6) UNIQUE,name VARCHAR(20) UNIQUE,fullname VARCHAR(50) UNIQUE,enname VARCHAR(100) UNIQUE,market VARCHAR(3),exchange VARCHAR(4),curr_type CHAR(3),list_status CHAR(1),list_date CHAR(8),delist_date CHAR(8)",
                    "unique_cols": "",
                    "query_cols": "ts_code,symbol,name,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date",
                    "get_func": get_stock_basic_d
                },
            "trade_cal":
                {
                    "db_cols": "exchange VARCHAR(4),cal_date CHAR(8),is_open CHAR(1),pretrade_date CHAR(8)",
                    "unique_cols": "exchange,cal_date",
                    "query_cols": "exchange,cal_date,is_open,pretrade_date",
                    "get_func": get_trade_cal
                },
            "namechange":
                {
                    "db_cols": "ts_code CHAR(9),name CHAR(20),start_date CHAR(8),end_date CHAR(8),ann_date CHAR(8),change_reason VARCHAR(20)",
                    "unique_cols": "ts_code,name,start_date,end_date",
                    "query_cols": "ts_code,name,start_date,end_date,ann_date,change_reason",
                    "get_func": get_namechange
                },
            "hs_const":
                {
                    "db_cols": "ts_code CHAR(9),hs_type CHAR(2),in_date CHAR(8),out_date CHAR(8),is_new CHAR(1)",
                    "unique_cols": "ts_code,hs_type,in_date,out_date,is_new",
                    "query_cols": "ts_code,hs_type,in_date,out_date,is_new",
                    "get_func": get_hs_const
                },
            "new_share":
                {
                    "db_cols": "ts_code CHAR(9) UNIQUE,sub_code CHAR(6),name VARCHAR(10),ipo_date CHAR(8),issue_date VARCHAR(8),amount VARCHAR(15),market_amount VARCHAR(15),price VARCHAR(10),pe VARCHAR(10),limit_amount VARCHAR(10),funds VARCHAR(15),ballot VARCHAR(10)",
                    "unique_cols": "",
                    "query_cols": "ts_code,sub_code,name,ipo_date,issue_date,amount,market_amount,price,pe,limit_amount,funds,ballot",
                    "get_func": get_new_share
                },
        },
    "stock_daily":
        {
            "basic":
                {
                    "db_cols": "ts_code CHAR(9),trade_date CHAR(8),open VARCHAR(10),high CHAR(10),low VARCHAR(10),close VARCHAR(10),pre_close VARCHAR(10),change_ VARCHAR(30),pct_chg VARCHAR(15),vol VARCHAR(20),amount VARCHAR(20),adj_factor VARCHAR(20),turnover_rate VARCHAR(20),turnover_rate_f VARCHAR(20),volume_ratio VARCHAR(20),pe VARCHAR(20),pe_ttm VARCHAR(20),pb VARCHAR(20),ps VARCHAR(20),ps_ttm VARCHAR(20),total_share VARCHAR(20),float_share VARCHAR(20),free_share VARCHAR(20),total_mv VARCHAR(20),circ_mv VARCHAR(20),buy_sm_vol VARCHAR(20),buy_sm_amount VARCHAR(20),sell_sm_vol VARCHAR(20),sell_sm_amount VARCHAR(20),buy_md_vol VARCHAR(20),buy_md_amount VARCHAR(20),sell_md_vol VARCHAR(20),sell_md_amount VARCHAR(20),buy_lg_vol VARCHAR(20),buy_lg_amount VARCHAR(20),sell_lg_vol VARCHAR(20),sell_lg_amount VARCHAR(20),buy_elg_vol VARCHAR(20),buy_elg_amount VARCHAR(20),sell_elg_vol VARCHAR(20),sell_elg_amount VARCHAR(20),net_mf_vol VARCHAR(20),net_mf_amount VARCHAR(20),up_limit VARCHAR(10),down_limit VARCHAR(10)",
                    "unique_cols": "ts_code,trade_date",
                    "query_cols": "ts_code,trade_date,open,high,low,close,pre_close,change_,pct_chg,vol,amount,adj_factor,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,total_share,float_share,free_share,total_mv,circ_mv,buy_sm_vol,buy_sm_amount,sell_sm_vol,sell_sm_amount,buy_md_vol,buy_md_amount,sell_md_vol,sell_md_amount,buy_lg_vol,buy_lg_amount,sell_lg_vol,sell_lg_amount,buy_elg_vol,buy_elg_amount,sell_elg_vol,sell_elg_amount,net_mf_vol,net_mf_amount,up_limit,down_limit"
                },
            "daily":
                {
                    "db_cols": "ts_code CHAR(9),trade_date CHAR(8),open VARCHAR(10),high CHAR(10),low VARCHAR(10),close VARCHAR(10),pre_close VARCHAR(10),change_ VARCHAR(30),pct_chg VARCHAR(15),vol VARCHAR(20),amount VARCHAR(20)",
                    "unique_cols": "ts_code,trade_date",
                    "query_cols": "ts_code,trade_date,open,high,low,close,pre_close,change_,pct_chg,vol,amount",
                    "get_func": get_daily
                },
            "adj_factor":
                {
                    "db_cols": "ts_code CHAR(9),trade_date CHAR(8),adj_factor VARCHAR(20)",
                    "unique_cols": "trade_date,ts_code",
                    "query_cols": "trade_date,ts_code,adj_factor",
                    "get_func": get_adj_factor
                },
            "daily_basic":
                {
                    "db_cols": "ts_code CHAR(9),trade_date CHAR(8),turnover_rate VARCHAR(20),turnover_rate_f VARCHAR(20),volume_ratio VARCHAR(20),pe VARCHAR(20),pe_ttm VARCHAR(20),pb VARCHAR(20),ps VARCHAR(20),ps_ttm VARCHAR(20),total_share VARCHAR(20),float_share VARCHAR(20),free_share VARCHAR(20),total_mv VARCHAR(20),circ_mv VARCHAR(20)",
                    "unique_cols": "ts_code,trade_date",
                    "query_cols": "ts_code,trade_date,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,total_share,float_share,free_share,total_mv,circ_mv",
                    "get_func": get_daily_basic
                },
            "moneyflow":
                {
                    "db_cols": "ts_code CHAR(9),trade_date CHAR(8),buy_sm_vol VARCHAR(20),buy_sm_amount VARCHAR(20),sell_sm_vol VARCHAR(20),sell_sm_amount VARCHAR(20),buy_md_vol VARCHAR(20),buy_md_amount VARCHAR(20),sell_md_vol VARCHAR(20),sell_md_amount VARCHAR(20),buy_lg_vol VARCHAR(20),buy_lg_amount VARCHAR(20),sell_lg_vol VARCHAR(20),sell_lg_amount VARCHAR(20),buy_elg_vol VARCHAR(20),buy_elg_amount VARCHAR(20),sell_elg_vol VARCHAR(20),sell_elg_amount VARCHAR(20),net_mf_vol VARCHAR(20),net_mf_amount VARCHAR(20)",
                    "unique_cols": "ts_code,trade_date",
                    "query_cols": "ts_code,trade_date,buy_sm_vol,buy_sm_amount,sell_sm_vol,sell_sm_amount,buy_md_vol,buy_md_amount,sell_md_vol,sell_md_amount,buy_lg_vol,buy_lg_amount,sell_lg_vol,sell_lg_amount,buy_elg_vol,buy_elg_amount,sell_elg_vol,sell_elg_amount,net_mf_vol,net_mf_amount",
                    "get_func": get_moneyflow
                },
            "stk_limit":
                {
                    "db_cols": "ts_code CHAR(9),trade_date CHAR(8),up_limit VARCHAR(10),down_limit VARCHAR(10)",
                    "unique_cols": "ts_code,trade_date",
                    "query_cols": "ts_code,trade_date,up_limit,down_limit",
                    "get_func": get_stk_limit
                },

        },

}

dropTableList = [
    "stock_basic_l_or_p",
    "stock_basic_d",
    "hs_const",
    "stock_company",
    "new_share",
]
db_names = list(dbs.keys())
