def _pager(pages,curr):
    if pages < 15:
        return range(1,pages+1)
    else:
        startp = [1,2,3,4]
        endp = [pages-3,pages-2,pages-1,pages]
        centerp = [curr-3,curr-2,curr-1,curr,curr+1,curr+2,curr+3]
        centerp = [x for x in centerp if x > 0 and x not in startp]
        centerp = [x for x in centerp if x > 0 and x not in endp]
        if centerp:
            out = startp
            if startp[-1]+1 != centerp[0]:
                out += [0]
            out += centerp
            if centerp[-1]+1 != endp[0]:
                out += [0]
            out += endp
            return out
        else:
            return startp + [0] + endp

def render_pager(total,curr,ea):
    pages = (total-1) // 100 + 1
    if pages < 2: return ''
    lst = _pager(pages,curr)
    out = '<ul class="pagination">'
    if curr > 1:
        out += '<li class="arrow"><a href="/l/%s/%s">&laquo;</a></li>' % (ea,curr-1)
    else:
        out += '<li class="arrow unavailable"><a href="">&laquo;</a></li>'
    for n in lst:
        if not n:
            out += '<li class="unavailable"><a href="">&hellip;</a></li>'
        elif n == curr:
            out += '<li class="current"><a href="/l/%s/%s">%s</a></li>' % (ea,n,n)
        else:
            out += '<li><a href="/l/%s/%s">%s</a></li>' % (ea,n,n)
    if curr == pages:
        out += '<li class="arrow unavailable"><a href="">&raquo;</a></li>'
    else:
        out += '<li class="arrow"><a href="/l/%s/%s">&raquo;</a></li>' % (ea,curr+1)
    out += "</ul>"
    return out
