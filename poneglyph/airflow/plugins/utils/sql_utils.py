from numpy import histogram_bin_edges
from pymysql import connect
import logging
import pymysql
from pymysql.cursors import DictCursor
from airflow import AirflowException

# from sqlalchemy import create_engine


class SqlConnection:
    @staticmethod
    def get_connection():
        try:
            connection = connect(
                # host="docker.for.win.localhost",
                host="127.0.0.1",
                port=3306,
                user="root",
                password="guntupalli",
                db="stocks_data",
                charset="utf8mb4",
                cursorclass=DictCursor,
            )
            connection.autocommit(True)
            return connection

        except pymysql.Error as e:
            logging.info("Cannot create Connection obj : ")
            raise AirflowException("Failed to connect to DB : ")

    # @staticmethod
    # def get_sql_engine():
    #     db_data = (
    #         "mysql+pymysql://"
    #         + "root"
    #         + ":"
    #         + "guntupalli"
    #         + "@"
    #         + "docker.for.win.localhost"
    #         + ":3306/"
    #         + "stocks_data"
    #         + "?charset=utf8mb4"
    #     )
    #     engine = create_engine(db_data)
    #     return engine
