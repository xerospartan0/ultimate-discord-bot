# Database utilities: Postgres connector and migration helper for multiple sqlite DBs
import os, sqlite3, psycopg2, glob, json

def get_pg_conn():
    dsn = os.getenv('PG_DSN', 'dbname=botdb user=bot password=botpass host=postgres')
    return psycopg2.connect(dsn)

def migrate_table(sqlite_db, table_name, create_sql, select_sql, insert_sql, transform_row=None):
    # sqlite_db: path, create_sql: to ensure table exists in sqlite, select_sql: to fetch rows
    s = sqlite3.connect(sqlite_db); sc = s.cursor()
    sc.execute(create_sql); s.commit()
    sc.execute(select_sql); rows = sc.fetchall(); s.close()
    pg = get_pg_conn(); pc = pg.cursor()
    pc.execute(create_sql.replace('INTEGER PRIMARY KEY', 'BIGINT PRIMARY KEY') if 'CREATE TABLE' in create_sql else create_sql)
    for row in rows:
        vals = transform_row(row) if transform_row else row
        pc.execute(insert_sql, vals)
    pg.commit(); pc.close(); pg.close()
    print('Migrated', table_name)
