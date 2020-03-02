import PyRSS2Gen
import datetime
import bbdata.dbj as dbj
from bbdata.mydict import mydict
import wh

def gen_rss(ea,num):
    url = dbj.conf.URL
    msgs = dbj.get_pass(mydict(echo=ea,lim=num))
    items = [PyRSS2Gen.RSSItem(
        title=n.title,
        description=wh.rend(n.txt),
        link='http://%s/q/%s' % (url,n.mid),
        guid='http://%s/q/%s' % (url,n.mid),
        author=n.msgfrom,
        pubDate=datetime.datetime.fromtimestamp(n.date)
    ) for n in msgs ]
    rssout = PyRSS2Gen.RSS2(
        title=ea,
        link='http://%s/l/%s' % (url,ea),
        description='Echoarea: %s' % ea,
        lastBuildDate=datetime.datetime.now(),
        items=items
    )
    return rssout.to_xml('utf-8')

def rss_carbon(username):
    url = dbj.conf.URL
    msgs = dbj.msg.select().order_by(dbj.msg.accepted.desc()).where(dbj.msg.msgto == username).limit(50)
    items = [PyRSS2Gen.RSSItem(
        title=n.title + ' :' + n.echoarea,
        description=wh.rend(n.txt),
        link='http://%s/q/%s' % (url,n.mid),
        guid='http://%s/q/%s' % (url,n.mid),
        author=n.msgfrom,
        pubDate=datetime.datetime.fromtimestamp(n.date)
    ) for n in msgs ]
    rssout = PyRSS2Gen.RSS2(
        title='Messages for: %s' % username,
        link='http://%s/l/noprofilenow' % (url),
        description='CarbonArea: %s' % username,
        lastBuildDate=datetime.datetime.now(),
        items=items
    )
    return rssout.to_xml('utf-8')
