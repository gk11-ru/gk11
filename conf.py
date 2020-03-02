from libz.peewee import SqliteDatabase

DATA='./data'
URL='none.gk11.ru'
BIND='127.0.0.1'
SHOWMSGFROM='never' # always, newmsg, never
STREET='none'

db = SqliteDatabase('%s/bb.db' % DATA)
userdb = SqliteDatabase('%s/user.db' % DATA)
