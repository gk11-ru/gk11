<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
%if get('rss'):
    <link rel="alternate" type="application/rss+xml" title="{{ea}}" href="/rss/{{ea}}">
%end
    <title>{{title}}</title>
    <link rel="stylesheet" href="/s/css/foundation.min.css" />
    <link rel="stylesheet" href="/s/css/font-awesome.min.css" />
    <link rel="icon" type="image/png" href="/s/favicon.png" />
%if get('reloadpage'):
    <meta http-equiv="refresh" content="30;URL={{get('reloadpage')}}">
%end


%if request.cookies.bg != 'no':
    <style>
        body {background: url(/s/varyag.jpg) no-repeat; background-size: cover; background-attachment: fixed; }
    </style>
%end
  </head>

