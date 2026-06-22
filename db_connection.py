import pymysql
import pymysql.cursors
import time

def get_db_connection(retries=2, delay=0.5):
    """Return a new pymysql connection. Retries on transient errors."""
    last_exc = None
    for _ in range(retries):
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='thesis',
                cursorclass=pymysql.cursors.DictCursor,  # <-- dict cursor here
                autocommit=False
            )
            return conn
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    if last_exc:
        raise last_exc
