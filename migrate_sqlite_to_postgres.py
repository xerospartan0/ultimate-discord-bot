# Template migration: copy selected tables from sqlite to Postgres
import sqlite3, psycopg2, os

SQLITE_DB = os.path.join(os.getcwd(), 'data', 'economy.db')
PG_DSN = os.getenv('PG_DSN', 'dbname=botdb user=bot password=botpass host=postgres')

def migrate_balances():
    s_conn = sqlite3.connect(SQLITE_DB)
    s_cur = s_conn.cursor()
    s_cur.execute('CREATE TABLE IF NOT EXISTS balances(user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    s_cur.execute('SELECT user_id, balance FROM balances')
    rows = s_cur.fetchall()
    s_conn.close()

    p_conn = psycopg2.connect(PG_DSN)
    p_cur = p_conn.cursor()
    p_cur.execute('CREATE TABLE IF NOT EXISTS balances(user_id BIGINT PRIMARY KEY, balance INTEGER DEFAULT 0)')
    for uid, bal in rows:
        p_cur.execute('INSERT INTO balances(user_id, balance) VALUES(%s,%s) ON CONFLICT (user_id) DO UPDATE SET balance=EXCLUDED.balance', (uid, bal))
    p_conn.commit()
    p_conn.close()
    print('Migration complete.')

if __name__ == "__main__":
    migrate_balances()
