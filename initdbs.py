from bbdata.dbj import msg, db
db.create_tables([msg])

from userbb import points, userdb
userdb.create_table(points)