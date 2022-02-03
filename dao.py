import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import config

db_file = str(Path(__file__).parent / config.db_file_name)

show_yes = 1
show_no = 0


def get_con_cur():
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    return con, cur


def create_table():
    con, cur = get_con_cur()
    cur.execute('''CREATE TABLE IF NOT EXISTS note (create_time timestamp PRIMARY KEY , note text,show INTEGER)''')
    con.commit()
    con.close()


create_table()


def add(note):
    con, cur = get_con_cur()
    cur.execute('''INSERT INTO note VALUES (?,?,?)''', (datetime.today(), note, show_yes))
    con.commit()
    con.close()


def get_all():
    con, cur = get_con_cur()
    rows = cur.execute("""SELECT note,create_time FROM note""")
    rows = list(rows)
    con.close()
    return rows


def get(begin_time=None, end_time=None):
    con, cur = get_con_cur()
    delta = timedelta(**config.show_time_delta)
    today = datetime.today()
    begin_time = begin_time or today - delta
    end_time = end_time or today
    rows = cur.execute("""SELECT note,create_time FROM note WHERE create_time BETWEEN ? and ? and show = ?""",
                       (begin_time, end_time, show_yes))
    rows = list(rows)
    con.close()
    return rows


def del_note(date):
    con, cur = get_con_cur()
    cur.execute('''UPDATE note set show = ? where create_time = ?''', (show_no, date))
    con.commit()
    con.close()
