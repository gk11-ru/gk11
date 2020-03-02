# -*- coding: utf-8 -*-

from libz.peewee import Model, TextField, CharField
import conf
from rssg import gen_rss, rss_carbon
from bbdata.dbj import hsh2, mydict
import libz.bottle as bottle

userdb = conf.userdb


class points(Model):
    uname = CharField(unique=True)
    uhash = CharField(unique=True)
    uaddr = CharField(index=True,default='')
    fields = TextField(default='')

    class Meta:
        database = userdb


def mkhash(uname,upass):
    return hsh2(uname.encode('utf-8') + upass.encode('utf-8'))


def save_user(uname, upass):
    if len(uname) < 1 or len(upass) < 1:
        return
    try:
        newuser = points.get(points.uname == uname)
    except:
        newuser = points()
    newhash = mkhash(uname,upass)
    newuser.uname = uname
    newuser.uhash = newhash
    newuser.save()
    return newuser.uhash

def check_auth(uhash):
    req = points.select().where(points.uhash == uhash)
    getuser = [x for x in req]
    if getuser:
        if getuser[0].uhash:
            au = mydict(getuser[0]._data)
            roots = open('%s/root.txt' % conf.DATA).read().decode('utf-8').splitlines()
            if au.uname in roots:
                au.update(root=True)
            return au
    return mydict()


def uweb(umod,rq,kuk):
    if umod == 'reguser':
        return mydict(html=bottle.template('userbb/reg.html',acc=rq.acc))
    elif umod == 'adduser':
        newhash = save_user(rq.uname, rq.upass)
        return mydict(html='login <b>%s</b>, password <b>%s</b><br>authstr: <b>%s</b><br><br><a href="/user/login">LOGIN</a>' % (rq.uname, rq.upass, newhash))
    elif umod == 'login':
        newhash = mkhash(rq.uname,rq.upass)
        return mydict(cookie={'uhash': newhash},redir=rq.redir or '/user/me')
    elif umod == 'logout':
        return mydict(cookie={'uhash': ''},redir='/user/me')
    elif umod == 'me':
        u = check_auth(rq.uhash or kuk.uhash)
        if u:
            return mydict(html=bottle.template('userbb/profile.html', u=u))
        else:
            return mydict(html=bottle.template('userbb/login.html', rq=rq))
