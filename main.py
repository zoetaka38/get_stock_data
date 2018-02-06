# -*- coding: utf-8 -*-

import logging
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
from datetime import datetime as dt
import pandas as pd
import jsm
from jholiday import holiday_name
from jholiday import is_holiday
import os, sys, csv
from retry import retry

from stem import Signal
from stem.control import Controller
import socks
import socket

import sys
sys.path.append('./brands')

def appendstockcsv(code, range_type, start_date, end_date, stockdf):
    q = jsm.Quotes()
    prices = q.get_historical_prices(code, range_type, start_date, end_date)
    for price in prices:
        stockdf = stockdf.append(pd.Series(price_to_csvl(price), index=['Date','Open','High','Low','Close','Volume', 'Adj Close']), ignore_index=True)
        stockdf = stockdf.drop_duplicates().sort_values(by=["Date"], ascending=False)
    return stockdf
def getstockcsv(code, range_type, start_date, end_date):
    q = jsm.Quotes()
    prices = q.get_historical_prices(code, range_type, start_date, end_date)
    stockdf = pd.DataFrame()
    for price in prices:
        stockdf = stockdf.append(pd.Series(price_to_csvl(price), index=['Date','Open','High','Low','Close','Volume', 'Adj Close']), ignore_index=True)
        stockdf = stockdf.drop_duplicates().sort_values(by=["Date"], ascending=False)
    return stockdf
def price_to_csvl(price):
    """株データをCSV形式に変換"""
    return [price.date.strftime('%Y-%m-%d'),
            price.open, price.high, price.low, 
            price.close, price.volume, price._adj_close]

SAVE_PATH = os.environ["SAVE_PATH"]
from brands import all_brands
args = {"skip":0,}
codes = []
for (i, (code, name, _)) in enumerate(all_brands[args["skip"]:]):
        codes.append(code)


# Tor
@retry(delay=0.1)
def init_tor_proxy():
    print("try init tor proxy")
    torip = socket.gethostbyname("tor_proxy")
    controller = Controller.from_port(address=torip, port=9051)
    return torip, controller

torip, controller = init_tor_proxy()

controller.authenticate(password=os.environ["TOR_PASSWORD"])
controller.signal(Signal.NEWNYM)
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, torip, 9050)
urllib.request.socket.socket = socks.socksocket

_type = os.environ["TIME_TYPE"]
i = 0

if _type == '1':
    print("start getting daily stock data")
    for (i, (code, name, _)) in enumerate(all_brands[args["skip"]:]):
        print('{} / {}'.format(i + 1, len(all_brands)), code, name,)
        file = os.path.join(SAVE_PATH, 'YH_JP_{}.csv'.format(code))
        # change ip address
        controller.signal(Signal.NEWNYM)
        # すでにデータを取得している場合
        if os.path.isfile(file):
            stockdf = pd.read_csv(file)
            # カラム名がDateとかでない場合
            if stockdf.columns[0] == 'Date':
                # ブランクデータではない場合（上場廃止企業など）
                if len(stockdf) != 0:
                    # CSV上にある最新の日付を取得する
                    tdatetime = datetime.datetime.strptime(max(stockdf.Date), '%Y-%m-%d')
                    start_date = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day)
                    # 関数実行日が土日祝の場合、最近の土日祝以外の日にする
                    end_date = datetime.date.today()
                    while is_holiday(end_date):
                        end_date = end_date - datetime.timedelta(days=1)
                    # すでにDB上にある最新日付と終了日が同じ場合=>処理対象外とする
                    if start_date == end_date:
                        print("do nothing because you already have ddata of code:%d" % (int(code)))
                    else:
                        # 開始日付と終了日が異なる場合=>関数の実行
                        # 関数実行時、開始日付はDB上に保存されている日付の次の日からにする
                        start_date = start_date + datetime.timedelta(days=1)
                        try:
                            stockdf = appendstockcsv(code, jsm.DAILY, start_date, end_date, stockdf)
                            stockdf = stockdf.ix[:,['Date','Open','High','Low','Close','Volume', 'Adj Close']]
                            stockdf.to_csv(file,index=False)
                            print("got ddata. code: %d" % (int(code)))
                        except Exception as e:
                            print('=== エラー内容 ===',)
                            print('type:' + str(type(e)),)
                            print('args:' + str(e.args),)
                            print('e itself:' + str(e),)
                # 上場廃止と思われるコード
                else:
                    pass
            # 中途半端にデータを取得してしまっている場合
            else:
                # change ip address
                controller.signal(Signal.NEWNYM)
                # 関数実行日が土日祝の場合、最近の土日祝以外の日にする
                start_date = datetime.date(1990,1,1)
                end_date = datetime.date.today()
                while is_holiday(end_date):
                    end_date = end_date - datetime.timedelta(days=1)
                try:
                    stockdf = getstockcsv(code, jsm.DAILY, start_date, end_date)
                    stockdf = stockdf.ix[:,['Date','Open','High','Low','Close','Volume', 'Adj Close']]
                    stockdf.to_csv(file,index=False)
                    print("got ddata. code: %d" % (int(code)))
                except Exception as e:
                    print('=== エラー内容 ===',)
                    print('type:' + str(type(e)),)
                    print('args:' + str(e.args),)
                    print('e itself:' + str(e),)
        # データを取得したことがない場合
        else:
            # change ip address
            controller.signal(Signal.NEWNYM)
            # 関数実行日が土日祝の場合、最近の土日祝以外の日にする
            start_date = datetime.date(1990,1,1)
            end_date = datetime.date.today()
            while is_holiday(end_date):
                end_date = end_date - datetime.timedelta(days=1)
            try:
                stockdf = getstockcsv(code, jsm.DAILY, start_date, end_date)
                stockdf = stockdf.ix[:,['Date','Open','High','Low','Close','Volume', 'Adj Close']]
                stockdf.to_csv(file,index=False)
                print("got ddata. code: %d" % (int(code)))
            except Exception as e:
                print('=== エラー内容 ===',)
                print('type:' + str(type(e)),)
                print('args:' + str(e.args),)
                print('e itself:' + str(e),)
elif _type == '2':
    for code in codes:
        # change ip address
        controller.signal(Signal.NEWNYM)
        g = GetStockData()
        g.GetHistoricalStockData(code, _type)
        print("got wdata. code: %d" % (int(code)))
elif _type == '3':
    for code in codes:
        # change ip address
        controller.signal(Signal.NEWNYM)
        g = GetStockData()
        g.GetHistoricalStockData(code, _type)
        print("got mdata. code: %d" % (int(code)))
else:
    for code in codes:
        print(code)
    print("do nothing. please enter 1 to 3 for _type")
