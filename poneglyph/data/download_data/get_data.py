from nsetools import Nse
import yfinance as yf
import logging
from datetime import date
from poneglyph.utils.db_utils import get_postgres_connection
import  psycopg2
from sqlalchemy import  create_engine


conn = get_postgres_connection()
c = conn.cursor()

engine = create_engine('postgresql://postgres:guntupalli@localhost:5432/stocks_data_db')

def get_data():
    nse = Nse()

    stock_names_dict = nse.get_stock_codes()
    stock_names_list = list(stock_names_dict.keys())[1:20]

    stocks = [
        download_price_history_for_stock(symbol=stock) for stock in stock_names_list if not stock[0].isdigit()
    ]

    # print(stocks)
    failed_stocks = [i for i in stocks if i]

    print("Failed Stocks : ")
    print(failed_stocks)

    failed_again = []

    if len(failed_stocks) > 0:
        failed_again = [
            download_price_history_for_stock(symbol=stock)
            for stock in failed_stocks
        ]

    if len(failed_again) > 0:
        print("Failed STOCKS after multiple tries : ")
        print(failed_again)


def get_create_table_stmt(symbol):
    table_name = symbol + "_history"
    stmt = f"""CREATE TABLE {table_name} ( Date DATE NOT NULL, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Adj_Close FLOAT, Volume INT, UNIQUE(Date));"""
    return stmt


def download_price_history_for_stock(symbol):
    today_str = str(date.today())
    failed_stocks = None

    try:
        c.execute(
            f"""SELECT count(*) as CNT FROM information_schema.tables WHERE table_schema = 'stocks_data' AND table_name = '{symbol}_history'; """
        )
        res = c.fetchone()
        if res[0] == 0:
            print(
                f"History is not available for {symbol}, Downloading FULL history..."
            )

            create_table_stmt = get_create_table_stmt(symbol)

            print(create_table_stmt)

            c.execute(create_table_stmt)

            full_data = yf.download(
                tickers=symbol + ".NS", threads=True, period="max"
            )
            full_data.columns = full_data.columns.str.replace(" ", "_")

            full_data.to_sql(symbol + "_history", engine, if_exists="append")
        else:
            c.execute(f"""SELECT max(Date) as mdate FROM {symbol}_history ; """)
            last_stock_data_date = c.fetchone()["mdate"].replace(" 00:00:00", "")
            print(
                f"Downloading Incremental history for {symbol} from {last_stock_data_date}"
            )
            incremental_data = yf.download(
                tickers=symbol + ".NS", start=last_stock_data_date, end=today_str
            )
            incremental_data.columns = incremental_data.columns.str.replace(
                " ", "_"
            )
            incremental_data.to_sql(symbol + "_history", engine, if_exists="append")
        conn.commit()

    except psycopg2.OperationalError as err:
        # failed_stocks = symbol
        print("Caught Exception err : ", err)
        pass

    except Exception as e:
        failed_stocks = symbol
        print("Caught Exception : ", e)
        pass

    return failed_stocks

