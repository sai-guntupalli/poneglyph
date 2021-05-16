from poneglyph.utils.config_parser import get_config
import  psycopg2
import pandas as pd


def get_postgres_connection():

    conn = None
    try:
        params = get_config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return conn






