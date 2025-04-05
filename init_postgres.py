import psycopg2
import os, time
import traceback


pg_host = os.environ.get('PG_HOST', 'postgres')
pg_port = os.environ.get('PG_PORT', 5432)
pg_db = os.environ.get('PG_DB', 'tfserving')
pg_user = os.environ.get('PG_USER', 'postgres')
pg_password = os.environ.get('PG_PASSWORD', 'postgres')

if __name__ == "__main__":
    print(" Init module: Initialize the postgres schemas.\n\n")
    print(" Init module starting...\n")
    time.sleep(5)
    try:
        conn = psycopg2.connect(
            dbname = pg_db,
            user = pg_user,
            password = pg_password,
            host = pg_host,
            port = pg_port
        )
        
        sql_init_statement = """
                CREATE TABLE IF NOT EXISTS object_counter (
                object_class VARCHAR(255),
                count bigint);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_object_class ON object_counter (object_class);
                """
        cursor = conn.cursor()
        cursor.execute(sql_init_statement)
        conn.commit()
        conn.close()
        print(" Init module successfully completed...\n")
    except Exception as e:
        print(traceback.format_exc())
        print(" Init module Failed...\n")