from datetime import timedelta
import logging

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from nsetools import Nse
import pymysql
import yfinance as yf

from datetime import date

from utils.sql_utils import SqlConnection


# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
with DAG(
    "download_stocks_data_dag",
    default_args=default_args,
    description="DAG for downloading stocks data",
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    tags=["download_stock_data"],
) as dag:

    conn = SqlConnection.get_connection()
    c = conn.cursor()
    # engine = SqlConnection.get_sql_engine()

    def download_stock_data_method(**kwargs):
        nse = Nse()

        stock_names_dict = nse.get_stock_codes()
        stock_names_list = list(stock_names_dict.keys())[1:4]

        stocks = []

        stocks = [
            download_price_history_for_stock(symbol=stock) for stock in stock_names_list
        ]

        failed_stocks = [i for i in stocks if i]

        logging.info("Failed Stocks : ")
        logging.info(failed_stocks)

        failed_again = []

        if len(failed_stocks) > 0:
            failed_again = [
                download_price_history_for_stock(symbol=stock)
                for stock in failed_stocks
            ]

        if len(failed_again) > 0:
            logging.info("Failed STOCKS after multiple tries : ")
            logging.info(failed_again)

    def get_create_table_stmt(symbol):
        table_name = symbol + "_history"
        stmt = f"""CREATE TABLE `{table_name}` ( Date DATE NOT NULL, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Adj_Close FLOAT, Volume INT, CONSTRAINT date_pk UNIQUE (Date));"""
        return stmt

    def download_price_history_for_stock(symbol):
        today_str = str(date.today())
        failed_stocks = None

        try:
            c.execute(
                f"""SELECT count(*) as CNT FROM information_schema.tables WHERE table_schema = 'stocks_data' AND table_name = '{symbol}_history'; """
            )
            res = c.fetchone()
            logging.info("|".join(res))
            if res["CNT"] == 0:
                logging.info(
                    f"History is not available for {symbol}, Downloading FULL history..."
                )

                create_table_stmt = get_create_table_stmt(symbol)

                logging.info(create_table_stmt)

                c.execute(create_table_stmt)

                full_data = yf.download(
                    tickers=symbol + ".NS", threads=True, period="max"
                )
                full_data.columns = full_data.columns.str.replace(" ", "_")

                full_data.to_sql(symbol + "_history", conn, if_exists="append")
            else:
                c.execute(f"""SELECT max(Date) as mdate FROM `{symbol}_history` ; """)
                last_stock_data_date = c.fetchone()["mdate"].replace(" 00:00:00", "")
                logging.info(
                    f"Downloading Incremental history for {symbol} from {last_stock_data_date}"
                )
                incremental_data = yf.download(
                    tickers=symbol + ".NS", start=last_stock_data_date, end=today_str
                )
                incremental_data.columns = incremental_data.columns.str.replace(
                    " ", "_"
                )
                incremental_data.to_sql(symbol + "_history", conn, if_exists="append")
            conn.commit()

        except pymysql.OperationalError as err:
            # failed_stocks = symbol
            pass

        except Exception as e:
            failed_stocks = symbol
            logging.info("Caught Exception : ", e)
            pass

        return failed_stocks

    t1 = PythonOperator(
        task_id="download_stock_data_task", python_callable=download_stock_data_method
    )

    t1
