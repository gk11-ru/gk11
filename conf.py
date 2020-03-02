from libz.peewee import SqliteDatabase

DATA='./data'
URL='gk11.ru'
BIND='127.0.0.1'
SHOWMSGFROM='never' # always, newmsg, never
STREET='gk11.ru'

db = SqliteDatabase('%s/bb.db' % DATA)
userdb = SqliteDatabase('%s/user.db' % DATA)
