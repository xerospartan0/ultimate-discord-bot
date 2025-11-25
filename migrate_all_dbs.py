# Migrate common sqlite DBs (economy.db, levels.db, reminders.db, suggestions.db) to Postgres.
import os, sqlite3, psycopg2, glob, json, time
from utils.db import get_pg_conn

SQLITE_DIR = os.path.join(os.getcwd(), 'data')

def migrate_balances():
    sdb = os.path.join(SQLITE_DIR, 'economy.db')
    if not os.path.exists(sdb):
        print('economy.db not found')
        return
    s = sqlite3.connect(sdb); sc = s.cursor()
    sc.execute('CREATE TABLE IF NOT EXISTS balances(user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    sc.execute('SELECT user_id, balance FROM balances'); rows = sc.fetchall(); s.close()
    pg = get_pg_conn(); pc = pg.cursor()
    pc.execute('CREATE TABLE IF NOT EXISTS balances(user_id BIGINT PRIMARY KEY, balance INTEGER DEFAULT 0)')
    for uid, bal in rows:
        pc.execute('INSERT INTO balances(user_id, balance) VALUES(%s,%s) ON CONFLICT (user_id) DO UPDATE SET balance=EXCLUDED.balance', (uid, bal))
    pg.commit(); pc.close(); pg.close()
    print('balances migrated')

def migrate_generic(name):
    sdb = os.path.join(SQLITE_DIR, name)
    if not os.path.exists(sdb):
        print(name, 'not found')
        return
    s = sqlite3.connect(sdb); sc = s.cursor()
    # This script leaves content copying to a manual step per-table; it's a template.
    print('Please implement table-specific migrations for', name)

if __name__ == '__main__':
    migrate_balances()
    migrate_generic('levels.db')
    migrate_generic('reminders.db')
    migrate_generic('suggestions.db')
