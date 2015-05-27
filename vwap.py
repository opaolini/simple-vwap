from __future__ import print_function, division
import requests
import StringIO
import decimal
import datetime
import time
import csv

# Reference points
SYMBOLS = ['bitfinexUSD']


def get_timestamp(day, month, year=2015, hour=8, minute=0, second=0):
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return int(time.mktime(dt.timetuple()))


def parse_csv(result):
    """
    Parsing csv from bitcoincharts.

    Using Decimal for fixed-point arithmetics
    """
    t = []
    f = StringIO.StringIO(result)
    try:
        reader = csv.reader(f)
        for row in reader:
            price = row[1]
            volume = row[2]
            timestamp = row[0]
            t.append([int(timestamp), decimal.Decimal(price), decimal.Decimal(volume)])
    finally:
        f.close()
    return t


def calc_vwap(t_array, tf=60 * 15):
    """
    Calculates VWAP from trades array.

    params:
    -------
    t_array: list, contains trade data
    tf: integer, timeframe to calculate vwap from defaults to 1 hour
    """
    end_timestamp = t_array[0][0] + tf  # Timestamp of first trade + 60*60 seconds (Default)
    pq = sum(t[1] * t[2] for t in t_array if t[0] < end_timestamp)
    q = sum(t[2] for t in t_array if t[0] < end_timestamp)
    return pq / q


def fetch_data(symbols, start):
    t_array = []
    for symbol in symbols:
        payload = {"symbol": symbol, "start": start}  # Params for Bitcoincharts
        r = requests.get('http://api.bitcoincharts.com/v1/trades.csv', params=payload)
        t_array += parse_csv(r.text)
    return t_array

start = get_timestamp(27, 5, hour=15, minute=25)  # Start Date: 27.05.2015 15:25
data = fetch_data(SYMBOLS, start)
vwap = calc_vwap(data, 60 * 10)  # 10 minute timewindow, effectively - 15:25-15:35
print("VWAP: %0.2f" % vwap)
